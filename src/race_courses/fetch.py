"""Polite HTTP fetching for organizer sites: robots.txt, per-host delays, redirects and size caps."""

import codecs
import functools
import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from urllib.parse import urljoin, urlsplit

import httpx

from race_courses.settings import USER_AGENT

ROBOTS_TOKEN = "race-courses-bot"
MAX_REDIRECTS = 5
REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})


def make_client() -> httpx.Client:
    """Build the HTTP client that identifies this crawler and never follows redirects by itself."""
    return httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=30.0, follow_redirects=False)


@dataclass(frozen=True)
class Page:
    """One HTTP response, after redirects, with the body fully read."""

    url: str
    status: int
    content_type: str
    body: bytes
    charset: str | None = None

    @property
    def text(self) -> str:
        return self.body.decode(self.charset or "utf-8", errors="replace")


class FetchError(Exception):
    """A URL could not be fetched. Carries the URL and, when there was a response, its status."""

    def __init__(self, url: str, reason: str, status: int | None = None) -> None:
        super().__init__(f"{reason}: {url}")
        self.url = url
        self.status = status


class Blocked(FetchError):
    """robots.txt does not allow the URL."""

    def __init__(self, url: str) -> None:
        super().__init__(url, "disallowed by robots.txt")


@functools.lru_cache(maxsize=4096)
def rule_regex(pattern: str) -> re.Pattern[str]:
    """Turn a robots.txt path pattern into a regex: "*" matches anything, a final "$" anchors the end."""
    anchored = pattern.endswith("$")
    pieces = [re.escape(piece) for piece in pattern.removesuffix("$").split("*")]
    return re.compile(".*".join(pieces) + ("$" if anchored else ""))


@dataclass(frozen=True)
class RobotsRule:
    pattern: str
    allowed: bool

    def matches(self, path: str) -> bool:
        return rule_regex(self.pattern).match(path) is not None


class Robots:
    """The robots.txt rules of one origin that apply to this crawler, matched as RFC 9309 says."""

    def __init__(self, rules: tuple[RobotsRule, ...]) -> None:
        self.rules = rules

    @classmethod
    def parse(cls, text: str) -> "Robots":
        """Keep the rules of the groups for our product token, or else those of the "*" groups."""
        specific: list[RobotsRule] = []
        generic: list[RobotsRule] = []
        token_seen = False
        agents: list[str] = []
        in_agent_lines = False
        for raw_line in text.lstrip("﻿").splitlines():
            key, separator, value = raw_line.split("#", 1)[0].partition(":")
            if not separator:
                continue
            key = key.strip().lower()
            value = value.strip()
            if key == "user-agent":
                if not in_agent_lines:
                    agents = []
                in_agent_lines = True
                agents.append(value.split("/", 1)[0].strip().lower())
                token_seen = token_seen or ROBOTS_TOKEN in agents
                continue
            in_agent_lines = False
            if key in {"allow", "disallow"} and value:
                rule = RobotsRule(value, allowed=key == "allow")
                if ROBOTS_TOKEN in agents:
                    specific.append(rule)
                if "*" in agents:
                    generic.append(rule)
        return cls(tuple(specific if token_seen else generic))

    def allows(self, url: str) -> bool:
        """The longest matching rule wins; on a tie allow wins; no match means allowed."""
        parts = urlsplit(url)
        path = (parts.path or "/") + (f"?{parts.query}" if parts.query else "")
        best: RobotsRule | None = None
        for rule in self.rules:
            if not rule.matches(path):
                continue
            if (
                best is None
                or len(rule.pattern) > len(best.pattern)
                or (len(rule.pattern) == len(best.pattern) and rule.allowed)
            ):
                best = rule
        return best is None or best.allowed


ALLOW_ALL = Robots(())
DISALLOW_ALL = Robots((RobotsRule("/", allowed=False),))


def split_http_url(url: str) -> tuple[str, str]:
    """Return the origin and hostname of an http(s) URL, or raise FetchError."""
    try:
        parts = urlsplit(url)
        hostname = parts.hostname
        port = parts.port
    except ValueError as exc:
        raise FetchError(url, "malformed URL") from exc
    if parts.scheme not in {"http", "https"} or not hostname:
        raise FetchError(url, "not an http(s) URL")
    origin = f"{parts.scheme}://{hostname}" + (f":{port}" if port else "")
    return origin, hostname


class Fetcher:
    """Fetch pages while honouring robots.txt and a minimum delay between requests to one host."""

    def __init__(
        self,
        client: httpx.Client,
        min_delay_s: float = 2.0,
        max_bytes: int = 25_000_000,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.client = client
        self.min_delay_s = min_delay_s
        self.max_bytes = max_bytes
        self.clock = clock
        self.sleep = sleep
        self.robots_by_origin: dict[str, Robots] = {}
        self.last_request_by_host: dict[str, float] = {}

    def get(self, url: str) -> Page:
        """Fetch a URL, following up to MAX_REDIRECTS redirects. Only a 2xx response returns a Page."""
        page = self.follow(url, check_robots=True)
        if 200 <= page.status < 300:
            return page
        raise FetchError(page.url, f"HTTP {page.status}", page.status)

    def follow(self, url: str, check_robots: bool) -> Page:
        current = url
        redirects = 0
        while True:
            origin, host = split_http_url(current)
            if check_robots and not self.robots_for(origin).allows(current):
                raise Blocked(current)
            page, location = self.request(current, host)
            if location is None:
                return page
            redirects += 1
            if redirects > MAX_REDIRECTS:
                raise FetchError(current, f"more than {MAX_REDIRECTS} redirects")
            current = urljoin(current, location)

    def robots_for(self, origin: str) -> Robots:
        if origin not in self.robots_by_origin:
            self.robots_by_origin[origin] = self.load_robots(origin)
        return self.robots_by_origin[origin]

    def load_robots(self, origin: str) -> Robots:
        """RFC 9309: 4xx means no rules; 5xx, no answer or a redirect loop means nothing is allowed."""
        try:
            page = self.follow(f"{origin}/robots.txt", check_robots=False)
        except FetchError:
            return DISALLOW_ALL
        if 200 <= page.status < 300:
            return Robots.parse(page.text)
        if 400 <= page.status < 500:
            return ALLOW_ALL
        return DISALLOW_ALL

    def request(self, url: str, host: str) -> tuple[Page, str | None]:
        """One GET with the delay applied. Returns the page and the Location header of a redirect."""
        self.wait_turn(host)
        try:
            with self.client.stream("GET", url) as response:
                body = self.read_body(url, response)
                media_type = response.headers.get("content-type", "").split(";", 1)[0].strip().lower()
                charset = response.charset_encoding
                try:
                    codecs.lookup(charset or "utf-8")
                except LookupError:
                    charset = None
                page = Page(url, response.status_code, media_type, body, charset)
                location = response.headers.get("location") if page.status in REDIRECT_STATUSES else None
        except httpx.HTTPError as exc:
            raise FetchError(url, f"{type(exc).__name__}: {exc}") from exc
        finally:
            self.last_request_by_host[host] = self.clock()
        return page, location

    def wait_turn(self, host: str) -> None:
        last = self.last_request_by_host.get(host)
        if last is None:
            return
        remaining = self.min_delay_s - (self.clock() - last)
        if remaining > 0:
            self.sleep(remaining)

    def read_body(self, url: str, response: httpx.Response) -> bytes:
        """Stream the body and give up as soon as it is known to exceed max_bytes."""
        too_large = FetchError(url, f"body larger than {self.max_bytes} bytes", response.status_code)
        declared = response.headers.get("content-length", "")
        if declared.isdigit() and int(declared) > self.max_bytes:
            raise too_large
        chunks: list[bytes] = []
        size = 0
        for chunk in response.iter_bytes():
            size += len(chunk)
            if size > self.max_bytes:
                raise too_large
            chunks.append(chunk)
        return b"".join(chunks)
