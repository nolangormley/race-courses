# race-courses

Open dataset of GPX course files for large US road races, and the crawler that rebuilds it every week.

## Layout
- `races.yaml`: the race catalog, the only hand-edited input. The README has the schema.
- `src/race_courses/`: the crawler package (see its AGENTS.md).
- `tests/`: pytest suite without network access (see its AGENTS.md).
- `courses/`, `index.json`, `COVERAGE.md`: output of `race-courses crawl`. Do not edit them by hand.
- `manual/`: traced GPX files that an event in races.yaml can name as its `source`; `manual/README.md` records how each was traced.
- `.github/workflows/ci.yml`: runs the tests and `race-courses check`.
- `deploy/`: the weekly crawl, a systemd user timer on a machine outside the cloud (see its AGENTS.md).

## Commands
- `uv sync`, then `uv run pytest`.
- `uv run race-courses check` validates races.yaml.
- `uv run race-courses crawl [--only SLUG ...] [--force]` updates the dataset; `--force` rebuilds unchanged courses too.
