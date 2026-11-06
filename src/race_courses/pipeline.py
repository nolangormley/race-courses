"""Crawl each race: find its course maps, build one GPX per event, and keep the index entries."""

import hashlib
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import httpx

from race_courses import discover, geometry, osm, publish, readers, validate
from race_courses.catalog import Event, Race
from race_courses.elevation import Elevation, gain_loss
from race_courses.fetch import FetchError, Fetcher, Page
from race_courses.models import Course, SourceRef

PIPELINE_VERSION = 2
MAX_FOUND_PAGES = 3
READABLE = discover.FETCHABLE | {"manual", "file", "osm"}
FILE_KEYS = (
    "file", "source", "retrieved", "length_m", "length_error_pct", "ascent_m", "descent_m",
    "method", "oriented_by", "geometry_sha256", "pipeline",
)


@dataclass(frozen=True)
class Context:
    fetcher: Fetcher
    elevation: Elevation
    overpass: Callable[[str], bytes]
    root: Path
    previous: dict[tuple[str, str], dict]
    day: date
    reuse: bool = True


@dataclass(frozen=True)
class Candidate:
    ref: SourceRef
    course: Course
    verdict: validate.Verdict


class RaceReader:
    """Fetch each page and file of one race only once."""

    def __init__(self, race: Race, context: Context):
        self.race = race
        self.fetcher = context.fetcher
        self.overpass = context.overpass
        self.root = context.root
        self.pages: dict[str, Page] = {}
        self.blobs: dict[str, bytes] = {}
        self.failures: dict[str, str] = {}

    def page(self, url: str) -> Page | None:
        if url not in self.pages and url not in self.failures:
            try:
                self.pages[url] = self.fetcher.get(url)
            except FetchError as error:
                self.failures[url] = str(error)
        return self.pages.get(url)

    def blob(self, ref: SourceRef) -> bytes | None:
        if ref.kind == "manual":
            return (self.root / ref.url).read_bytes()
        if ref.url not in self.blobs and ref.url not in self.failures:
            try:
                if ref.kind == "osm":
                    self.blobs[ref.url] = self.overpass(osm.relation_query(ref.url))
                else:
                    self.blobs[ref.url] = self.fetcher.get(ref.url).body
            except (FetchError, httpx.HTTPError) as error:
                self.failures[ref.url] = str(error)
        return self.blobs.get(ref.url)

    def found_pages(self) -> list[str]:
        """The homepage and the course pages that it links to."""
        home = self.page(self.race.website)
        if home is None:
            return []
        links = discover.find_course_links(home.text, home.url, limit=MAX_FOUND_PAGES)
        return [self.race.website, *links]

    def sources(self, urls: list[str]) -> list[SourceRef]:
        refs: dict[str, SourceRef] = {}
        for url in urls:
            page = self.page(url)
            if page is None:
                continue
            # A course link without a file extension can lead straight to the map file.
            kind = discover.kind_for_content_type(page.content_type)
            if kind is not None:
                self.blobs.setdefault(page.url, page.body)
                refs.setdefault(page.url, SourceRef(kind=kind, url=page.url, found_on=url))
                continue
            for ref in discover.find_sources(page.text, page.url):
                refs.setdefault(ref.url, ref)
        return list(refs.values())


def crawl(races: list[Race], context: Context, log: Callable[[str], None] = print) -> list[dict]:
    entries = []
    for position, race in enumerate(races, start=1):
        reader = RaceReader(race, context)
        for event in race.events:
            entry = crawl_event(race, event, reader, context)
            log(f"[{position}/{len(races)}] {race.slug} {event.slug}: {entry['status']} - {entry['detail']}")
            entries.append(entry)
    return entries


def crawl_event(race: Race, event: Event, reader: RaceReader, context: Context) -> dict:
    listed = [url for url in (event.course_url, race.course_url) if url][:1]
    refs = explicit_refs(event) + reader.sources(listed)
    if not any(ref.kind in READABLE for ref in refs):
        known = {ref.url for ref in refs}
        refs += [ref for ref in reader.sources(reader.found_pages()) if ref.url not in known]
    base = base_entry(race, event, listed[0] if listed and listed[0] in reader.pages else race.website)
    candidates, problems = read_candidates(event, refs, reader)
    best = min(
        candidates,
        key=lambda candidate: (validate.RANK[candidate.verdict.status], abs(candidate.verdict.length_error_pct)),
        default=None,
    )
    previous = context.previous.get((race.slug, event.slug))
    if best is not None and best.verdict.status != "reject":
        try:
            return published_entry(race, event, base, best, previous, context)
        except (httpx.HTTPError, ValueError) as error:
            return keep_file({**base, "status": "error", "detail": f"elevation lookup failed: {error}"}, previous)
    return keep_file(missing_entry(base, best, refs, problems, reader), previous)


def explicit_refs(event: Event) -> list[SourceRef]:
    if event.source is None:
        return []
    if event.source.startswith("manual/"):
        return [SourceRef(kind="manual", url=event.source, found_on="races.yaml", label="hand-traced")]
    ref = discover.source_ref(event.source, found_on="races.yaml")
    return [ref or SourceRef(kind="file", url=event.source, found_on="races.yaml")]


def read_candidates(event: Event, refs: list[SourceRef], reader: RaceReader) -> tuple[list[Candidate], list[str]]:
    candidates, problems = [], []
    for ref in refs:
        if ref.kind not in READABLE:
            continue
        data = reader.blob(ref)
        if data is None:
            problems.append(reader.failures[ref.url])
            continue
        try:
            shape = osm.read_relation(data) if ref.kind == "osm" else readers.read_source(data)
        except ValueError as error:
            problems.append(f"cannot read {ref.url}: {error}")
            continue
        course = geometry.assemble(shape, event.distance_m)
        if course is None:
            problems.append(f"no line near {event.distance_m / 1000:.2f} km in {ref.url}")
            continue
        candidates.append(Candidate(ref, course, validate.check(course, event.distance_m)))
    return candidates, problems


def base_entry(race: Race, event: Event, page: str) -> dict:
    return {
        "race": race.slug,
        "event": event.slug,
        "name": race.name,
        "event_name": event.name,
        "city": race.city,
        "state": race.state,
        "month": race.month,
        "distance_m": event.distance_m,
        "finishers": event.finishers,
        "finishers_year": event.finishers_year,
        "page": page,
    }


def published_entry(
    race: Race, event: Event, base: dict, best: Candidate, previous: dict | None, context: Context
) -> dict:
    coordinates = "".join(f"{point.lat:.6f},{point.lon:.6f};" for point in best.course.points)
    digest = hashlib.sha256(coordinates.encode()).hexdigest()
    path = Path("courses") / race.state.lower() / race.slug / f"{event.slug}.gpx"
    entry = {
        **base,
        "status": best.verdict.status,
        "detail": "; ".join(best.verdict.notes) or f"{best.ref.kind} map",
        "file": path.as_posix(),
        "source": {"kind": best.ref.kind, "url": best.ref.url, "page": best.ref.found_on},
        "length_m": round(best.course.length_m, 1),
        "length_error_pct": round(best.verdict.length_error_pct, 2),
        "method": best.course.method,
        "oriented_by": best.course.oriented_by,
        "geometry_sha256": digest,
        "pipeline": PIPELINE_VERSION,
    }
    unchanged = (
        context.reuse
        and previous is not None
        and previous.get("geometry_sha256") == digest
        and previous.get("pipeline") == PIPELINE_VERSION
        and previous.get("file") == entry["file"]
        and (context.root / path).exists()
    )
    if unchanged:
        return {**entry, **{key: previous[key] for key in ("retrieved", "ascent_m", "descent_m")}}
    points = context.elevation.profile(geometry.resample(best.course.points))
    ascent, descent = gain_loss(points)
    title = f"{race.name} – {event.name}"
    if best.ref.kind == "manual":
        description = f"Hand-traced course ({best.ref.url})."
    else:
        description = f"Course line from the organizer's map at {best.ref.url}, read {context.day.isoformat()}."
    description += (
        " Elevation from USGS 3DEP; bridges and tunnels levelled with OpenStreetMap data"
        " (© OpenStreetMap contributors)."
    )
    target = context.root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(publish.gpx_bytes(points, title, description, base["page"], context.day))
    return {**entry, "retrieved": context.day.isoformat(), "ascent_m": round(ascent, 1), "descent_m": round(descent, 1)}


def missing_entry(
    base: dict, best: Candidate | None, refs: list[SourceRef], problems: list[str], reader: RaceReader
) -> dict:
    if best is not None:
        return {**base, "status": "reject", "detail": "; ".join(best.verdict.notes)}
    readable = [ref for ref in refs if ref.kind in READABLE]
    if readable:
        unread = all(ref.url in reader.failures for ref in readable)
        return {**base, "status": "error" if unread else "no-match", "detail": "; ".join(problems)}
    kinds = sorted({ref.kind for ref in refs})
    if kinds:
        return {**base, "status": "unsupported", "detail": "only " + ", ".join(kinds), "found": kinds}
    if not reader.pages:
        return {**base, "status": "error", "detail": "; ".join(reader.failures.values())}
    return {**base, "status": "no-source", "detail": "no course map on " + ", ".join(sorted(reader.pages))}


def keep_file(entry: dict, previous: dict | None) -> dict:
    """Keep the earlier course file when the latest crawl could not confirm it."""
    confirmed = entry["status"] in ("ok", "warn")
    if confirmed or previous is None or not previous.get("file") or previous.get("pipeline") != PIPELINE_VERSION:
        return entry
    kept = {key: previous[key] for key in FILE_KEYS if key in previous}
    detail = f"{entry['detail']} (kept the course read {previous['retrieved']})"
    return {**entry, **kept, "status": "stale", "detail": detail}
