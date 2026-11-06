# tests

Pytest suite; no test touches the network.

- `fakes.py`: `FakeFetcher` (serves a dict of URL to bytes or FetchError), `FakeElevation`, and builders for KML lines and HTML pages.
- `test_<module>.py` covers `src/race_courses/<module>.py`; `test_pipeline.py` and `test_cli.py` run the real parsing and geometry code against the fakes.
- HTTP-level tests use `httpx.MockTransport`; fixture files live in `fixtures/`.
