"""Tests for the polite fetcher: robots.txt, delays, redirects, size caps and decoding. No network."""

from collections.abc import Callable, Iterator

import httpx
import pytest

from race_courses.fetch import MAX_REDIRECTS, Blocked, FetchError, Fetcher, Page, Robots, make_client
from race_courses.settings import USER_AGENT

Route = tuple[int, dict[str, str], bytes | httpx.SyncByteStream]


class FakeWeb:
    """Serves canned responses by exact URL and records every request in order."""

    def __init__(self, routes: dict[str, Route | type[httpx.TransportError]]) -> None:
        self.routes = routes
        self.requests: list[str] = []
        self.on_request: Callable[[], None] = lambda: None

    def handle(self, request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        self.requests.append(url)
        self.on_request()
        route = self.routes.get(url, (404, {}, b"not found"))
        if isinstance(route, type):
            raise route("network down", request=request)
        status, headers, body = route
        if isinstance(body, httpx.SyncByteStream):
            return httpx.Response(status, headers=headers, stream=body)
        return httpx.Response(status, headers=headers, content=body)

    def client(self) -> httpx.Client:
        return httpx.Client(transport=httpx.MockTransport(self.handle), follow_redirects=False)


class FakeClock:
    def __init__(self) -> None:
        self.now = 100.0
        self.sleeps: list[float] = []

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


class CountingStream(httpx.SyncByteStream):
    """A chunked body that remembers how many chunks were actually consumed."""

    def __init__(self, chunk: bytes, count: int) -> None:
        self.chunk = chunk
        self.count = count
        self.served = 0

    def __iter__(self) -> Iterator[bytes]:
        for _unused in range(self.count):
            self.served += 1
            yield self.chunk


def robots(text: str) -> Route:
    return (200, {"content-type": "text/plain"}, text.encode())


def html(body: str = "<html>ok</html>") -> Route:
    return (200, {"content-type": "text/html; charset=utf-8"}, body.encode())


def redirect(location: str, status: int = 302) -> Route:
    return (status, {"location": location}, b"")


def make_fetcher(
    web: FakeWeb, clock: FakeClock | None = None, min_delay_s: float = 2.0, max_bytes: int = 25_000_000
) -> Fetcher:
    clock = clock or FakeClock()
    return Fetcher(web.client(), min_delay_s=min_delay_s, max_bytes=max_bytes, clock=clock, sleep=clock.sleep)


def test_make_client_identifies_the_crawler() -> None:
    client = make_client()
    assert client.headers["user-agent"] == USER_AGENT
    assert client.timeout == httpx.Timeout(30.0)
    assert client.follow_redirects is False


def test_page_text_uses_the_header_charset() -> None:
    page = Page("http://a.test/", 200, "text/html", "caf\xe9".encode("latin-1"), "iso-8859-1")
    assert page.text == "café"


def test_page_text_defaults_to_utf8_with_replacement() -> None:
    page = Page("http://a.test/", 200, "text/html", b"caf\xc3\xa9 \xff")
    assert page.text == "café �"


def test_get_returns_a_page_and_fetches_robots_once_per_origin() -> None:
    web = FakeWeb(
        {
            "http://a.test/robots.txt": robots("User-agent: *\nDisallow: /private/\n"),
            "http://a.test/page": html("<p>hello</p>"),
            "http://a.test/file.gpx": (200, {"content-type": "Application/GPX+XML; charset=ISO-8859-1"}, b"<gpx/>"),
        }
    )
    fetcher = make_fetcher(web)
    page = fetcher.get("http://a.test/page")
    assert page == Page("http://a.test/page", 200, "text/html", b"<p>hello</p>", "utf-8")
    file_page = fetcher.get("http://a.test/file.gpx")
    assert (file_page.content_type, file_page.charset) == ("application/gpx+xml", "iso-8859-1")
    assert web.requests == ["http://a.test/robots.txt", "http://a.test/page", "http://a.test/file.gpx"]


def test_unknown_header_charset_is_dropped() -> None:
    web = FakeWeb({"http://a.test/page": (200, {"content-type": "text/html; charset=bogus-9"}, b"caf\xc3\xa9")})
    page = make_fetcher(web).get("http://a.test/page")
    assert page.charset is None
    assert page.text == "café"


def test_robots_disallow_raises_blocked_before_any_request() -> None:
    web = FakeWeb({"http://a.test/robots.txt": robots("User-agent: *\nDisallow: /private/\n")})
    with pytest.raises(Blocked) as caught:
        make_fetcher(web).get("http://a.test/private/x")
    assert caught.value.url == "http://a.test/private/x"
    assert caught.value.status is None
    assert web.requests == ["http://a.test/robots.txt"]


def test_robots_group_for_our_token_replaces_the_wildcard_group() -> None:
    rules = Robots.parse("User-agent: *\nDisallow: /\n\nUser-agent: race-courses-bot\nDisallow: /secret/\n")
    assert rules.allows("http://a.test/page")
    assert not rules.allows("http://a.test/secret/x")
    assert Robots.parse("User-agent: *\nDisallow: /\n\nUser-agent: Race-Courses-Bot\n").allows("http://a.test/x")


def test_robots_longest_match_wins_like_google_maps() -> None:
    rules = Robots.parse("User-agent: *\nDisallow: /maps/\nAllow: /maps/d/\n")
    assert rules.allows("https://www.google.com/maps/d/kml?mid=1&forcekml=1")
    assert not rules.allows("https://www.google.com/maps/place/x")


def test_robots_wildcards_anchors_comments_and_bom() -> None:
    rules = Robots.parse(
        "﻿# exports\nUser-agent: *\nCrawl-delay: 5\nDisallow: /*.gpx* # raw\nDisallow: /end$\nDisallow:\n"
    )
    assert not rules.allows("https://a.test/routes/1.gpx")
    assert not rules.allows("https://a.test/routes/1.gpx?sub=1")
    assert not rules.allows("https://a.test/end")
    assert rules.allows("https://a.test/ending")
    assert rules.allows("https://a.test/routes/1")
    assert rules.allows("https://a.test/")


def test_robots_tie_between_allow_and_disallow_allows() -> None:
    rules = Robots.parse("User-agent: *\nDisallow: /a/\nAllow: /a/\n")
    assert rules.allows("https://a.test/a/x")


def test_robots_404_allows_everything() -> None:
    web = FakeWeb({"http://a.test/page": html()})
    assert make_fetcher(web).get("http://a.test/page").status == 200
    assert web.requests == ["http://a.test/robots.txt", "http://a.test/page"]


def test_robots_500_blocks_the_origin_for_the_run() -> None:
    web = FakeWeb({"http://a.test/robots.txt": (500, {}, b"oops"), "http://a.test/page": html()})
    fetcher = make_fetcher(web)
    with pytest.raises(Blocked):
        fetcher.get("http://a.test/page")
    with pytest.raises(Blocked):
        fetcher.get("http://a.test/other")
    assert web.requests == ["http://a.test/robots.txt"]


def test_robots_network_error_blocks_the_origin() -> None:
    web = FakeWeb({"http://a.test/robots.txt": httpx.ConnectError, "http://a.test/page": html()})
    with pytest.raises(Blocked):
        make_fetcher(web).get("http://a.test/page")
    assert web.requests == ["http://a.test/robots.txt"]


def test_robots_redirect_is_followed() -> None:
    web = FakeWeb(
        {
            "http://a.test/robots.txt": redirect("https://a.test/robots.txt", 301),
            "https://a.test/robots.txt": robots("User-agent: *\nDisallow: /private/\n"),
            "http://a.test/page": html(),
        }
    )
    fetcher = make_fetcher(web)
    assert fetcher.get("http://a.test/page").status == 200
    with pytest.raises(Blocked):
        fetcher.get("http://a.test/private/x")
    assert web.requests == ["http://a.test/robots.txt", "https://a.test/robots.txt", "http://a.test/page"]


def test_redirects_are_followed_to_the_final_url() -> None:
    web = FakeWeb({"http://a.test/old": redirect("/new", 301), "http://a.test/new": html("<p>new</p>")})
    page = make_fetcher(web).get("http://a.test/old")
    assert page.url == "http://a.test/new"
    assert page.body == b"<p>new</p>"
    assert web.requests == ["http://a.test/robots.txt", "http://a.test/old", "http://a.test/new"]


def test_cross_host_redirect_checks_the_target_robots() -> None:
    web = FakeWeb(
        {
            "http://a.test/go": redirect("http://b.test/landing"),
            "http://b.test/robots.txt": robots("User-agent: *\nDisallow: /landing\n"),
            "http://b.test/landing": html(),
        }
    )
    with pytest.raises(Blocked) as caught:
        make_fetcher(web).get("http://a.test/go")
    assert caught.value.url == "http://b.test/landing"
    assert web.requests == ["http://a.test/robots.txt", "http://a.test/go", "http://b.test/robots.txt"]


def test_cross_host_redirect_to_an_allowed_page_returns_it() -> None:
    web = FakeWeb({"http://a.test/go": redirect("http://b.test/landing"), "http://b.test/landing": html()})
    page = make_fetcher(web).get("http://a.test/go")
    assert page.url == "http://b.test/landing"


def test_redirect_loop_raises_after_max_redirects() -> None:
    web = FakeWeb({"http://a.test/loop": redirect("/loop")})
    with pytest.raises(FetchError, match="redirects"):
        make_fetcher(web).get("http://a.test/loop")
    assert web.requests.count("http://a.test/loop") == MAX_REDIRECTS + 1


@pytest.mark.parametrize("status", [304, 404, 500])
def test_non_2xx_raises_fetch_error_with_the_status(status: int) -> None:
    web = FakeWeb({"http://a.test/page": (status, {}, b"")})
    with pytest.raises(FetchError) as caught:
        make_fetcher(web).get("http://a.test/page")
    assert caught.value.status == status
    assert caught.value.url == "http://a.test/page"


def test_network_error_raises_fetch_error_without_status() -> None:
    web = FakeWeb({"http://a.test/robots.txt": robots(""), "http://a.test/page": httpx.ReadTimeout})
    with pytest.raises(FetchError, match="ReadTimeout") as caught:
        make_fetcher(web).get("http://a.test/page")
    assert caught.value.status is None


@pytest.mark.parametrize("url", ["mailto:info@a.test", "ftp://a.test/course.gpx", "/relative", "http://[bad"])
def test_non_http_urls_raise_fetch_error(url: str) -> None:
    web = FakeWeb({})
    with pytest.raises(FetchError):
        make_fetcher(web).get(url)
    assert web.requests == []


def test_redirect_to_a_non_http_url_raises_fetch_error() -> None:
    web = FakeWeb({"http://a.test/go": redirect("ftp://a.test/file")})
    with pytest.raises(FetchError, match="not an http"):
        make_fetcher(web).get("http://a.test/go")


def test_declared_content_length_over_max_bytes_is_refused() -> None:
    web = FakeWeb({"http://a.test/big": (200, {}, b"x" * 100)})
    with pytest.raises(FetchError, match="larger than") as caught:
        make_fetcher(web, max_bytes=99).get("http://a.test/big")
    assert caught.value.status == 200


def test_streamed_body_over_max_bytes_stops_reading_early() -> None:
    stream = CountingStream(b"x" * 1000, count=100)
    web = FakeWeb({"http://a.test/big": (200, {}, stream)})
    with pytest.raises(FetchError, match="larger than"):
        make_fetcher(web, max_bytes=5000).get("http://a.test/big")
    assert 5 < stream.served < 100


def test_body_exactly_at_max_bytes_is_accepted() -> None:
    web = FakeWeb({"http://a.test/ok": (200, {}, b"x" * 100)})
    assert make_fetcher(web, max_bytes=100).get("http://a.test/ok").body == b"x" * 100


def test_requests_to_one_host_wait_for_the_minimum_delay() -> None:
    web = FakeWeb({"http://a.test/page": html(), "http://a.test/other": html(), "http://b.test/page": html()})
    clock = FakeClock()
    fetcher = make_fetcher(web, clock, min_delay_s=2.0)
    fetcher.get("http://a.test/page")
    assert clock.sleeps == [2.0]
    fetcher.get("http://a.test/other")
    assert clock.sleeps == [2.0, 2.0]
    fetcher.get("http://b.test/page")
    assert clock.sleeps == [2.0, 2.0, 2.0]
    clock.now += 10
    fetcher.get("http://a.test/page")
    assert clock.sleeps == [2.0, 2.0, 2.0]


def test_delay_counts_from_the_end_of_the_previous_request() -> None:
    web = FakeWeb({"http://a.test/robots.txt": robots(""), "http://a.test/page": html()})
    clock = FakeClock()

    def slow_server() -> None:
        clock.now += 1.5

    web.on_request = slow_server
    make_fetcher(web, clock, min_delay_s=2.0).get("http://a.test/page")
    assert clock.sleeps == [2.0]
