# race-courses

GPX course files for large US road races, rebuilt every week from the maps that race organizers publish.
Each file holds one clean track in race order, with elevation from USGS 3DEP and with bridges and tunnels levelled.
[COVERAGE.md](COVERAGE.md) lists every race in the catalog and says why its course is or is not here yet.

## Use the files

- `courses/<state>/<race>/<event>.gpx`: one GPX 1.1 track per event, with a point every 20 m and elevation in metres.
- `index.json`: one record per event with the race, distance, finisher count, status, source map, measured length and ascent.
- A raw file is at `https://raw.githubusercontent.com/nolangormley/race-courses/main/<file>`.

| Status | Meaning |
| --- | --- |
| `ok` | Course found; its length is within 3% of the race distance. |
| `warn` | Course found, but check it: its length is within 8% of the race distance, or it was joined from part of a larger map. |
| `stale` | File from an earlier crawl that the latest crawl could not confirm; `retrieved` says how old it is. |
| `unsupported` | The organizer shows the course only as a PDF, an image or a map type the crawler cannot read. |
| `no-source` | No course map found on the organizer's site. |
| `no-match` | Maps found, but no line in them matches the race distance. |
| `reject` | A line matches, but it failed a check (for example, it leaves the US). |
| `error` | The site could not be read (robots.txt, bot protection, or downtime). |

## How the crawl works

1. `races.yaml` lists races that had at least 1,000 finishers in their latest edition, each with a source for the count.
2. The crawler reads each race's course page on the organizer's own site, or finds it from the homepage, and collects GPX, KML and KMZ links and embedded Google My Maps.
   An event can also name an OpenStreetMap route relation (`https://www.openstreetmap.org/relation/<id>`) as its `source`.
3. It picks the line whose length matches the event distance, joins maps that are drawn in pieces, and orients the line with start and finish markers when the map has them.
4. It adds USGS 3DEP elevation every 20 m.
   The 3DEP model is bare earth, so a bridge reads as the river below it; the crawler levels bridges and tunnels that OpenStreetMap shows on the course.
5. It publishes a course when the length is within 8% of the race distance; `length_error_pct` says by how much it differs.
6. A GitHub Action runs every Monday and commits only what changed.

The crawler sends the user agent `race-courses-bot`, obeys robots.txt, and waits 2 seconds between requests to the same site.
It does not use Strava, and it skips sites such as RideWithGPS whose robots.txt disallows route exports.

## Add or fix a race

Edit `races.yaml` and open a pull request; CI checks the file.

```yaml
- slug: pittsburgh-marathon            # lowercase words joined by hyphens
  name: Pittsburgh Marathon
  city: Pittsburgh
  state: PA
  month: 5
  website: https://www.thepittsburghmarathon.com/
  course_url: https://...              # organizer page with the course map (optional)
  events:
    - name: Marathon
      distance_m: 42195
      finishers: 3850                  # at least 1,000
      finishers_year: 2025
      finishers_source: https://...    # where the count comes from
      course_url: https://...          # only when this event's map has its own page
      source: https://...              # direct GPX/KML/My Maps link, an OSM relation, or a manual/ path
```

When an organizer publishes the course only as a PDF or an image, trace it by hand, save it as `manual/<state>/<race>/<event>.gpx`, and set the event's `source` to that path.
The crawler then gives it the same elevation and checks as the other courses.

## Run it

```sh
uv sync
uv run race-courses check
uv run race-courses crawl --only pittsburgh-marathon
uv run pytest
```

## Sources and removal

- Course lines come from maps that race organizers publish, or from OpenStreetMap route relations; each record in `index.json` links its source map and page.
- Elevation comes from USGS 3DEP, which is in the public domain.
- Bridge and tunnel positions, and courses with the source kind `osm`, come from OpenStreetMap, © OpenStreetMap contributors, under the ODbL.
- The code is under the MIT license.

Race organizers who want a course removed or corrected can open an issue.
