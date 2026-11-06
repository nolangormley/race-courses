"""Read race courses that OpenStreetMap maps as route relations (ODbL)."""

import json
import re

from race_courses.models import Geometry, Line, Marker, Point

RELATION_URL = re.compile(r"^https?://(?:www\.)?openstreetmap\.org/relation/(\d+)/?$")
RELATION_QUERY = "[out:json][timeout:90];relation({relation_id});out geom;"
ROLE_NAMES = {"start": "Start", "end": "Finish", "finish": "Finish"}


def relation_query(url: str) -> str:
    """The Overpass query that returns the relation of an openstreetmap.org/relation/<id> URL."""
    match = RELATION_URL.match(url)
    if match is None:
        raise ValueError(f"not an OpenStreetMap relation URL: {url}")
    return RELATION_QUERY.format(relation_id=match.group(1))


def read_relation(data: bytes) -> Geometry:
    """One line per way member, and start and finish markers from the node roles."""
    try:
        relations = [element for element in json.loads(data)["elements"] if element["type"] == "relation"]
        if len(relations) != 1:
            raise ValueError(f"expected one relation, found {len(relations)}")
        lines, markers = [], []
        for member in relations[0]["members"]:
            if member["type"] == "way" and len(member.get("geometry") or ()) >= 2:
                points = tuple(Point(node["lat"], node["lon"]) for node in member["geometry"])
                lines.append(Line(name=member["role"], points=points))
            elif member["type"] == "node" and member["role"] in ROLE_NAMES:
                markers.append(Marker(name=ROLE_NAMES[member["role"]], point=Point(member["lat"], member["lon"])))
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"not an Overpass relation response: {error}") from error
    return Geometry(lines=tuple(lines), markers=tuple(markers))
