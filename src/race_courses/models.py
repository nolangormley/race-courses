"""Value types that the pipeline stages share."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    lat: float
    lon: float
    ele: float | None = None


@dataclass(frozen=True)
class Line:
    name: str
    points: tuple[Point, ...]


@dataclass(frozen=True)
class Marker:
    name: str
    point: Point


@dataclass(frozen=True)
class Geometry:
    """All lines and named points that one source file holds."""

    lines: tuple[Line, ...] = ()
    markers: tuple[Marker, ...] = ()


@dataclass(frozen=True)
class SourceRef:
    """A course file or map that a race page links to or embeds."""

    kind: str
    url: str
    found_on: str
    label: str = ""


@dataclass(frozen=True)
class Course:
    """One continuous track for one event, in race order."""

    points: tuple[Point, ...]
    length_m: float
    method: str
    oriented_by: str
