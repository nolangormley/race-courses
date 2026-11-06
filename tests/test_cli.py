import json
from contextlib import nullcontext

import yaml

from race_courses import cli

from tests.fakes import FakeElevation, FakeFetcher, coordinates, html, kml


def race(slug, course_url):
    return {
        "slug": slug,
        "name": slug.replace("-", " ").title(),
        "city": "Pittsburgh",
        "state": "PA",
        "month": 5,
        "website": f"https://{slug}.example/",
        "course_url": course_url,
        "events": [{
            "name": "5K",
            "distance_m": 5000,
            "finishers": 1500,
            "finishers_year": 2025,
            "finishers_source": f"https://{slug}.example/results",
        }],
    }


def setup(tmp_path, monkeypatch, races, responses):
    (tmp_path / "races.yaml").write_text(yaml.safe_dump(races))
    monkeypatch.setattr(cli, "make_client", lambda: nullcontext())
    monkeypatch.setattr(cli, "Fetcher", lambda client: FakeFetcher(responses))
    monkeypatch.setattr(cli, "Elevation", lambda client: FakeElevation())


RESPONSES = {
    "https://first-5k.example/course": html('<a href="/course.kml">Course map (KML)</a>'),
    "https://first-5k.example/course.kml": kml(("5K", coordinates(5000))),
    "https://second-5k.example/course": html('<a href="/course.pdf">Course map</a>'),
}


def test_check_counts_races(tmp_path, capsys):
    (tmp_path / "races.yaml").write_text(yaml.safe_dump([race("first-5k", None)]))

    assert cli.main(["--root", str(tmp_path), "check"]) == 0
    assert "1 races, 1 events" in capsys.readouterr().out


def test_check_fails_on_problems(tmp_path, capsys):
    (tmp_path / "races.yaml").write_text(yaml.safe_dump([{**race("first-5k", None), "state": "XX"}]))

    assert cli.main(["--root", str(tmp_path), "check"]) == 1
    assert "unknown state 'XX'" in capsys.readouterr().err


def test_crawl_writes_index_coverage_and_files(tmp_path, monkeypatch):
    races = [race("first-5k", "https://first-5k.example/course"), race("second-5k", "https://second-5k.example/course")]
    setup(tmp_path, monkeypatch, races, RESPONSES)

    assert cli.main(["--root", str(tmp_path), "crawl"]) == 0

    index = json.loads((tmp_path / "index.json").read_text())
    assert [(entry["race"], entry["status"]) for entry in index] == [("first-5k", "ok"), ("second-5k", "unsupported")]
    assert (tmp_path / "courses" / "pa" / "first-5k" / "5k.gpx").exists()
    assert "2 races, 2 events, 1 courses published (50%)" in (tmp_path / "COVERAGE.md").read_text()


def test_crawl_only_keeps_other_entries_and_drops_removed_races(tmp_path, monkeypatch):
    races = [race("first-5k", "https://first-5k.example/course"), race("second-5k", "https://second-5k.example/course")]
    setup(tmp_path, monkeypatch, races, RESPONSES)
    assert cli.main(["--root", str(tmp_path), "crawl"]) == 0

    setup(tmp_path, monkeypatch, races[1:], RESPONSES)
    assert cli.main(["--root", str(tmp_path), "crawl", "--only", "second-5k"]) == 0

    index = json.loads((tmp_path / "index.json").read_text())
    assert [entry["race"] for entry in index] == ["second-5k"]
    assert list((tmp_path / "courses").rglob("*")) == []


def test_crawl_rejects_unknown_race(tmp_path, monkeypatch, capsys):
    setup(tmp_path, monkeypatch, [race("first-5k", None)], RESPONSES)

    assert cli.main(["--root", str(tmp_path), "crawl", "--only", "nope"]) == 1
    assert "unknown race: nope" in capsys.readouterr().err
