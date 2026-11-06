import pytest
import yaml

from race_courses import catalog

RACE = {
    "slug": "pittsburgh-marathon",
    "name": "Pittsburgh Marathon",
    "city": "Pittsburgh",
    "state": "PA",
    "month": 5,
    "website": "https://www.thepittsburghmarathon.com/",
    "course_url": "https://www.thepittsburghmarathon.com/course",
    "events": [
        {
            "name": "Marathon",
            "distance_m": 42195,
            "finishers": 3850,
            "finishers_year": 2025,
            "finishers_source": "https://example.com/results",
        },
        {
            "name": "Half Marathon",
            "distance_m": 21097,
            "finishers": 9000,
            "finishers_year": 2025,
            "finishers_source": "https://example.com/results",
            "source": "manual/pa/pittsburgh-marathon/half-marathon.gpx",
        },
    ],
}


def write(tmp_path, entries):
    path = tmp_path / "races.yaml"
    path.write_text(yaml.safe_dump(entries))
    return path


def with_changes(race_changes=None, event_changes=None):
    race = {**RACE, "events": [{**RACE["events"][0], **(event_changes or {})}]}
    return {**race, **(race_changes or {})}


def problems(tmp_path, entries):
    with pytest.raises(ValueError) as caught:
        catalog.load(write(tmp_path, entries))
    return str(caught.value)


def test_loads_races_and_events(tmp_path):
    manual = tmp_path / "manual" / "pa" / "pittsburgh-marathon" / "half-marathon.gpx"
    manual.parent.mkdir(parents=True)
    manual.write_text("<gpx/>")

    [race] = catalog.load(write(tmp_path, [RACE]))

    assert race.slug == "pittsburgh-marathon"
    assert race.course_url == "https://www.thepittsburghmarathon.com/course"
    assert [event.slug for event in race.events] == ["marathon", "half-marathon"]
    assert race.events[0].distance_m == 42195.0
    assert race.events[1].source == "manual/pa/pittsburgh-marathon/half-marathon.gpx"


def test_empty_file_has_no_races(tmp_path):
    path = tmp_path / "races.yaml"
    path.write_text("")
    assert catalog.load(path) == []


def test_event_slug():
    assert catalog.event_slug("5K") == "5k"
    assert catalog.event_slug("Half Marathon") == "half-marathon"
    assert catalog.event_slug("10 Mile (Run)") == "10-mile-run"


@pytest.mark.parametrize(
    ("race_changes", "event_changes", "expected"),
    [
        ({"slug": "Pittsburgh_Marathon"}, None, "slug must be lowercase"),
        ({"state": "XX"}, None, "unknown state 'XX'"),
        ({"month": 13}, None, "month must be 1 to 12"),
        ({"website": "www.example.com"}, None, "website must start with http"),
        ({"colour": "red"}, None, "unknown key 'colour'"),
        ({"events": {"name": "Marathon"}}, None, "events must be a list"),
        (None, {"finishers": 999}, "finishers must be at least 1000"),
        (None, {"distance_m": 0}, "distance_m must be a positive number"),
        (None, {"finishers_source": ""}, "missing finishers_source"),
        (None, {"distance_m": -5}, "distance_m must be a positive number"),
        (None, {"finishers_year": 25}, "finishers_year must be a year"),
        (None, {"source": "ftp://example.com/course.gpx"}, "source must be a URL or a path under manual/"),
        (None, {"source": "manual/pa/missing.gpx"}, "manual/pa/missing.gpx does not exist"),
        (None, {"pace": "fast"}, "unknown key 'pace'"),
    ],
)
def test_reports_problems(tmp_path, race_changes, event_changes, expected):
    message = problems(tmp_path, [with_changes(race_changes, event_changes)])
    assert expected in message
    assert "entry 1" in message


def test_reports_missing_fields(tmp_path):
    message = problems(tmp_path, [{"slug": "lonely-5k"}])
    for key in ("name", "city", "state", "month", "website", "events"):
        assert f"missing {key}" in message


def test_reports_duplicate_slugs_and_event_names(tmp_path):
    twin_events = with_changes()
    twin_events["events"] = [RACE["events"][0], RACE["events"][0]]
    message = problems(tmp_path, [with_changes(), with_changes(), twin_events])
    assert "entry 2 (pittsburgh-marathon): slug is used twice" in message
    assert "two events have the same name" in message


def test_reports_every_problem_at_once(tmp_path):
    message = problems(tmp_path, [with_changes({"state": "XX"}), "not a race", with_changes({"month": 0})])
    assert "entry 1" in message and "entry 2: is not a mapping" in message and "entry 3" in message
