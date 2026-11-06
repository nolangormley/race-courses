import math
import random

import pytest

from race_courses.geometry import EARTH_RADIUS_M, assemble, cumulative_m, haversine_m, named_distances, resample
from race_courses.models import Geometry, Line, Marker, Point

ORIGIN_LAT, ORIGIN_LON = 40.44, -80.0
DEG_PER_M = math.degrees(1 / EARTH_RADIUS_M)


def point_at(east_m: float, north_m: float = 0.0, ele: float | None = None) -> Point:
    return Point(
        lat=ORIGIN_LAT + north_m * DEG_PER_M,
        lon=ORIGIN_LON + east_m * DEG_PER_M / math.cos(math.radians(ORIGIN_LAT)),
        ele=ele,
    )


def east_line(name: str, start_m: float, end_m: float, step_m: float = 50.0, north_m: float = 0.0) -> Line:
    steps = round(abs(end_m - start_m) / step_m)
    direction = 1 if end_m >= start_m else -1
    points = [point_at(start_m + direction * ii * step_m, north_m) for ii in range(steps + 1)]
    return Line(name=name, points=tuple(points))


def east_of(point: Point) -> float:
    return (point.lon - ORIGIN_LON) * math.cos(math.radians(ORIGIN_LAT)) / DEG_PER_M


def test_haversine_matches_one_degree_of_latitude():
    assert haversine_m(Point(40.0, -80.0), Point(41.0, -80.0)) == pytest.approx(111_195, rel=1e-3)


def test_cumulative_is_a_running_total():
    points = [point_at(0, 0), point_at(300, 0), point_at(300, 400)]
    assert cumulative_m(points) == pytest.approx([0, 300, 700], abs=0.5)
    assert cumulative_m([]) == []


def test_one_clean_line_is_the_course():
    line = east_line("course", 0, 5000)
    course = assemble(Geometry(lines=(line,)), 5000)
    assert course is not None
    assert course.method == "line"
    assert course.oriented_by == "as-drawn"
    assert course.points == line.points
    assert course.length_m == pytest.approx(5000, abs=1)


def test_split_course_is_chained_and_pieces_flipped():
    pieces = (
        east_line("leg 1", 0, 2000),
        east_line("leg 2", 4000, 2000),
        east_line("leg 3", 4050, 6000),
    )
    course = assemble(Geometry(lines=pieces), 6000)
    assert course is not None
    assert course.method == "chain:3/3"
    assert course.length_m == pytest.approx(6000, abs=1)
    easts = [east_of(point) for point in course.points]
    assert easts == sorted(easts)
    assert easts[0] == pytest.approx(0, abs=0.1)
    assert easts[-1] == pytest.approx(6000, abs=0.1)


def test_multi_course_map_picks_the_length_closest_to_target():
    short = east_line("short course", 0, 10_000, north_m=0)
    long = east_line("long course", 0, 20_000, north_m=30)
    geometry = Geometry(lines=(short, long))
    assert assemble(geometry, 21_000).points == long.points
    assert assemble(geometry, 10_200).points == short.points
    assert assemble(geometry, 21_000).method == "line"


def test_same_line_drawn_twice_counts_once():
    line = east_line("course", 0, 5000)
    copy = Line(name="course copy", points=line.points)
    geometry = Geometry(lines=(line, copy))
    course = assemble(geometry, 5000)
    assert course is not None
    assert course.method == "line"
    assert assemble(geometry, 10_000) is None


def test_consecutive_duplicate_points_are_dropped():
    points = (point_at(0), point_at(0), point_at(100), point_at(100), point_at(100), point_at(200))
    course = assemble(Geometry(lines=(Line("dup", points),)), 200)
    assert course is not None
    assert len(course.points) == 3
    assert course.length_m == pytest.approx(200, abs=0.5)


def test_isolated_spike_is_removed():
    clean = east_line("course", 0, 1000)
    with_spike = clean.points[:11] + (point_at(500, 800),) + clean.points[11:]
    course = assemble(Geometry(lines=(Line("spiky", with_spike),)), 1000)
    assert course is not None
    assert course.points == clean.points
    assert course.length_m == pytest.approx(1000, abs=1)


def test_hairpin_turn_is_not_a_spike():
    points = (point_at(0, 0), point_at(100, 0), point_at(0, 15))
    course = assemble(Geometry(lines=(Line("hairpin", points),)), 200)
    assert course is not None
    assert len(course.points) == 3


def test_start_marker_reverses_a_backwards_line():
    line = east_line("course", 5000, 0)
    markers = (Marker("Marathon Start", point_at(0, 10)),)
    course = assemble(Geometry(lines=(line,), markers=markers), 5000)
    assert course is not None
    assert course.oriented_by == "markers"
    assert course.points == line.points[::-1]


def test_finish_marker_alone_orients():
    line = east_line("course", 0, 5000)
    markers = (Marker("FINISH LINE", point_at(-20, 0)),)
    course = assemble(Geometry(lines=(line,), markers=markers), 5000)
    assert course is not None
    assert course.oriented_by == "markers"
    assert east_of(course.points[-1]) == pytest.approx(0, abs=0.1)


def test_start_finish_marker_keeps_a_correct_line():
    line = east_line("course", 0, 5000)
    markers = (Marker("Start/Finish", point_at(5, 5)),)
    course = assemble(Geometry(lines=(line,), markers=markers), 5000)
    assert course is not None
    assert course.oriented_by == "markers"
    assert course.points == line.points


def test_start_marker_of_another_event_is_ignored():
    line = east_line("10K", 10_000, 0)
    markers = (Marker("5K Start", point_at(3000, 0)), Marker("10K Start", point_at(0, 30)))
    course = assemble(Geometry(lines=(line,), markers=markers), 10_000)
    assert course is not None
    assert course.oriented_by == "markers"
    assert east_of(course.points[0]) == pytest.approx(0, abs=0.1)


def test_marker_far_from_both_ends_is_ignored():
    line = east_line("course", 5000, 0)
    markers = (Marker("Start", point_at(2500, 5000)),)
    course = assemble(Geometry(lines=(line,), markers=markers), 5000)
    assert course is not None
    assert course.oriented_by == "as-drawn"
    assert course.points == line.points


def test_no_candidate_within_25_percent_gives_none():
    geometry = Geometry(lines=(east_line("course", 0, 5000),))
    assert assemble(geometry, 7000) is None
    assert assemble(geometry, 3900) is None
    assert assemble(geometry, 6000) is not None
    assert assemble(Geometry(), 5000) is None


def test_hundreds_of_tiny_segments_chain_in_order():
    rng = random.Random(7)
    pieces = [east_line(f"piece {ii}", ii * 100, (ii + 1) * 100) for ii in range(300)]
    rng.shuffle(pieces)
    pieces = [
        Line(piece.name, piece.points[::-1]) if rng.random() < 0.5 else piece for piece in pieces
    ]
    markers = (Marker("Start Line", point_at(0, 8)),)
    course = assemble(Geometry(lines=tuple(pieces), markers=markers), 30_000)
    assert course is not None
    assert course.method == "chain:300/300"
    assert course.oriented_by == "markers"
    assert course.length_m == pytest.approx(30_000, abs=5)
    easts = [east_of(point) for point in course.points]
    assert easts == sorted(easts)
    assert len(course.points) == 601


def test_resample_spacing_and_endpoints():
    points = (point_at(0), point_at(105))
    resampled = resample(points, 20)
    assert resampled[0] == points[0]
    assert resampled[-1] == points[-1]
    assert cumulative_m(resampled) == pytest.approx([0, 20, 40, 60, 80, 100, 105], abs=0.01)


def test_resample_interpolates_elevation():
    points = (point_at(0, ele=100.0), point_at(50, ele=120.0), point_at(100, ele=200.0))
    eles = [point.ele for point in resample(points, 25)]
    assert eles == pytest.approx([100, 110, 120, 160, 200], abs=0.01)


def test_resample_keeps_missing_elevation_missing():
    points = (point_at(0, ele=100.0), point_at(40))
    assert [point.ele for point in resample(points, 20)] == [100.0, None, None]


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("2025 14k", [14000.0]),
        ("5K Route - 7:30am Start", [5000.0]),
        ("Half Turnaround at 12th St", [21097.5]),
        ("Half Marathon Fly-Over Tour", [21097.5]),
        ("Marathon Course (26.2 mi)", [42195.0, pytest.approx(42164.8, abs=0.1)]),
        ("10 Miler", [pytest.approx(16093.4, abs=0.1)]),
        ("Bike Path Mile 6 to Surf Dr. Mile 8.5", []),
        ("Line 30", []),
    ],
)
def test_named_distances(name, expected):
    assert named_distances(name) == expected


def test_lines_named_for_other_distances_are_not_chained():
    # Two loops from one start make 21 km together, but they are the 14K and 7K courses.
    fourteen = east_line("2025 14k", 0, 14_000, step_m=100)
    seven = east_line("2025 7k", 14_000, 21_000, step_m=100)
    assert assemble(Geometry(lines=(fourteen, seven)), 21_097) is None
    assert assemble(Geometry(lines=(fourteen, seven)), 14_000).method == "line"


def test_unnamed_pieces_still_chain():
    pieces = (east_line("Line 1", 0, 10_000, step_m=100), east_line("Line 2", 10_000, 21_100, step_m=100))
    assert assemble(Geometry(lines=pieces), 21_097).method == "chain:2/2"
