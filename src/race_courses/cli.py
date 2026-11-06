"""Command line: `race-courses check` and `race-courses crawl`."""

import argparse
import sys
import time
from datetime import date
from pathlib import Path

from race_courses import api, catalog, pipeline, publish
from race_courses.elevation import Elevation
from race_courses.fetch import Fetcher, make_client


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="race-courses", description="Build GPX files of large US road race courses.")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check", help="check races.yaml and exit")
    crawl = commands.add_parser("crawl", help="crawl the races and update courses/, index.json and COVERAGE.md")
    crawl.add_argument("--only", nargs="+", metavar="SLUG", help="crawl only these races")
    crawl.add_argument("--force", action="store_true", help="rebuild every course, also the unchanged ones")
    parser.add_argument("--root", type=Path, default=Path("."), help="dataset folder that holds races.yaml")
    args = parser.parse_args(argv)

    try:
        races = catalog.load(args.root / "races.yaml")
    except ValueError as error:
        print(f"races.yaml has problems:\n{error}", file=sys.stderr)
        return 1
    if args.command == "check":
        print(f"races.yaml: {len(races)} races, {sum(len(race.events) for race in races)} events")
        return 0

    selected = races
    if args.only:
        unknown = set(args.only) - {race.slug for race in races}
        if unknown:
            print(f"unknown race: {', '.join(sorted(unknown))}", file=sys.stderr)
            return 1
        selected = [race for race in races if race.slug in args.only]

    index_path = args.root / "index.json"
    previous = publish.read_index(index_path)
    today = date.today()
    with make_client() as client:
        context = pipeline.Context(
            fetcher=Fetcher(client),
            elevation=Elevation(client),
            overpass=lambda query: api.overpass(client, query, time.sleep),
            root=args.root,
            previous=previous,
            day=today,
            reuse=not args.force,
        )
        fresh = pipeline.crawl(selected, context, log=lambda line: print(line, flush=True))

    listed = {(race.slug, event.slug) for race in races for event in race.events}
    merged = {key: entry for key, entry in previous.items() if key in listed}
    merged.update({(entry["race"], entry["event"]): entry for entry in fresh})
    entries = list(merged.values())
    publish.write_index(index_path, entries)
    (args.root / "COVERAGE.md").write_text(publish.coverage_markdown(entries, today))
    for path in publish.prune(args.root, entries):
        print(f"removed {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
