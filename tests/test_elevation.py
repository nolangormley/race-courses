import json
import math
from collections.abc import Callable, Sequence
from pathlib import Path
from urllib.parse import parse_qs

import httpx
import pytest

from race_courses.elevation import Elevation, gain_loss, structure_mask
from race_courses.geometry import EARTH_RADIUS_M, resample
from race_courses.models import Point

FIXTURES = Path(__file__).parent / "fixtures" / "shape"
ORIGIN_LAT, ORIGIN_LON = 40.44, -80.0
DEG_PER_M = math.degrees(1 / EARTH_RADIUS_M)
THREE_DEP_HOST = "elevation.nationalmap.gov"
OVERPASS_HOST = "overpass-api.de"

Dem = Callable[[float, float], str]


def point_at(east_m: float, north_m: float = 0.0) -> Point:
    return Point(
        lat=ORIGIN_LAT + north_m * DEG_PER_M,
        lon=ORIGIN_LON + east_m * DEG_PER_M / math.cos(math.radians(ORIGIN_LAT)),
    )


def east_of(lon: float) -> float:
    return (lon - ORIGIN_LON) * math.cos(math.radians(ORIGIN_LAT)) / DEG_PER_M


def east_points(start_m: float, end_m: float, step_m: float = 20.0) -> tuple[Point, ...]:
    return tuple(point_at(start_m + ii * step_m) for ii in range(round((end_m - start_m) / step_m) + 1))


def way(*points: Point, **tags: str) -> dict:
    return {
        "type": "way",
        "id": 1,
        "tags": {"highway": "primary", **tags},
        "geometry": [{"lat": point.lat, "lon": point.lon} for point in points],
    }


def slope(east_m: float) -> float:
    return 300 + east_m / 100


def slope_dem(lon: float, lat: float) -> str:
    return f"{slope(east_of(lon)):.6f}"


def river_dem(lon: float, lat: float) -> str:
    """A bare-earth model with a river valley 30 m deep between east 200 and 400."""
    east = east_of(lon)
    dip = 30 if 200 < east < 400 else 0
    return f"{slope(east) - dip:.6f}"


def hill_dem(lon: float, lat: float) -> str:
    east = east_of(lon)
    rise = 50 if 200 < east < 400 else 0
    return f"{slope(east) + rise:.6f}"


def pothole_dem(lon: float, lat: float) -> str:
    east = east_of(lon)
    return "250" if abs(east - 300) < 1 else f"{slope(east):.6f}"


def sloped(count: int) -> list[float]:
    return [round(slope(ii * 20), 1) for ii in range(count)]


class FakeApis:
    """MockTransport handler that plays 3DEP and Overpass and records what happened."""

    def __init__(
        self,
        dem: Dem,
        ways: Sequence[dict] = (),
        dem_outcomes: Sequence[int | Exception] = (),
        overpass_responses: Sequence[httpx.Response] = (),
    ):
        self.dem = dem
        self.ways = list(ways)
        self.dem_outcomes = list(dem_outcomes)
        self.overpass_responses = list(overpass_responses)
        self.requests: list[httpx.Request] = []
        self.batch_sizes: list[int] = []
        self.sleeps: list[float] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        assert request.headers["User-Agent"].startswith("race-courses-bot")
        if request.url.host == THREE_DEP_HOST:
            return self.three_dep(request)
        assert request.url.host == OVERPASS_HOST
        return self.overpass(request)

    def three_dep(self, request: httpx.Request) -> httpx.Response:
        if self.dem_outcomes:
            outcome = self.dem_outcomes.pop(0)
            if isinstance(outcome, Exception):
                raise outcome
            return httpx.Response(outcome)
        form = parse_qs(request.content.decode())
        assert form["geometryType"] == ["esriGeometryMultipoint"]
        assert form["returnFirstValueOnly"] == ["true"]
        assert form["f"] == ["json"]
        coordinates = json.loads(form["geometry"][0])["points"]
        self.batch_sizes.append(len(coordinates))
        samples = [
            {"locationId": ii, "value": self.dem(lon, lat), "rasterId": 1, "resolution": 1}
            for ii, (lon, lat) in enumerate(coordinates)
        ]
        return httpx.Response(200, json={"samples": samples[::-1]})

    def overpass(self, request: httpx.Request) -> httpx.Response:
        if self.overpass_responses:
            return self.overpass_responses.pop(0)
        query = parse_qs(request.content.decode())["data"][0]
        assert query.startswith("[out:json][timeout:60];")
        assert 'way["highway"]["bridge"]["bridge"!="no"]' in query
        assert 'way["highway"]["tunnel"]["tunnel"!="no"]' in query
        return httpx.Response(200, json={"version": 0.6, "elements": self.ways})

    def hosts(self) -> list[str]:
        return [request.url.host for request in self.requests]


def elevation_for(fake: FakeApis, **kwargs) -> Elevation:
    client = httpx.Client(transport=httpx.MockTransport(fake))
    return Elevation(client, sleep=fake.sleeps.append, **kwargs)


def eles(points: tuple[Point, ...]) -> list[float]:
    return [point.ele for point in points]


def test_profile_fills_and_rounds_elevation():
    fake = FakeApis(slope_dem)
    points = east_points(0, 200)
    profiled = elevation_for(fake).profile(points)
    assert [(point.lat, point.lon) for point in profiled] == [(point.lat, point.lon) for point in points]
    assert eles(profiled) == pytest.approx(sloped(11), abs=1e-9)
    assert fake.sleeps == []
    assert fake.hosts() == [THREE_DEP_HOST, OVERPASS_HOST]


def test_nodata_is_interpolated_along_distance_and_held_at_the_ends():
    def gappy_dem(lon: float, lat: float) -> str:
        east = east_of(lon)
        return "NoData" if east < 10 or 30 < east < 130 else slope_dem(lon, lat)

    profiled = elevation_for(FakeApis(gappy_dem)).profile(east_points(0, 200))
    assert eles(profiled) == pytest.approx([300.2, *sloped(11)[1:]], abs=1e-9)


def test_all_nodata_raises():
    elevation = elevation_for(FakeApis(lambda lon, lat: "NoData"))
    with pytest.raises(ValueError, match="no elevation"):
        elevation.profile(east_points(0, 100))


def test_requests_are_batched_and_samples_matched_by_id():
    fake = FakeApis(slope_dem)
    profiled = elevation_for(fake, batch=5).profile(east_points(0, 220))
    assert fake.batch_sizes == [5, 5, 2]
    assert eles(profiled) == pytest.approx(sloped(12), abs=1e-9)


def test_server_errors_are_retried_with_backoff():
    fake = FakeApis(slope_dem, dem_outcomes=[503, 502])
    profiled = elevation_for(fake).profile(east_points(0, 40))
    assert fake.sleeps == [1.0, 2.0]
    assert eles(profiled) == pytest.approx(sloped(3), abs=1e-9)


def test_timeouts_are_retried():
    fake = FakeApis(slope_dem, dem_outcomes=[httpx.ReadTimeout("slow"), httpx.ConnectTimeout("slow")])
    assert eles(elevation_for(fake).profile(east_points(0, 20))) == pytest.approx(sloped(2), abs=1e-9)
    assert fake.sleeps == [1.0, 2.0]


def test_gives_up_after_three_retries():
    fake = FakeApis(slope_dem, dem_outcomes=[503, 503, 503, 503])
    with pytest.raises(httpx.HTTPStatusError):
        elevation_for(fake).profile(east_points(0, 20))
    assert fake.sleeps == [1.0, 2.0, 4.0]


def test_client_errors_are_not_retried():
    fake = FakeApis(slope_dem, dem_outcomes=[400])
    with pytest.raises(httpx.HTTPStatusError):
        elevation_for(fake).profile(east_points(0, 20))
    assert fake.sleeps == []


def test_truncated_sample_list_raises():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"samples": [{"locationId": 0, "value": "300"}]})

    elevation = Elevation(httpx.Client(transport=httpx.MockTransport(handler)))
    with pytest.raises(ValueError, match="1 samples for 2 points"):
        elevation.profile(east_points(0, 20))


def test_overpass_rate_limit_honours_retry_after():
    responses = [httpx.Response(429, headers={"Retry-After": "7"}), httpx.Response(504)]
    fake = FakeApis(slope_dem, overpass_responses=responses)
    elevation_for(fake).profile(east_points(0, 40))
    assert fake.sleeps == [7.0, 2.0]
    assert fake.hosts().count(OVERPASS_HOST) == 3


def test_overpass_runtime_error_raises():
    remark = 'runtime error: Query timed out in "query" at line 1 after 60 seconds.'
    responses = [httpx.Response(200, json={"elements": [], "remark": remark})]
    elevation = elevation_for(FakeApis(slope_dem, overpass_responses=responses))
    with pytest.raises(ValueError, match="Overpass"):
        elevation.profile(east_points(0, 40))


def test_bridge_crossing_is_levelled():
    course = east_points(0, 600)
    bare_eles = eles(elevation_for(FakeApis(river_dem)).profile(course))
    assert bare_eles[15] == pytest.approx(273.0, abs=1e-9)
    assert min(bare_eles) < 275

    bridge = way(point_at(190), point_at(410), bridge="yes", layer="1")
    fixed_eles = eles(elevation_for(FakeApis(river_dem, ways=[bridge])).profile(course))
    assert fixed_eles == pytest.approx(sloped(31), abs=1e-9)


def test_road_under_a_bridge_keeps_ground_elevation():
    course = east_points(0, 600)
    overpass = way(point_at(300, -100), point_at(300, 100), bridge="yes", layer="1")
    profiled = eles(elevation_for(FakeApis(river_dem, ways=[overpass])).profile(course))
    assert profiled[15] == pytest.approx(273.0, abs=1e-9)
    expected = [round(float(river_dem(point.lon, point.lat)), 1) for point in course]
    assert profiled == pytest.approx(expected, abs=1e-9)


def test_tunnel_is_levelled():
    course = east_points(0, 600)
    tunnel = way(point_at(190), point_at(410), tunnel="yes", layer="-1")
    profiled = elevation_for(FakeApis(hill_dem, ways=[tunnel])).profile(course)
    assert eles(profiled) == pytest.approx(sloped(31), abs=1e-9)


@pytest.mark.parametrize(("angle_deg", "levelled"), [(30, True), (45, False)], ids=["aligned", "crossing"])
def test_heading_decides_whether_a_point_is_on_the_structure(angle_deg: float, levelled: bool):
    course = east_points(0, 600)
    run_x, run_y = 100 * math.cos(math.radians(angle_deg)), 100 * math.sin(math.radians(angle_deg))
    skewed = way(point_at(300 - run_x, -run_y), point_at(300 + run_x, run_y), bridge="yes")
    profiled = eles(elevation_for(FakeApis(pothole_dem, ways=[skewed])).profile(course))
    assert profiled[15] == pytest.approx(303.0 if levelled else 250.0, abs=1e-9)


def test_structure_at_the_start_holds_the_first_ground_value():
    def cliff_dem(lon: float, lat: float) -> str:
        return "250" if east_of(lon) < 110 else slope_dem(lon, lat)

    course = east_points(0, 200)
    bridge = way(point_at(-10), point_at(110), bridge="yes")
    profiled = eles(elevation_for(FakeApis(cliff_dem, ways=[bridge])).profile(course))
    # The point at east 120 is 10 m past the bridge end, so it counts as on it too.
    assert profiled[:9] == pytest.approx([301.4] * 8 + [301.6], abs=1e-9)


def test_real_3dep_response_shape():
    body = json.loads((FIXTURES / "3dep_samples.json").read_text())

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == THREE_DEP_HOST:
            return httpx.Response(200, json=body)
        return httpx.Response(200, json={"elements": []})

    points = [Point(sample["location"]["y"], sample["location"]["x"]) for sample in body["samples"]]
    profiled = Elevation(httpx.Client(transport=httpx.MockTransport(handler))).profile(points)
    assert eles(profiled) == [299.2, 288.4, 277.1]


def test_real_overpass_response_marks_the_clemente_bridge_deck():
    body = json.loads((FIXTURES / "overpass_clemente.json").read_text())
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=body))
    elevation = Elevation(httpx.Client(transport=transport))
    deck = [element for element in body["elements"] if element["id"] == 11713124][0]["geometry"]
    south, north = Point(deck[0]["lat"], deck[0]["lon"]), Point(deck[-1]["lat"], deck[-1]["lon"])
    dlat, dlon = north.lat - south.lat, north.lon - south.lon
    approach_south = Point(south.lat - dlat / 3, south.lon - dlon / 3)
    approach_north = Point(north.lat + dlat / 3, north.lon + dlon / 3)
    course = resample((approach_south, south, north, approach_north), 20)

    segments = elevation.structures(course)
    assert len(segments) == 2 + 9 + 6
    mask = structure_mask(course, segments)
    on_deck = [ii for ii, flagged in enumerate(mask) if flagged]
    assert on_deck == list(range(on_deck[0], on_deck[-1] + 1))
    assert 13 <= len(on_deck) <= 17
    assert on_deck[0] >= 4 and on_deck[-1] <= len(mask) - 5


def test_gain_loss_ignores_noise_below_the_threshold():
    points = [Point(0, 0, ele) for ele in (100, 100.4, 100, 100.6, 100.1, 100.7, 100.2)]
    assert gain_loss(points) == (0.0, 0.0)


def test_gain_loss_counts_real_climbs_and_descents():
    points = [Point(0, 0, ele) for ele in (100, 105, 103, 110, 108)]
    assert gain_loss(points) == pytest.approx((12.0, 4.0))


def test_gain_loss_accumulates_a_slow_climb():
    points = [Point(0, 0, 100 + 0.3 * ii) for ii in range(41)]
    gain, loss = gain_loss(points)
    assert gain == pytest.approx(12.0, abs=0.5)
    assert loss == 0.0
