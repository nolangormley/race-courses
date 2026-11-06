"""Parse downloaded GPX, KML and KMZ files into Geometry. All input is untrusted."""

import io
import re
import zipfile
import zlib
from xml.etree.ElementTree import Element, ParseError

from defusedxml import DefusedXmlException
from defusedxml.ElementTree import fromstring

from race_courses.models import Geometry, Line, Marker, Point

MAX_KMZ_ENTRIES = 200
MAX_KMZ_BYTES = 50_000_000
SNIFF_BYTES = 4096
ZIP_ERRORS = (zipfile.BadZipFile, zipfile.LargeZipFile, RuntimeError, NotImplementedError, EOFError, zlib.error)


def read_source(data: bytes) -> Geometry:
    """Parse a downloaded course file; the format is sniffed from the content, not the name."""
    head = data[:SNIFF_BYTES]
    if head.startswith(b"PK\x03\x04"):
        return read_kmz(data)
    if b"<gpx" in head:
        return read_gpx(data)
    if b"<kml" in head:
        return read_kml(data)
    raise ValueError("not a GPX, KML or KMZ file")


def parse_xml(data: bytes) -> Element:
    try:
        root: Element = fromstring(data)
    except (ParseError, DefusedXmlException, ValueError) as exc:
        raise ValueError(f"malformed XML: {exc}") from exc
    return root


def local_name(element: Element) -> str:
    return element.tag.rsplit("}", 1)[-1]


def children(element: Element, name: str) -> list[Element]:
    return [child for child in element if local_name(child) == name]


def child_text(element: Element, name: str) -> str:
    for child in element:
        if local_name(child) == name:
            return (child.text or "").strip()
    return ""


def make_point(lat: float, lon: float, ele: float | None) -> Point:
    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        raise ValueError(f"coordinates out of range: {lat}, {lon}")
    return Point(lat=lat, lon=lon, ele=ele)


def gpx_point(element: Element) -> Point:
    lat_text = element.get("lat")
    lon_text = element.get("lon")
    if lat_text is None or lon_text is None:
        raise ValueError(f"<{local_name(element)}> without lat and lon")
    ele_text = child_text(element, "ele")
    try:
        lat = float(lat_text)
        lon = float(lon_text)
        ele = float(ele_text) if ele_text else None
    except ValueError as exc:
        raise ValueError(f"bad <{local_name(element)}> coordinates") from exc
    return make_point(lat, lon, ele)


def read_gpx(data: bytes) -> Geometry:
    """One Line per trkseg (named after its trk) and per rte, one Marker per wpt. GPX 1.0 and 1.1."""
    root = parse_xml(data)
    if local_name(root) != "gpx":
        raise ValueError("root element is not <gpx>")
    lines: list[Line] = []
    for track in children(root, "trk"):
        name = child_text(track, "name")
        for segment in children(track, "trkseg"):
            points = tuple(gpx_point(point) for point in children(segment, "trkpt"))
            if points:
                lines.append(Line(name, points))
    for route in children(root, "rte"):
        points = tuple(gpx_point(point) for point in children(route, "rtept"))
        if points:
            lines.append(Line(child_text(route, "name"), points))
    markers = tuple(Marker(child_text(waypoint, "name"), gpx_point(waypoint)) for waypoint in children(root, "wpt"))
    return Geometry(lines=tuple(lines), markers=markers)


def kml_tuple(token: str, separator: str | None) -> Point:
    """One "lon,lat[,alt]" (coordinates) or "lon lat [alt]" (gx:coord) tuple. The altitude is dropped."""
    parts = token.split(separator)
    if len(parts) not in {2, 3}:
        raise ValueError(f"bad coordinate tuple: {token!r}")
    try:
        lon = float(parts[0])
        lat = float(parts[1])
    except ValueError as exc:
        raise ValueError(f"bad coordinate tuple: {token!r}") from exc
    return make_point(lat, lon, None)


def kml_coordinates(text: str) -> tuple[Point, ...]:
    """Parse a <coordinates> body. Some writers put a space after each comma; that is tolerated."""
    normalized = re.sub(r",\s+", ",", text.strip())
    return tuple(kml_tuple(token, ",") for token in normalized.split())


def placemark_name(placemark: Element, parents: dict[Element, Element]) -> str:
    """A placemark's own name, else the name of the nearest Folder above it."""
    name = child_text(placemark, "name")
    ancestor = parents.get(placemark)
    while not name and ancestor is not None:
        if local_name(ancestor) == "Folder":
            name = child_text(ancestor, "name")
        ancestor = parents.get(ancestor)
    return name


def read_kml(data: bytes) -> Geometry:
    """Lines from LineStrings and gx:Tracks, markers from Points. Polygons and altitudes are dropped."""
    root = parse_xml(data)
    parents = {child: parent for parent in root.iter() for child in parent}
    lines: list[Line] = []
    markers: list[Marker] = []
    for placemark in root.iter():
        if local_name(placemark) != "Placemark":
            continue
        name = placemark_name(placemark, parents)
        for geometry in placemark.iter():
            kind = local_name(geometry)
            if kind == "LineString":
                points = kml_coordinates(child_text(geometry, "coordinates"))
                if points:
                    lines.append(Line(name, points))
            elif kind == "Track":
                coords = [coord.text for coord in children(geometry, "coord") if coord.text and coord.text.strip()]
                points = tuple(kml_tuple(coord, None) for coord in coords)
                if points:
                    lines.append(Line(name, points))
            elif kind == "Point":
                points = kml_coordinates(child_text(geometry, "coordinates"))
                if points:
                    markers.append(Marker(name, points[0]))
    return Geometry(lines=tuple(lines), markers=tuple(markers))


def read_kmz(data: bytes) -> Geometry:
    """Parse doc.kml, else the first .kml entry. Refuse archives over the entry and size limits."""
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            entries = archive.infolist()
            if len(entries) > MAX_KMZ_ENTRIES:
                raise ValueError(f"KMZ has more than {MAX_KMZ_ENTRIES} entries")
            if sum(entry.file_size for entry in entries) > MAX_KMZ_BYTES:
                raise ValueError(f"KMZ unpacks to more than {MAX_KMZ_BYTES} bytes")
            names = [entry.filename for entry in entries]
            kml_names = [name for name in names if name.lower().endswith(".kml")]
            if not kml_names:
                raise ValueError("KMZ has no .kml entry")
            chosen = "doc.kml" if "doc.kml" in names else kml_names[0]
            with archive.open(chosen) as entry:
                content = entry.read(MAX_KMZ_BYTES + 1)
    except ZIP_ERRORS as exc:
        raise ValueError(f"bad KMZ archive: {exc}") from exc
    if len(content) > MAX_KMZ_BYTES:
        raise ValueError("KMZ entry is larger than its header declares")
    return read_kml(content)
