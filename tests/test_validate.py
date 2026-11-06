import math

import pytest

from race_courses.geometry import EARTH_RADIUS_M, cumulative_m
from race_courses.models import Course, Point
from race_courses.validate import check

ORIGIN_LAT, ORIGIN_LON = 40.44, -80.0
DEG_PER_M = math.degrees(1 / EARTH_RADIUS_M)


def point_at(east_m: float, north_m: float = 0.0) -> Point:
    return Point(
        lat=ORIGIN_LAT + north_m * DEG_PER_M,
        lon=ORIGIN_LON + east_m * DEG_PER_M / math.cos(math.radians(ORIGIN_LAT)),
    )


def course_of(points: tuple[Point, ...]) -> Course:
    return Course(points=points, length_m=cumulative_m(points)[-1], method="line", oriented_by="as-drawn")


def straight_course(length_m: float, step_m: float = 100.0) -> Course:
    steps = round(length_m / step_m)
    return course_of(tuple(point_at(ii * step_m) for ii in range(steps + 1)))


def test_length_within_three_percent_is_ok():
    verdict = check(straight_course(10_200), 10_000)
    assert verdict.status == "ok"
    assert verdict.notes == ()
    assert verdict.length_error_pct == pytest.approx(2.0, abs=0.01)


def test_length_within_eight_percent_warns():
    verdict = check(straight_course(9_500), 10_000)
    assert verdict.status == "warn"
    assert verdict.length_error_pct == pytest.approx(-5.0, abs=0.01)
    assert "length" in verdict.notes[0]


def test_length_beyond_eight_percent_rejects():
    verdict = check(straight_course(11_000), 10_000)
    assert verdict.status == "reject"
    assert verdict.length_error_pct == pytest.approx(10.0, abs=0.01)


def test_length_thresholds_are_inclusive():
    assert check(straight_course(10_300), 10_000).status == "ok"
    assert check(straight_course(10_800), 10_000).status == "warn"


def test_point_outside_the_us_rejects():
    course = course_of((Point(19.43, -99.13), Point(19.44, -99.13)))
    verdict = check(course, course.length_m)
    assert verdict.status == "reject"
    assert "outside the US" in verdict.notes[0]


@pytest.mark.parametrize(
    "point",
    [Point(40.44, -80.0), Point(61.2, -149.9), Point(21.3, -157.8), Point(18.4, -66.1)],
    ids=["pittsburgh", "anchorage", "honolulu", "san juan"],
)
def test_points_in_every_us_region_pass(point: Point):
    course = course_of((point, Point(point.lat + 0.001, point.lon)))
    assert check(course, course.length_m).status == "ok"


def test_long_straight_segment_is_noted_without_changing_the_status():
    points = (point_at(0), point_at(2000), point_at(2100), point_at(2200))
    verdict = check(course_of(points), 2200)
    assert verdict.status == "ok"
    assert verdict.notes == ("1 straight segment(s) over 1.5 km, longest 2.0 km at km 0.0",)


def test_segment_at_the_shortcut_limit_has_no_note():
    points = (point_at(0), point_at(1500), point_at(1600))
    assert check(course_of(points), 1600).notes == ()


def test_reject_outranks_shortcut_warning():
    points = (point_at(0), point_at(2000), point_at(2100))
    verdict = check(course_of(points), 1000)
    assert verdict.status == "reject"
    assert len(verdict.notes) == 2


@pytest.mark.parametrize(
    ("method", "status", "note"),
    [
        ("chain:3/3", "ok", "joined from 3 of 3 pieces of the map"),
        ("chain:262/264", "ok", "joined from 262 of 264 pieces of the map"),
        ("chain:5/12", "warn", "joined from 5 of 12 pieces of the map; check that it is the right course"),
    ],
)
def test_chained_course_gets_a_note(method, status, note):
    points = (point_at(0), point_at(1000), point_at(2000))
    course = Course(points=points, length_m=cumulative_m(points)[-1], method=method, oriented_by="as-drawn")
    verdict = check(course, 2000)
    assert verdict.status == status
    assert verdict.notes == (note,)
