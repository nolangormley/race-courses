"""Find course maps, and the pages that hold them, in organizer HTML."""

import re
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import parse_qs, urldefrag, urljoin, urlsplit

from race_courses.models import SourceRef

FETCHABLE = frozenset({"gpx", "kml", "kmz", "mymaps"})
MYMAPS_KML = "https://www.google.com/maps/d/kml?mid={mid}&forcekml=1"

MYMAPS_HOST = re.compile(r"(^|\.)google\.[a-z.]+$")
MID_CHARS = re.compile(r"[\w-]+")
# "course", "route" or "map" as a word or a word start ("coursemap.pdf"), but not "maple" or "sitemap".
COURSE_WORDS = re.compile(r"(course|route|(?<!site)map)s?(?![a-z])", re.IGNORECASE)
MAX_LABEL_CHARS = 120
# No .svg: course maps are raster or PDF, while icons under a "Course" heading are usually SVG.
FILE_EXTENSION = re.compile(r"\.(gpx|kml|kmz|pdf|png|jpe?g|gif|webp|bmp|tiff?)(?=$|[?&#;])", re.IGNORECASE)
FILE_KINDS = {"gpx": "gpx", "kml": "kml", "kmz": "kmz", "pdf": "pdf"}
MEDIA_TYPE_KINDS = {
    "application/pdf": "pdf",
    "application/gpx+xml": "gpx",
    "application/vnd.google-earth.kml+xml": "kml",
    "application/vnd.google-earth.kmz": "kmz",
}
SRC_ATTRIBUTES = ("src", "data-src", "data-lazy-src")
HEADINGS = frozenset({"h1", "h2", "h3", "h4", "h5", "h6"})

# Each pattern is matched against "hostname/path" of a URL that is not a Google My Maps link.
HOST_KINDS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "googlemaps",
        re.compile(r"(^|\.)google\.[a-z.]+/maps($|[/?])|^maps\.app\.goo\.gl/|^goo\.gl/maps/", re.IGNORECASE),
    ),
    ("strava", re.compile(r"(^|\.)strava\.com/(routes|activities|segments)/\d", re.IGNORECASE)),
    ("ridewithgps", re.compile(r"(^|\.)ridewithgps\.com/(routes/|trips/|embeds)", re.IGNORECASE)),
    ("mapmyrun", re.compile(r"(^|\.)mapmy(run|ride|walk|hike|fitness)\.com/routes/", re.IGNORECASE)),
    ("garmin", re.compile(r"(^|\.)garmin\.com(/.*)?/(course|activity)/", re.IGNORECASE)),
    ("plotaroute", re.compile(r"(^|\.)plotaroute\.com/.*(route|embedmap)", re.IGNORECASE)),
    ("racemap", re.compile(r"(^|\.)racemap\.com/.", re.IGNORECASE)),
    ("arcgis", re.compile(r"(^|\.)arcgis\.com/(apps|experience|stories|home|sharing)/|^arcg\.is/.", re.IGNORECASE)),
    ("onthegomap", re.compile(r"(^|\.)onthegomap\.com/", re.IGNORECASE)),
    ("caltopo", re.compile(r"(^|\.)(caltopo|sartopo)\.com/.", re.IGNORECASE)),
    ("footpath", re.compile(r"(^|\.)footpathapp\.com/.", re.IGNORECASE)),
    ("osm", re.compile(r"(^|\.)openstreetmap\.org/relation/\d+/?$", re.IGNORECASE)),
)

RAW_MYMAPS_MID = re.compile(r"google\.[a-z.]+/maps/d/[^\s\"'<>]*?[?&]mid=([\w-]+)", re.IGNORECASE)
RAW_FILE_URL = re.compile(r"https?://[^\s\"'<>()\\]+?\.(?:gpx|kml|kmz)(?![\w.])", re.IGNORECASE)


def mymaps_mid(url: str) -> str | None:
    """The map id of a Google My Maps URL (embed, viewer, edit or kml export), or None."""
    parts = urlsplit(url)
    if not parts.hostname or not MYMAPS_HOST.search(parts.hostname) or not parts.path.startswith("/maps/d/"):
        return None
    mids = parse_qs(parts.query).get("mid", [])
    if mids and MID_CHARS.fullmatch(mids[0]):
        return mids[0]
    return None


def classify(url: str, label: str = "") -> str | None:
    """Name the kind of course source a URL points to, or None when it is not one."""
    try:
        parts = urlsplit(url)
    except ValueError:
        return None
    host = parts.hostname
    if parts.scheme not in {"http", "https"} or not host:
        return None
    if mymaps_mid(url) is not None:
        return "mymaps"
    located = f"{host}{parts.path or '/'}"
    for kind, pattern in HOST_KINDS:
        if pattern.search(located):
            return kind
    extension = FILE_EXTENSION.search(f"{parts.path}?{parts.query}")
    if extension is None:
        return None
    kind = FILE_KINDS.get(extension.group(1).lower(), "image")
    if kind not in {"pdf", "image"} or COURSE_WORDS.search(f"{parts.path}?{parts.query}"):
        return kind
    # A short label such as "Course map" counts; a caption-length alt text or link text does not.
    if len(label) <= MAX_LABEL_CHARS and COURSE_WORDS.search(label):
        return kind
    return None


def kind_for_content_type(content_type: str) -> str | None:
    """The kind of a fetched document judged by its media type, for links that have no file extension."""
    if content_type.startswith("image/"):
        return "image"
    return MEDIA_TYPE_KINDS.get(content_type)


def source_ref(url: str, found_on: str, label: str = "") -> SourceRef | None:
    """The SourceRef for one absolute URL, or None when the URL is not a course map."""
    try:
        url = urldefrag(url.strip()).url
    except ValueError:
        return None
    kind = classify(url, label)
    if kind is None:
        return None
    if kind == "mymaps":
        url = MYMAPS_KML.format(mid=mymaps_mid(url))
    return SourceRef(kind=kind, url=url, found_on=found_on, label=label.strip())


def absolute(page_url: str, href: str) -> str | None:
    try:
        return urldefrag(urljoin(page_url, href.strip())).url
    except ValueError:
        return None


@dataclass(frozen=True)
class Candidate:
    """A URL found in the page, the text that labels it and the heading of the section it sits in."""

    url: str
    label: str
    section: str
    origin: str


def squash(text: str) -> str:
    return " ".join(text.split())


class SourceCollector(HTMLParser):
    """Collect link, embed and image URLs in document order."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.candidates: list[Candidate] = []
        self.open_href: str | None = None
        self.open_text: list[str] = []
        self.heading_text: list[str] | None = None
        self.section = ""

    def add(self, url: str, label: str, origin: str) -> None:
        self.candidates.append(Candidate(url, squash(label), self.section, origin))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {name: value for name, value in attrs if value is not None}
        if tag in HEADINGS:
            self.heading_text = []
        elif tag == "a":
            self.close_link()
            if "href" in attributes:
                self.open_href = attributes["href"]
        elif tag in {"iframe", "embed"}:
            for name in SRC_ATTRIBUTES:
                if name in attributes:
                    self.add(attributes[name], "", "embed")
        elif tag == "object" and "data" in attributes:
            self.add(attributes["data"], "", "embed")
        elif tag == "img":
            alt = attributes.get("alt", "")
            if self.open_href is not None:
                self.open_text.append(alt)
            for name in SRC_ATTRIBUTES:
                if name in attributes:
                    self.add(attributes[name], alt, "image")

    def handle_data(self, data: str) -> None:
        if self.open_href is not None:
            self.open_text.append(data)
        if self.heading_text is not None:
            self.heading_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a":
            self.close_link()
        elif tag in HEADINGS and self.heading_text is not None:
            heading = squash(" ".join(self.heading_text))
            # Only a heading that names a course, route or map starts a section that labels its files.
            self.section = heading if COURSE_WORDS.search(heading) else ""
            self.heading_text = None

    def close_link(self) -> None:
        if self.open_href is not None:
            self.add(self.open_href, " ".join(self.open_text), "link")
        self.open_href = None
        self.open_text = []


def collect(html: str) -> SourceCollector:
    collector = SourceCollector()
    collector.feed(html)
    collector.close()
    return collector


def scan_raw(html: str) -> list[str]:
    """URLs that only appear inside scripts or JSON blobs, where the tag parser cannot see them."""
    text = html.replace("\\/", "/").replace("\\u0026", "&").replace("&amp;", "&")
    urls = [MYMAPS_KML.format(mid=mid) for mid in RAW_MYMAPS_MID.findall(text)]
    urls.extend(RAW_FILE_URL.findall(text))
    return urls


def find_sources(html: str, page_url: str) -> list[SourceRef]:
    """Every course file, map embed and map link on a page, in document order, deduplicated by URL."""
    candidates = collect(html).candidates
    candidates.extend(Candidate(url, "", "", "script") for url in scan_raw(html))
    found: dict[str, SourceRef] = {}
    for candidate in candidates:
        url = absolute(page_url, candidate.url)
        if url is None:
            continue
        ref = source_ref(url, page_url, candidate.label)
        if ref is None and candidate.section:
            ref = source_ref(url, page_url, candidate.section)
        if ref is None or ref.url in found or (candidate.origin == "image" and ref.kind != "image"):
            continue
        found[ref.url] = ref
    return list(found.values())


def site_name(url: str) -> str:
    return (urlsplit(url).hostname or "").removeprefix("www.")


def find_course_links(html: str, page_url: str, limit: int = 5) -> list[str]:
    """Same-site page links that mention course, route or map; path matches rank above text matches."""
    site = site_name(page_url)
    self_url = (absolute(page_url, "") or page_url).rstrip("/")
    path_matches: list[str] = []
    text_matches: list[str] = []
    seen: set[str] = set()
    for candidate in collect(html).candidates:
        if candidate.origin != "link":
            continue
        url = absolute(page_url, candidate.url)
        if url is None or url in seen or url.rstrip("/") == self_url:
            continue
        parts = urlsplit(url)
        if parts.scheme not in {"http", "https"} or site_name(url) != site or FILE_EXTENSION.search(parts.path):
            continue
        seen.add(url)
        if COURSE_WORDS.search(f"{parts.path}?{parts.query}"):
            path_matches.append(url)
        elif COURSE_WORDS.search(candidate.label):
            text_matches.append(url)
    return (path_matches + text_matches)[:limit]
