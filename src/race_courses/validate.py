"""Judge whether an assembled course is believable before it is published."""

from dataclasses import dataclass

from race_courses.geometry import cumulative_m
from race_courses.models import Course, Point

OK_PCT = 3.0
WARN_PCT = 8.0
SHORTCUT_M = 1500.0
CHAIN_SHARE = 0.9
RANK = {"ok": 0, "warn": 1, "reject": 2}
US_BOXES = {
    "CONUS": (24.4, -125.0, 49.4, -66.9),
    "Alaska": (51.2, -179.2, 71.5, -129.9),
    "Hawaii": (18.9, -160.3, 22.3, -154.7),
    "Puerto Rico": (17.8, -67.4, 18.6, -65.2),
}


@dataclass(frozen=True)
class Verdict:
    status: str
    notes: tuple[str, ...]
    length_error_pct: float


def check(course: Course, target_m: float) -> Verdict:
    """Compare the course against its advertised distance and basic plausibility rules."""
    status = "ok"
    notes: list[str] = []
    length_error_pct = (course.length_m - target_m) / target_m * 100
    if abs(length_error_pct) > OK_PCT:
        status = "warn" if abs(length_error_pct) <= WARN_PCT else "reject"
        notes.append(f"length {course.length_m / 1000:.2f} km is {length_error_pct:+.1f}% off target")
    outside = next((point for point in course.points if not in_us(point)), None)
    if outside is not None:
        status = "reject"
        notes.append(f"point outside the US at {outside.lat:.4f},{outside.lon:.4f}")
    distances = cumulative_m(course.points)
    shortcuts = [
        (distances[ii] - distances[ii - 1], distances[ii - 1])
        for ii in range(1, len(distances))
        if distances[ii] - distances[ii - 1] > SHORTCUT_M
    ]
    # A long straight segment can be a straight road; the length check catches real shortcuts.
    if shortcuts:
        longest, at_m = max(shortcuts)
        notes.append(
            f"{len(shortcuts)} straight segment(s) over {SHORTCUT_M / 1000:.1f} km, "
            f"longest {longest / 1000:.1f} km at km {at_m / 1000:.1f}"
        )
    if course.method.startswith("chain:"):
        used, available = course.method.removeprefix("chain:").split("/")
        if int(used) >= CHAIN_SHARE * int(available):
            notes.append(f"joined from {used} of {available} pieces of the map")
        else:
            # Pieces chosen from a larger map can come from more than one course.
            status = max(status, "warn", key=RANK.get)
            notes.append(f"joined from {used} of {available} pieces of the map; check that it is the right course")
    return Verdict(status=status, notes=tuple(notes), length_error_pct=length_error_pct)


def in_us(point: Point) -> bool:
    return any(
        south <= point.lat <= north and west <= point.lon <= east
        for south, west, north, east in US_BOXES.values()
    )
