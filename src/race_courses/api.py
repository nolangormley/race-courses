"""Form POSTs to the public APIs (USGS 3DEP and Overpass), with retries."""

from collections.abc import Callable, Container

import httpx

from race_courses.settings import USER_AGENT

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
HEADERS = {"User-Agent": USER_AGENT}
RETRIES = 3


def post(
    client: httpx.Client,
    url: str,
    form: dict[str, str],
    retry_statuses: Container[int],
    timeout: float,
    sleep: Callable[[float], None],
) -> httpx.Response:
    """POST a form, retrying timeouts and the given statuses up to RETRIES times."""
    for attempt in range(RETRIES):
        try:
            response = client.post(url, data=form, headers=HEADERS, timeout=timeout)
        except httpx.TimeoutException:
            sleep(2.0**attempt)
            continue
        if response.status_code not in retry_statuses:
            return response.raise_for_status()
        sleep(retry_after(response) or 2.0**attempt)
    return client.post(url, data=form, headers=HEADERS, timeout=timeout).raise_for_status()


def retry_after(response: httpx.Response) -> float | None:
    header = response.headers.get("Retry-After", "")
    return float(header) if header.isdigit() else None


def overpass(client: httpx.Client, query: str, sleep: Callable[[float], None]) -> bytes:
    """The response body of one Overpass QL query."""
    form = {"data": query}
    return post(client, OVERPASS_URL, form, retry_statuses={429, 502, 503, 504}, timeout=120.0, sleep=sleep).content
