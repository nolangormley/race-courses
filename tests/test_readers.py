"""Tests for the GPX, KML and KMZ readers on messy and hostile input."""

import io
import zipfile
from pathlib import Path

import pytest

from race_courses.models import Line, Marker, Point
from race_courses.readers import MAX_KMZ_BYTES, MAX_KMZ_ENTRIES, read_gpx, read_kml, read_kmz, read_source

FIXTURES = Path(__file__).parent / "fixtures" / "sources"


def fixture(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


def make_kmz(entries: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in entries.items():
            archive.writestr(name, content)
    return buffer.getvalue()


def test_gpx_11_tracks_routes_and_waypoints() -> None:
    geometry = read_gpx(fixture("course.gpx"))
    assert [(line.name, len(line.points)) for line in geometry.lines] == [
        ("Marathon", 3),
        ("Marathon", 2),
        ("", 2),
        ("Lead vehicle route", 2),
    ]
    assert geometry.lines[0].points[0] == Point(lat=40.4406, lon=-79.9959, ele=230.5)
    assert geometry.lines[1].points[0] == Point(lat=40.4412, lon=-79.9945, ele=None)
    assert geometry.lines[3].points[1] == Point(lat=40.4410, lon=-79.9950, ele=None)
    assert geometry.markers == (
        Marker("Start", Point(40.4406, -79.9959, 230.5)),
        Marker("Mile 1", Point(40.4420, -79.9900, None)),
    )


def test_gpx_10_is_read_the_same_way() -> None:
    geometry = read_gpx(fixture("course10.gpx"))
    assert [(line.name, len(line.points)) for line in geometry.lines] == [("10K", 2), ("Course", 2)]
    assert geometry.lines[1].points == (Point(33.7490, -84.3880, 320.0), Point(33.7500, -84.3870, None))
    assert geometry.markers == (Marker("Peachtree start", Point(33.7490, -84.3880)),)


@pytest.mark.parametrize(
    "body",
    [
        '<gpx><trk><trkseg><trkpt lon="-80"/></trkseg></trk></gpx>',
        '<gpx><wpt lat="north" lon="-80"/></gpx>',
        '<gpx><wpt lat="91" lon="-80"/></gpx>',
        '<gpx><wpt lat="40" lon="-181"/></gpx>',
        '<gpx><wpt lat="40" lon="-80"><ele>high</ele></wpt></gpx>',
        "<kml><Document/></kml>",
        "<gpx><trk>",
        "",
    ],
)
def test_gpx_rejects_bad_input(body: str) -> None:
    with pytest.raises(ValueError):
        read_gpx(body.encode())


def test_kml_22_folders_multigeometry_track_points_and_polygons() -> None:
    geometry = read_kml(fixture("course.kml"))
    assert [(line.name, len(line.points)) for line in geometry.lines] == [
        ("Course", 3),
        ("Relay legs", 2),
        ("Relay legs", 2),
        ("Recorded run", 2),
    ]
    assert geometry.lines[0].points[0] == Point(lat=40.4406, lon=-79.9959, ele=None)
    assert geometry.lines[3].points == (Point(40.4406, -79.9959), Point(40.4410, -79.9950))
    assert geometry.markers == (
        Marker("Start", Point(40.4406, -79.9959)),
        Marker("Landmarks", Point(40.4410, -79.9950)),
    )


def test_kml_21_with_spaces_after_commas() -> None:
    geometry = read_kml(fixture("course21.kml"))
    assert geometry.lines == (
        Line("Half Marathon", (Point(44.977, -93.265), Point(44.980, -93.260), Point(44.985, -93.255))),
    )
    assert geometry.markers == (Marker("Finish", Point(44.985, -93.255)),)


def test_kml_without_namespace_or_folder() -> None:
    body = b"<kml><Placemark><LineString><coordinates>-80,40 -80.1,40.1</coordinates></LineString></Placemark></kml>"
    assert read_kml(body).lines == (Line("", (Point(40.0, -80.0), Point(40.1, -80.1))),)


@pytest.mark.parametrize("coordinates", ["-80,40,1,2", "-80", "west,40", "-80,95", "-200,40"])
def test_kml_rejects_bad_coordinates(coordinates: str) -> None:
    body = f"<kml><Placemark><LineString><coordinates>{coordinates}</coordinates></LineString></Placemark></kml>"
    with pytest.raises(ValueError):
        read_kml(body.encode())


def test_kml_rejects_malformed_xml() -> None:
    with pytest.raises(ValueError):
        read_kml(b"<kml><Placemark>")


def test_kmz_reads_doc_kml_first() -> None:
    other = b"<kml><Placemark><Point><coordinates>0,0</coordinates></Point></Placemark></kml>"
    data = make_kmz({"a-other.kml": other, "doc.kml": fixture("course21.kml"), "images/icon.png": b"\x89PNG"})
    assert [line.name for line in read_kmz(data).lines] == ["Half Marathon"]


def test_kmz_falls_back_to_the_first_kml_entry() -> None:
    data = make_kmz({"readme.txt": b"hi", "Course.KML": fixture("course21.kml")})
    assert [line.name for line in read_kmz(data).lines] == ["Half Marathon"]


def test_kmz_rejects_archives_without_kml() -> None:
    with pytest.raises(ValueError, match=r"no \.kml"):
        read_kmz(make_kmz({"readme.txt": b"hi"}))


def test_kmz_rejects_too_many_entries() -> None:
    entries = {f"file{ii}.txt": b"x" for ii in range(MAX_KMZ_ENTRIES)}
    entries["doc.kml"] = fixture("course21.kml")
    with pytest.raises(ValueError, match="entries"):
        read_kmz(make_kmz(entries))


def test_kmz_rejects_oversized_contents() -> None:
    data = make_kmz({"doc.kml": fixture("course21.kml"), "big.bin": b"\0" * (MAX_KMZ_BYTES + 1)})
    with pytest.raises(ValueError, match="unpacks"):
        read_kmz(data)


def test_kmz_rejects_non_zip_data() -> None:
    with pytest.raises(ValueError):
        read_kmz(b"PK\x03\x04 not really a zip")


def test_read_source_sniffs_each_format() -> None:
    assert read_source(fixture("course.gpx")).markers[0].name == "Start"
    assert read_source(fixture("course.kml")).markers[0].name == "Start"
    assert read_source(make_kmz({"doc.kml": fixture("course21.kml")})).markers[0].name == "Finish"
    assert read_source(b"\xef\xbb\xbf" + fixture("course21.kml")).markers[0].name == "Finish"


@pytest.mark.parametrize("data", [b"", b"<html><body>Not found</body></html>", b"%PDF-1.4", b"PK\x03\x04garbage"])
def test_read_source_rejects_other_content(data: bytes) -> None:
    with pytest.raises(ValueError):
        read_source(data)


def test_entity_expansion_is_refused() -> None:
    bomb = (
        b'<?xml version="1.0"?><!DOCTYPE lolz [<!ENTITY lol "lol"><!ENTITY lol2 "&lol;&lol;&lol;">]>'
        b'<gpx><wpt lat="1" lon="1"><name>&lol2;</name></wpt></gpx>'
    )
    with pytest.raises(ValueError):
        read_gpx(bomb)
