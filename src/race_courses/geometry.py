"""Pick the one course line out of a messy source map, clean it, and resample it."""

import math
import re
from collections.abc import Sequence
from dataclasses import dataclass
from itertools import count, pairwise

from race_courses.models import Course, Geometry, Marker, Point

STEP_M = 20.0
END_SLACK_M = 0.001
EARTH_RADIUS_M = 6_371_008.8
JOIN_M = 100.0
FIT_TOLERANCE = 0.25
DUPLICATE_M = 1.0
SPIKE_LEG_M = 30.0
SPIKE_GAP_RATIO = 0.1
MARKER_REACH_M = 1000.0
START_NAME = re.compile(r"\bstart", re.IGNORECASE)
FINISH_NAME = re.compile(r"\bfinish", re.IGNORECASE)
NAMED_HALF = re.compile(r"\bhalf(?:[\s-]*marathon)?\b", re.IGNORECASE)
NAMED_MARATHON = re.compile(r"\bmarathon\b", re.IGNORECASE)
NAMED_LENGTH = re.compile(r"(\d+(?:\.\d+)?)\s*-?\s*(km|k|miles|miler|mile|mi)\b", re.IGNORECASE)
UNIT_M = {"k": 1000.0, "km": 1000.0, "mi": 1609.344, "mile": 1609.344, "miles": 1609.344, "miler": 1609.344}
NAME_TOLERANCE = 0.1

Endpoint = tuple[int, int]


@dataclass(frozen=True)
class Chain:
    """Cleaned lines in travel order; each piece is (line index, reversed)."""

    pieces: tuple[tuple[int, bool], ...]
    length_m: float


def haversine_m(point_a: Point, point_b: Point) -> float:
    """Great-circle distance between two points in metres."""
    lat_a, lat_b = math.radians(point_a.lat), math.radians(point_b.lat)
    half_dlat = math.radians(point_b.lat - point_a.lat) / 2
    half_dlon = math.radians(point_b.lon - point_a.lon) / 2
    chord = math.sin(half_dlat) ** 2 + math.cos(lat_a) * math.cos(lat_b) * math.sin(half_dlon) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(chord))


def cumulative_m(points: Sequence[Point]) -> list[float]:
    """Distance along the path at each point; the first entry is 0."""
    if not points:
        return []
    distances = [0.0]
    for previous, current in pairwise(points):
        distances.append(distances[-1] + haversine_m(previous, current))
    return distances


def assemble(geometry: Geometry, target_m: float) -> Course | None:
    """Pick the line or chain of lines whose length is closest to target_m."""
    named_for_target = [line for line in geometry.lines if name_fits(line.name, target_m)]
    lines = drop_copies([cleaned for cleaned in (clean(line.points) for line in named_for_target) if len(cleaned) >= 2])
    lengths = [cumulative_m(line)[-1] for line in lines]
    neighbours = endpoint_neighbours(lines)
    candidates: dict[frozenset[int], Chain] = {}
    for index in range(len(lines)):
        candidates[frozenset([index])] = Chain(((index, False),), lengths[index])
    for index in range(len(lines)):
        for reversed_start in (False, True):
            chain = chain_from(index, reversed_start, lengths, neighbours)
            candidates.setdefault(frozenset(piece[0] for piece in chain.pieces), chain)
    fitting = [
        chain for chain in candidates.values()
        if abs(chain.length_m - target_m) <= FIT_TOLERANCE * target_m
    ]
    if not fitting:
        return None
    best = min(fitting, key=lambda chain: abs(chain.length_m - target_m))
    joined: list[Point] = []
    for index, reversed_piece in best.pieces:
        joined.extend(reversed(lines[index]) if reversed_piece else lines[index])
    points, oriented_by = orient(clean(joined), geometry.markers)
    method = "line" if len(best.pieces) == 1 else f"chain:{len(best.pieces)}/{len(lines)}"
    return Course(points=points, length_m=cumulative_m(points)[-1], method=method, oriented_by=oriented_by)


def named_distances(name: str) -> list[float]:
    """Race distances that a line name states, for example 14000.0 for "2025 14k"."""
    distances = [21097.5 for _ in NAMED_HALF.finditer(name)]
    rest = NAMED_HALF.sub(" ", name)
    distances += [42195.0 for _ in NAMED_MARATHON.finditer(rest)]
    distances += [float(number) * UNIT_M[unit.lower()] for number, unit in NAMED_LENGTH.findall(rest)]
    return distances


def name_fits(name: str, target_m: float) -> bool:
    """False when the name states only distances that differ from target_m, such as a "7K" line for a half."""
    stated = named_distances(name)
    return not stated or any(abs(distance - target_m) <= NAME_TOLERANCE * target_m for distance in stated)


def clean(points: Sequence[Point]) -> list[Point]:
    """Drop consecutive duplicate points and isolated spikes."""
    distinct: list[Point] = []
    for point in points:
        if not distinct or haversine_m(distinct[-1], point) >= DUPLICATE_M:
            distinct.append(point)
    kept = distinct[:1]
    for ii in range(1, len(distinct) - 1):
        if not is_spike(kept[-1], distinct[ii], distinct[ii + 1]):
            kept.append(distinct[ii])
    if len(distinct) > 1:
        kept.append(distinct[-1])
    return kept


def is_spike(previous: Point, current: Point, following: Point) -> bool:
    shorter_leg = min(haversine_m(previous, current), haversine_m(current, following))
    return shorter_leg > SPIKE_LEG_M and haversine_m(previous, following) < SPIKE_GAP_RATIO * shorter_leg


def drop_copies(lines: list[list[Point]]) -> list[list[Point]]:
    """Keep the first of any lines drawn twice over the same points."""
    kept: list[list[Point]] = []
    for line in lines:
        if not any(is_copy(line, earlier) for earlier in kept):
            kept.append(line)
    return kept


def is_copy(line_a: list[Point], line_b: list[Point]) -> bool:
    return len(line_a) == len(line_b) and all(
        haversine_m(point_a, point_b) < DUPLICATE_M for point_a, point_b in zip(line_a, line_b, strict=True)
    )


def endpoint_neighbours(lines: list[list[Point]]) -> dict[Endpoint, list[tuple[float, Endpoint]]]:
    """For each line end (index, 0 for first or 1 for last), the other lines' ends within JOIN_M."""
    located = {
        (index, end): line[0] if end == 0 else line[-1]
        for index, line in enumerate(lines)
        for end in (0, 1)
    }
    neighbours: dict[Endpoint, list[tuple[float, Endpoint]]] = {key: [] for key in located}
    ordered = sorted(located, key=lambda key: located[key].lat)
    lat_window = math.degrees(JOIN_M / EARTH_RADIUS_M)
    for ii, key_a in enumerate(ordered):
        for jj in range(ii + 1, len(ordered)):
            key_b = ordered[jj]
            if located[key_b].lat - located[key_a].lat > lat_window:
                break
            if key_a[0] == key_b[0]:
                continue
            distance = haversine_m(located[key_a], located[key_b])
            if distance <= JOIN_M:
                neighbours[key_a].append((distance, key_b))
                neighbours[key_b].append((distance, key_a))
    for near in neighbours.values():
        near.sort()
    return neighbours


def chain_from(
    start: int,
    reversed_start: bool,
    lengths: list[float],
    neighbours: dict[Endpoint, list[tuple[float, Endpoint]]],
) -> Chain:
    """Greedily extend from one line's tail to the nearest unused line end."""
    pieces = [(start, reversed_start)]
    used = {start}
    tail = (start, 0 if reversed_start else 1)
    length = lengths[start]
    while True:
        join = next(((gap, key) for gap, key in neighbours[tail] if key[0] not in used), None)
        if join is None:
            return Chain(tuple(pieces), length)
        gap, (index, end) = join
        used.add(index)
        pieces.append((index, end == 1))
        tail = (index, 1 - end)
        length += gap + lengths[index]


def orient(points: list[Point], markers: Sequence[Marker]) -> tuple[tuple[Point, ...], str]:
    """Reverse the course when start or finish markers say it was drawn backwards."""
    first, last = points[0], points[-1]
    start = nearest_marker([marker for marker in markers if START_NAME.search(marker.name)], first, last)
    finish = nearest_marker([marker for marker in markers if FINISH_NAME.search(marker.name)], first, last)
    if start is None and finish is None:
        return tuple(points), "as-drawn"
    as_drawn = flipped = 0.0
    if start is not None:
        as_drawn += haversine_m(start, first)
        flipped += haversine_m(start, last)
    if finish is not None:
        as_drawn += haversine_m(finish, last)
        flipped += haversine_m(finish, first)
    return tuple(reversed(points) if flipped < as_drawn else points), "markers"


def nearest_marker(markers: list[Marker], first: Point, last: Point) -> Point | None:
    """The marker closest to either end of the course, if one is within reach."""
    reaches = [
        min(haversine_m(marker.point, first), haversine_m(marker.point, last)) for marker in markers
    ]
    if not reaches or min(reaches) > MARKER_REACH_M:
        return None
    return markers[reaches.index(min(reaches))].point


def resample(points: Sequence[Point], step_m: float = STEP_M) -> tuple[Point, ...]:
    """Points every step_m along the path, plus the exact last point."""
    distances = cumulative_m(points)
    total = distances[-1]
    result: list[Point] = []
    segment = 0
    for step in count():
        target = step * step_m
        if target > total - END_SLACK_M:
            break
        while distances[segment + 1] <= target:
            segment += 1
        fraction = (target - distances[segment]) / (distances[segment + 1] - distances[segment])
        result.append(between(points[segment], points[segment + 1], fraction))
    result.append(points[-1])
    return tuple(result)


def between(point_a: Point, point_b: Point, fraction: float) -> Point:
    if fraction == 0.0:
        return point_a
    ele = None
    if point_a.ele is not None and point_b.ele is not None:
        ele = point_a.ele + (point_b.ele - point_a.ele) * fraction
    return Point(
        lat=point_a.lat + (point_b.lat - point_a.lat) * fraction,
        lon=point_a.lon + (point_b.lon - point_a.lon) * fraction,
        ele=ele,
    )
