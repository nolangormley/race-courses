# race_courses package

The crawler turns `races.yaml` into one GPX file per race event, plus `index.json` and `COVERAGE.md`.

## Data flow
`cli.main` loads the catalog, then calls `pipeline.crawl` with a `Fetcher`, an `Elevation` and an Overpass callable.
The crawl works through each race in this order:
1. `pipeline.RaceReader` fetches pages once per race.
2. `discover` finds course sources on those pages.
3. `readers` parses each source into a `Geometry`.
4. `geometry.assemble` picks the line that fits the event distance.
5. `validate.check` judges that line.
6. `geometry.resample` and `Elevation.profile` add a point every 20 m with elevation.
7. `publish` writes the files.

## Modules
- `models.py`: the shared value types `Point`, `Line`, `Marker`, `Geometry`, `SourceRef` and `Course`.
- `settings.py`: the user agent and the project URL.
- `catalog.py`: `load(path)` reads `races.yaml` into `Race` and `Event` objects and raises one `ValueError` that lists every problem. Events need at least `MIN_FINISHERS`.
- `fetch.py`: `Fetcher.get(url)` is polite crawling. It obeys robots.txt (RFC 9309), waits between requests to the same host, follows redirects by hand, and caps the size. It raises `FetchError` or `Blocked`. `make_client()` builds the httpx client.
- `discover.py`:
  - `kind_for_content_type` names files that are served without an extension.
  - `find_sources(html, url)` lists course sources by kind. The `FETCHABLE` kinds are gpx, kml, kmz and mymaps; other kinds, such as pdf and strava, are kept for the coverage report.
  - `source_ref(url, ...)` classifies one URL.
  - `find_course_links(html, url)` ranks the pages of the same site that probably show the course.
- `readers.py`: `read_source(bytes)` detects the format and parses GPX, KML or KMZ with defusedxml.
- `geometry.py`:
  - `assemble(geometry, target_m)` cleans the lines, chains pieces, picks the candidate nearest the distance, and orients it with start and finish markers.
  - Also provides `resample`, `haversine_m` and `cumulative_m`.
- `api.py`: `post` sends a form POST with retries and backoff (honours Retry-After). `overpass(client, query, sleep)` runs one Overpass query. Both `elevation` and the OSM source use it.
- `osm.py`: `relation_query(url)` and `read_relation(bytes)` turn an `openstreetmap.org/relation/<id>` route into a `Geometry`, with start and finish markers taken from the member roles.
- `elevation.py`:
  - `Elevation.profile(points)` gets elevation from USGS 3DEP `getSamples` in batches and fills NoData gaps.
  - It levels bridges and tunnels from OpenStreetMap (Overpass), using a distance-and-heading test so that roads passing under a bridge stay on the ground.
  - `gain_loss` adds up ascent and descent with a threshold.
- `validate.py`: `check(course, target_m)` returns a `Verdict`:
  - ok when the length is within 3%,
  - warn when it is within 8%,
  - reject otherwise, or when the course leaves the US.
  - Straight segments longer than 1.5 km get a note but do not change the status.
  - A course chained from less than 90% of a map's lines (`method` "chain:used/available") is at most warn, because the pieces can come from different courses.
  - `geometry.assemble` ignores lines whose names state a different distance ("2025 14k" for a half), so courses of other events on the same map are not chained in.
- `pipeline.py`:
  - `crawl(races, context)` returns the index entries.
  - An entry is reused without new API calls when its geometry hash and `PIPELINE_VERSION` are unchanged.
  - A course that the latest crawl cannot confirm keeps its earlier file with the status `stale`, but only when that file came from the same `PIPELINE_VERSION`. Bump the version when course building changes.
- `publish.py`: `gpx_bytes`, `read_index`, `write_index`, `prune` (deletes GPX files that no entry names) and `coverage_markdown`.
- `cli.py`: `race-courses check` and `race-courses crawl [--only SLUG ...] [--force]`.
