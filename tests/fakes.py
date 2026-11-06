"""Fakes and file builders that the tests share."""

from race_courses.fetch import FetchError, Page
from race_courses.models import Point

METERS_PER_DEGREE = 111_195.0


def coordinates(length_m: float, lon: float = -80.0, lat: float = 40.0, steps: int = 60) -> str:
    """KML coordinates of a straight line to the north."""
    span = length_m / METERS_PER_DEGREE
    return " ".join(f"{lon},{lat + span * ii / steps},0" for ii in range(steps + 1))


def kml(*lines: tuple[str, str]) -> bytes:
    placemarks = "".join(
        f"<Placemark><name>{name}</name><LineString><coordinates>{points}</coordinates></LineString></Placemark>"
        for name, points in lines
    )
    return f'<?xml version="1.0"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document>{placemarks}</Document></kml>'.encode()


def html(body: str) -> bytes:
    return f"<!doctype html><html><body>{body}</body></html>".encode()


class FakeFetcher:
    def __init__(self, responses: dict[str, bytes | FetchError]):
        self.responses = responses
        self.media: dict[str, str] = {}
        self.calls: list[str] = []

    def get(self, url: str) -> Page:
        self.calls.append(url)
        response = self.responses.get(url, FetchError(url, "HTTP 404", status=404))
        if isinstance(response, FetchError):
            raise response
        media = "text/html" if response.startswith(b"<!doctype") else "application/octet-stream"
        return Page(url=url, status=200, content_type=self.media.get(url, media), body=response)


class FakeElevation:
    def __init__(self):
        self.calls = 0

    def profile(self, points):
        self.calls += 1
        return tuple(Point(point.lat, point.lon, 200.0 + ii % 7) for ii, point in enumerate(points))
