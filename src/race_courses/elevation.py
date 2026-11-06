"""Add USGS 3DEP elevation to a track and level the bridges and tunnels it crosses."""

import json
import math
import time
from collections.abc import Callable, Sequence
from itertools import pairwise

import httpx

from race_courses import api
from race_courses.geometry import EARTH_RADIUS_M, cumulative_m
from race_courses.models import Point

SAMPLES_URL = "https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/getSamples"
STRUCTURES_QUERY = (
    "[out:json][timeout:60];("
    'way["highway"]["bridge"]["bridge"!="no"]({bbox});'
    'way["highway"]["tunnel"]["tunnel"!="no"]({bbox});'
    ");out geom;"
)
BBOX_PAD_M = 100.0
ON_STRUCTURE_M = 12.0
HEADING_TOLERANCE = math.cos(math.radians(35.0))
CELL_M = 100.0

XY = tuple[float, float]
Segment = tuple[XY, XY]


class Elevation:
    """Ground elevation for course points, with bridges and tunnels levelled."""

    def __init__(
        self,
        client: httpx.Client,
        batch: int = 400,
        sleep: Callable[[float], None] = time.sleep,
    ):
        self.client = client
        self.batch = batch
        self.sleep = sleep

    def profile(self, points: Sequence[Point]) -> tuple[Point, ...]:
        """The same points with ele filled, rounded to 0.1 m."""
        samples: list[float | None] = []
        for start in range(0, len(points), self.batch):
            samples.extend(self.sample(points[start:start + self.batch]))
        distances = cumulative_m(points)
        eles = fill(samples, distances)
        on_structure = structure_mask(points, self.structures(points))
        if not all(on_structure):
            eles = fill([None if flagged else ele for ele, flagged in zip(eles, on_structure, strict=True)], distances)
        return tuple(Point(point.lat, point.lon, round(ele, 1)) for point, ele in zip(points, eles, strict=True))

    def sample(self, points: Sequence[Point]) -> list[float | None]:
        """One 3DEP getSamples call; None stands for NoData."""
        geometry = {"points": [[point.lon, point.lat] for point in points], "spatialReference": {"wkid": 4326}}
        form = {
            "geometry": json.dumps(geometry),
            "geometryType": "esriGeometryMultipoint",
            "returnFirstValueOnly": "true",
            "f": "json",
        }
        response = api.post(
            self.client, SAMPLES_URL, form, retry_statuses=range(500, 600), timeout=60.0, sleep=self.sleep
        )
        body = response.json()
        if "samples" not in body:
            raise ValueError(f"3DEP getSamples failed: {body.get('error', body)}")
        values = {sample["locationId"]: sample["value"] for sample in body["samples"]}
        if len(values) != len(points):
            raise ValueError(f"3DEP returned {len(values)} samples for {len(points)} points")
        return [None if values[ii] == "NoData" else float(values[ii]) for ii in range(len(points))]

    def structures(self, points: Sequence[Point]) -> list[tuple[Point, Point]]:
        """Road segments on bridges or in tunnels, from OpenStreetMap around the course."""
        lat_pad = math.degrees(BBOX_PAD_M / EARTH_RADIUS_M)
        lats = [point.lat for point in points]
        lons = [point.lon for point in points]
        lon_pad = lat_pad / math.cos(math.radians((min(lats) + max(lats)) / 2))
        south, north = min(lats) - lat_pad, max(lats) + lat_pad
        west, east = min(lons) - lon_pad, max(lons) + lon_pad
        query = STRUCTURES_QUERY.format(bbox=f"{south:.6f},{west:.6f},{north:.6f},{east:.6f}")
        body = json.loads(api.overpass(self.client, query, self.sleep))
        # Overpass reports a query that ran out of time or memory as a remark on a 200 response.
        if "elements" not in body or "runtime error" in body.get("remark", ""):
            raise ValueError(f"Overpass query failed: {body.get('remark', body)}")
        segments: list[tuple[Point, Point]] = []
        for way in body["elements"]:
            nodes = [Point(node["lat"], node["lon"]) for node in way.get("geometry", [])]
            segments.extend(pairwise(nodes))
        return segments


def fill(values: Sequence[float | None], distances: Sequence[float]) -> list[float]:
    """Replace each run of None by linear interpolation along distance; hold the ends flat."""
    known = [ii for ii, value in enumerate(values) if value is not None]
    if not known:
        raise ValueError("no elevation data for any point")
    result = [0.0] * len(values)
    for ii in range(known[0]):
        result[ii] = values[known[0]]
    for before, after in pairwise(known):
        result[before] = values[before]
        span = distances[after] - distances[before]
        for ii in range(before + 1, after):
            fraction = (distances[ii] - distances[before]) / span
            result[ii] = values[before] + (values[after] - values[before]) * fraction
    for ii in range(known[-1], len(values)):
        result[ii] = values[known[-1]]
    return result


def structure_mask(points: Sequence[Point], structures: Sequence[tuple[Point, Point]]) -> list[bool]:
    """Which course points run along a bridge or tunnel segment, not under or over one."""
    if not structures:
        return [False] * len(points)
    origin = points[0]
    course = [project(point, origin) for point in points]
    grid: dict[tuple[int, int], list[Segment]] = {}
    for start, end in structures:
        segment = (project(start, origin), project(end, origin))
        for cell in cells_around(segment):
            grid.setdefault(cell, []).append(segment)
    mask = []
    for ii, position in enumerate(course):
        behind, ahead = course[max(ii - 1, 0)], course[min(ii + 1, len(course) - 1)]
        heading = (ahead[0] - behind[0], ahead[1] - behind[1])
        cell = (math.floor(position[0] / CELL_M), math.floor(position[1] / CELL_M))
        mask.append(any(runs_along(position, heading, segment) for segment in grid.get(cell, ())))
    return mask


def project(point: Point, origin: Point) -> XY:
    """Local east and north metres from origin; good enough across one city."""
    east = math.radians(point.lon - origin.lon) * EARTH_RADIUS_M * math.cos(math.radians(origin.lat))
    north = math.radians(point.lat - origin.lat) * EARTH_RADIUS_M
    return east, north


def cells_around(segment: Segment) -> list[tuple[int, int]]:
    """Grid cells that a point within ON_STRUCTURE_M of the segment can fall in."""
    (start_x, start_y), (end_x, end_y) = segment
    columns = range(
        math.floor((min(start_x, end_x) - ON_STRUCTURE_M) / CELL_M),
        math.floor((max(start_x, end_x) + ON_STRUCTURE_M) / CELL_M) + 1,
    )
    rows = range(
        math.floor((min(start_y, end_y) - ON_STRUCTURE_M) / CELL_M),
        math.floor((max(start_y, end_y) + ON_STRUCTURE_M) / CELL_M) + 1,
    )
    return [(column, row) for column in columns for row in rows]


def runs_along(position: XY, heading: XY, segment: Segment) -> bool:
    """True when position is near the segment and heading is near parallel to it."""
    (start_x, start_y), (end_x, end_y) = segment
    seg_x, seg_y = end_x - start_x, end_y - start_y
    seg_len = math.hypot(seg_x, seg_y)
    heading_len = math.hypot(heading[0], heading[1])
    if seg_len == 0 or heading_len == 0:
        return False
    if abs(seg_x * heading[0] + seg_y * heading[1]) < HEADING_TOLERANCE * seg_len * heading_len:
        return False
    rel_x, rel_y = position[0] - start_x, position[1] - start_y
    fraction = max(0.0, min(1.0, (rel_x * seg_x + rel_y * seg_y) / seg_len**2))
    return math.hypot(rel_x - fraction * seg_x, rel_y - fraction * seg_y) <= ON_STRUCTURE_M


def gain_loss(points: Sequence[Point], threshold_m: float = 1.0) -> tuple[float, float]:
    """Total ascent and descent, ignoring moves smaller than threshold_m from the last counted level."""
    gain = loss = 0.0
    reference = points[0].ele
    for point in points:
        delta = point.ele - reference
        if delta >= threshold_m:
            gain += delta
            reference = point.ele
        elif delta <= -threshold_m:
            loss -= delta
            reference = point.ele
    return gain, loss
