import json
from dataclasses import replace
from datetime import date

from race_courses import pipeline
from race_courses.catalog import Event, Race
from race_courses.fetch import Blocked

from tests.fakes import METERS_PER_DEGREE, FakeElevation, FakeFetcher, coordinates, html, kml

DAY = date(2026, 11, 5)
COURSE_PAGE = "https://race.example/course"
MY_MAPS_KML = "https://www.google.com/maps/d/kml?mid=ABC123&forcekml=1"
MARATHON = Event("marathon", "Marathon", 42195.0, 5000, 2025, "https://race.example/results")
HALF = Event("half-marathon", "Half Marathon", 21097.0, 9000, 2025, "https://race.example/results")
RACE = Race(
    "example-marathon", "Example Marathon", "Pittsburgh", "PA", 5, "https://race.example/", COURSE_PAGE, (MARATHON,)
)
MY_MAPS_PAGE = html('<iframe src="https://www.google.com/maps/d/embed?mid=ABC123"></iframe>')


def no_overpass(query):
    raise AssertionError(f"unexpected Overpass query {query}")


def run(tmp_path, responses, races=(RACE,), previous=None, day=DAY, elevation=None, overpass=no_overpass):
    fetcher = FakeFetcher(responses)
    context = pipeline.Context(
        fetcher=fetcher,
        elevation=elevation or FakeElevation(),
        overpass=overpass,
        root=tmp_path,
        previous=previous or {},
        day=day,
    )
    entries = pipeline.crawl(list(races), context, log=lambda line: None)
    return entries, fetcher, context.elevation


def test_publishes_course_from_my_maps(tmp_path):
    [entry], _, elevation = run(tmp_path, {COURSE_PAGE: MY_MAPS_PAGE, MY_MAPS_KML: kml(("Course", coordinates(42195)))})

    assert entry["status"] == "ok"
    assert entry["file"] == "courses/pa/example-marathon/marathon.gpx"
    assert entry["source"] == {"kind": "mymaps", "url": MY_MAPS_KML, "page": COURSE_PAGE}
    assert abs(entry["length_error_pct"]) < 0.5
    assert entry["retrieved"] == "2026-11-05"
    assert entry["page"] == COURSE_PAGE
    assert elevation.calls == 1
    gpx = (tmp_path / entry["file"]).read_text()
    assert "Example Marathon – Marathon" in gpx
    assert gpx.count("<trkpt") > 2000
    assert "<ele>" in gpx


def test_unchanged_course_is_not_rebuilt(tmp_path):
    responses = {COURSE_PAGE: MY_MAPS_PAGE, MY_MAPS_KML: kml(("Course", coordinates(42195)))}
    [first], _, _ = run(tmp_path, responses)
    written = (tmp_path / first["file"]).stat().st_mtime_ns

    [second], _, elevation = run(
        tmp_path, responses, previous={("example-marathon", "marathon"): first}, day=date(2026, 11, 12)
    )

    assert elevation.calls == 0
    assert second["retrieved"] == "2026-11-05"
    assert second == first
    assert (tmp_path / first["file"]).stat().st_mtime_ns == written


def test_changed_course_is_rebuilt(tmp_path):
    [first], _, _ = run(tmp_path, {COURSE_PAGE: MY_MAPS_PAGE, MY_MAPS_KML: kml(("Course", coordinates(42195)))})
    moved = {COURSE_PAGE: MY_MAPS_PAGE, MY_MAPS_KML: kml(("Course", coordinates(42195, lon=-80.01)))}

    [second], _, elevation = run(
        tmp_path, moved, previous={("example-marathon", "marathon"): first}, day=date(2026, 11, 12)
    )

    assert elevation.calls == 1
    assert second["retrieved"] == "2026-11-12"
    assert second["geometry_sha256"] != first["geometry_sha256"]


def test_events_share_one_map(tmp_path):
    race = replace(RACE, events=(MARATHON, HALF))
    both = kml(("Full", coordinates(42195)), ("Half", coordinates(21097, lon=-80.02)))

    entries, fetcher, _ = run(tmp_path, {COURSE_PAGE: MY_MAPS_PAGE, MY_MAPS_KML: both}, races=[race])

    assert [entry["status"] for entry in entries] == ["ok", "ok"]
    assert abs(entries[1]["length_m"] - 21097) < 100
    assert fetcher.calls.count(MY_MAPS_KML) == 1
    assert fetcher.calls.count(COURSE_PAGE) == 1


def test_pdf_only_is_unsupported(tmp_path):
    responses = {
        COURSE_PAGE: html('<a href="/files/course-map.pdf">Course map</a>'),
        "https://race.example/": html("<p>Welcome</p>"),
    }

    [entry], fetcher, _ = run(tmp_path, responses)

    assert entry["status"] == "unsupported"
    assert entry["found"] == ["pdf"]
    assert "https://race.example/" in fetcher.calls
    assert "file" not in entry


def test_missing_course_page_falls_back_to_homepage(tmp_path):
    responses = {
        "https://race.example/": html('<a href="/the-course">The Course</a>'),
        "https://race.example/the-course": html('<a href="/maps/marathon.gpx">Download GPX</a>'),
        "https://race.example/maps/marathon.gpx": (
            '<?xml version="1.0"?><gpx version="1.1" xmlns="http://www.topografix.com/GPX/1/1"><trk><trkseg>'
            + "".join(f'<trkpt lat="{40 + 0.38 * ii / 60}" lon="-80"/>' for ii in range(61))
            + "</trkseg></trk></gpx>"
        ).encode(),
    }

    [entry], _, _ = run(tmp_path, responses)

    assert entry["status"] in ("ok", "warn")
    assert entry["source"]["kind"] == "gpx"
    assert entry["source"]["page"] == "https://race.example/the-course"
    assert entry["page"] == "https://race.example/"


def test_unconfirmed_course_keeps_earlier_file(tmp_path):
    [first], _, _ = run(tmp_path, {COURSE_PAGE: MY_MAPS_PAGE, MY_MAPS_KML: kml(("Course", coordinates(42195)))})

    [second], _, _ = run(
        tmp_path,
        {COURSE_PAGE: html('<a href="/course.pdf">Course map</a>')},
        previous={("example-marathon", "marathon"): first},
    )

    assert second["status"] == "stale"
    assert second["file"] == first["file"]
    assert second["retrieved"] == first["retrieved"]
    assert "kept the course read 2026-11-05" in second["detail"]


def test_manual_source_needs_no_network(tmp_path):
    manual = tmp_path / "manual" / "pa" / "example-marathon" / "marathon.gpx"
    manual.parent.mkdir(parents=True)
    manual.write_text(
        '<?xml version="1.0"?><gpx version="1.1" xmlns="http://www.topografix.com/GPX/1/1"><trk><trkseg>'
        + "".join(f'<trkpt lat="{40 + 0.3795 * ii / 60}" lon="-80"/>' for ii in range(61))
        + "</trkseg></trk></gpx>"
    )
    race = replace(RACE, course_url=None, events=(replace(MARATHON, source="manual/pa/example-marathon/marathon.gpx"),))

    [entry], fetcher, _ = run(tmp_path, {}, races=[race])

    assert entry["status"] == "ok"
    assert entry["source"]["kind"] == "manual"
    assert fetcher.calls == []


def test_explicit_source_url_is_read_first(tmp_path):
    direct = "https://files.example/course.kml"
    race = replace(RACE, events=(replace(MARATHON, source=direct),))

    [entry], _, _ = run(
        tmp_path,
        {COURSE_PAGE: html("<p>Map coming soon</p>"), direct: kml(("Course", coordinates(42195)))},
        races=[race],
    )

    assert entry["status"] == "ok"
    assert entry["source"]["url"] == direct
    assert entry["source"]["page"] == "races.yaml"


def test_blocked_site_is_an_error(tmp_path):
    blocked = {
        COURSE_PAGE: Blocked(COURSE_PAGE),
        "https://race.example/": Blocked("https://race.example/"),
    }

    [entry], _, _ = run(tmp_path, blocked)

    assert entry["status"] == "error"
    assert "disallowed by robots.txt: https://race.example/course" in entry["detail"]


def test_short_line_is_no_match(tmp_path):
    [entry], _, _ = run(tmp_path, {COURSE_PAGE: MY_MAPS_PAGE, MY_MAPS_KML: kml(("10K loop", coordinates(10000)))})

    assert entry["status"] == "no-match"
    assert "no line near 42.20 km" in entry["detail"]


def test_course_outside_the_us_is_rejected(tmp_path):
    london = kml(("Course", coordinates(42195, lon=-0.1, lat=51.5)))

    [entry], _, _ = run(tmp_path, {COURSE_PAGE: MY_MAPS_PAGE, MY_MAPS_KML: london})

    assert entry["status"] == "reject"
    assert "file" not in entry


def test_elevation_failure_is_an_error(tmp_path):
    class BrokenElevation:
        def profile(self, points):
            raise ValueError("every sample is NoData")

    [entry], _, _ = run(
        tmp_path,
        {COURSE_PAGE: MY_MAPS_PAGE, MY_MAPS_KML: kml(("Course", coordinates(42195)))},
        elevation=BrokenElevation(),
    )

    assert entry["status"] == "error"
    assert "elevation lookup failed" in entry["detail"]
    assert not (tmp_path / "courses").exists()


def test_course_link_that_serves_a_file_is_a_source(tmp_path):
    responses = {
        COURSE_PAGE: html('<a href="/modules/media/?id=7">Course map</a>'),
        "https://race.example/modules/media/?id=7": kml(("Course", coordinates(42195))),
    }
    fetcher = FakeFetcher(responses)
    fetcher.media["https://race.example/modules/media/?id=7"] = "application/vnd.google-earth.kml+xml"
    context = pipeline.Context(
        fetcher=fetcher, elevation=FakeElevation(), overpass=no_overpass, root=tmp_path, previous={}, day=DAY
    )
    race = replace(RACE, course_url=None, website=COURSE_PAGE)

    [entry] = pipeline.crawl([race], context, log=lambda line: None)

    assert entry["status"] == "ok"
    assert entry["source"]["kind"] == "kml"
    assert fetcher.calls.count("https://race.example/modules/media/?id=7") == 1


def test_openstreetmap_relation_source(tmp_path):
    relation = "https://www.openstreetmap.org/relation/11680552"
    span = 42195 / METERS_PER_DEGREE
    cuts = [40.0, 40.0 + span / 3, 40.0 + 2 * span / 3, 40.0 + span]

    def way(south, north, reverse=False):
        nodes = [{"lat": south + (north - south) * ii / 30, "lon": -80.0} for ii in range(31)]
        return {"type": "way", "role": "", "geometry": nodes[::-1] if reverse else nodes}

    members = [
        way(cuts[1], cuts[2], reverse=True),
        way(cuts[2], cuts[3], reverse=True),
        way(cuts[0], cuts[1]),
        {"type": "node", "role": "start", "lat": cuts[0], "lon": -80.0},
    ]
    body = json.dumps({"elements": [{"type": "relation", "id": 11680552, "members": members}]}).encode()
    queries = []
    race = replace(RACE, course_url=None, events=(replace(MARATHON, source=relation),))

    [entry], fetcher, _ = run(tmp_path, {}, races=[race], overpass=lambda query: queries.append(query) or body)

    assert entry["status"] == "ok"
    assert entry["source"]["kind"] == "osm"
    assert entry["method"] == "chain:3/3"
    assert entry["oriented_by"] == "markers"
    assert queries == ["[out:json][timeout:90];relation(11680552);out geom;"]
    assert fetcher.calls == []
    gpx = (tmp_path / entry["file"]).read_text()
    assert gpx.index('lat="40.000000"') < gpx.index(f'lat="{cuts[3]:.6f}"')


def test_file_from_an_older_pipeline_is_not_kept(tmp_path):
    [first], _, _ = run(tmp_path, {COURSE_PAGE: MY_MAPS_PAGE, MY_MAPS_KML: kml(("Course", coordinates(42195)))})
    older = {**first, "pipeline": pipeline.PIPELINE_VERSION - 1}

    [second], _, _ = run(
        tmp_path, {COURSE_PAGE: html("<p>No map yet</p>")}, previous={("example-marathon", "marathon"): older}
    )

    assert second["status"] == "no-source"
    assert "file" not in second
