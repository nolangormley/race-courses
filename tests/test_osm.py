import json

import pytest

from race_courses import discover, osm


def way(role, *points):
    return {"type": "way", "ref": 1, "role": role, "geometry": [{"lat": lat, "lon": lon} for lat, lon in points]}


def relation_bytes(*members, extra=()):
    elements = [{"type": "relation", "id": 7, "members": list(members), "tags": {"route": "running"}}, *extra]
    return json.dumps({"version": 0.6, "elements": elements}).encode()


@pytest.mark.parametrize(
    "url",
    [
        "https://www.openstreetmap.org/relation/11680552",
        "http://openstreetmap.org/relation/11680552/",
    ],
)
def test_relation_query(url):
    assert osm.relation_query(url) == "[out:json][timeout:90];relation(11680552);out geom;"


def test_relation_query_refuses_other_urls():
    with pytest.raises(ValueError):
        osm.relation_query("https://www.openstreetmap.org/way/42")


def test_relation_links_are_osm_sources():
    ref = discover.source_ref("https://www.openstreetmap.org/relation/11680552", "races.yaml")
    assert ref.kind == "osm"
    assert ref.url == "https://www.openstreetmap.org/relation/11680552"


def test_reads_ways_in_member_order_and_role_markers():
    data = relation_bytes(
        way("", (42.0, -71.0), (42.1, -71.0)),
        {"type": "node", "ref": 2, "role": "start", "lat": 42.0, "lon": -71.0},
        way("forward", (42.1, -71.0), (42.2, -71.0), (42.3, -71.0)),
        way("", (42.3, -71.0)),
        {"type": "node", "ref": 3, "role": "end", "lat": 42.3, "lon": -71.0},
        {"type": "node", "ref": 4, "role": "marker", "lat": 42.15, "lon": -71.0},
    )

    geometry = osm.read_relation(data)

    assert [len(line.points) for line in geometry.lines] == [2, 3]
    assert geometry.lines[1].name == "forward"
    assert [(marker.name, marker.point.lat) for marker in geometry.markers] == [("Start", 42.0), ("Finish", 42.3)]


@pytest.mark.parametrize(
    "data",
    [
        b"<html>busy</html>",
        json.dumps({"elements": []}).encode(),
        relation_bytes(extra=[{"type": "relation", "id": 8, "members": []}]),
        relation_bytes({"type": "way", "role": "", "geometry": [{"lat": 1.0}, {"lat": 2.0}]}),
    ],
)
def test_bad_responses_raise_value_error(data):
    with pytest.raises(ValueError):
        osm.read_relation(data)
