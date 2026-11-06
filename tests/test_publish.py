from datetime import date
from xml.etree import ElementTree

from race_courses import publish
from race_courses.models import Point

NS = {"gpx": publish.GPX_NS}


def entry(race, event, status, state="PA", **fields):
    return {
        "race": race,
        "event": event,
        "name": race.replace("-", " ").title(),
        "event_name": event.title(),
        "state": state,
        "status": status,
        "detail": "",
        **fields,
    }


def test_gpx_has_one_track_with_elevation():
    points = [Point(40.4406, -79.9959, 233.27), Point(40.4466, -80.0089, None)]

    data = publish.gpx_bytes(
        points, "Pittsburgh Marathon – Marathon", "From the organizer's map.", "https://example.com", date(2026, 11, 5)
    )
    root = ElementTree.fromstring(data)

    assert data.startswith(b"<?xml")
    assert root.get("version") == "1.1"
    assert root.find("gpx:metadata/gpx:name", NS).text == "Pittsburgh Marathon – Marathon"
    assert root.find("gpx:metadata/gpx:link", NS).get("href") == "https://example.com"
    assert root.find("gpx:metadata/gpx:time", NS).text == "2026-11-05T00:00:00Z"
    track_points = root.findall("gpx:trk/gpx:trkseg/gpx:trkpt", NS)
    assert [(point.get("lat"), point.get("lon")) for point in track_points] == [
        ("40.440600", "-79.995900"),
        ("40.446600", "-80.008900"),
    ]
    assert track_points[0].find("gpx:ele", NS).text == "233.3"
    assert track_points[1].find("gpx:ele", NS) is None


def test_index_round_trip_is_sorted(tmp_path):
    path = tmp_path / "index.json"
    entries = [
        entry("b-race", "5k", "ok", state="TX"),
        entry("a-race", "marathon", "ok"),
        entry("a-race", "half", "warn"),
    ]

    publish.write_index(path, entries)
    loaded = publish.read_index(path)

    assert list(loaded) == [("a-race", "half"), ("a-race", "marathon"), ("b-race", "5k")]
    assert publish.read_index(tmp_path / "missing.json") == {}


def test_prune_removes_unlisted_files_and_empty_folders(tmp_path):
    kept = tmp_path / "courses" / "pa" / "a-race" / "marathon.gpx"
    orphan = tmp_path / "courses" / "tx" / "gone-race" / "5k.gpx"
    for path in (kept, orphan):
        path.parent.mkdir(parents=True)
        path.write_text("<gpx/>")

    removed = publish.prune(tmp_path, [entry("a-race", "marathon", "ok", file="courses/pa/a-race/marathon.gpx")])

    assert removed == [orphan]
    assert kept.exists()
    assert not (tmp_path / "courses" / "tx").exists()


def test_prune_without_courses_folder(tmp_path):
    assert publish.prune(tmp_path, []) == []


def test_coverage_counts_and_lists_missing_events():
    entries = [
        entry("a-race", "marathon", "ok"),
        entry("a-race", "half", "stale"),
        entry(
            "b-race",
            "5k",
            "unsupported",
            page="https://b.example/course",
            detail="only pdf | strava",
            found=["pdf", "strava"],
        ),
        entry("c-race", "10k", "unsupported", found=["pdf"]),
    ]

    text = publish.coverage_markdown(entries, date(2026, 11, 5))

    assert "3 races, 4 events, 2 courses published (50%)" in text
    assert "| ok | 1 |" in text and "| stale | 1 |" in text and "| unsupported | 2 |" in text
    assert "| warn |" not in text
    assert "pdf 2, strava 1." in text
    assert "| PA | [B Race](https://b.example/course) | 5K | unsupported | only pdf / strava |" in text
    assert "A Race" not in text.split("## Not covered yet")[1]
