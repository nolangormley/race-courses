"""Load and check the race list in races.yaml."""

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

MIN_FINISHERS = 1000
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
STATES = frozenset(
    "AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH "
    "NJ NM NY NC ND OH OK OR PA PR RI SC SD TN TX UT VT VA WA WV WI WY".split()
)
RACE_KEYS = {"slug", "name", "city", "state", "month", "website", "course_url", "events", "notes"}
EVENT_KEYS = {
    "name", "distance_m", "finishers", "finishers_year", "finishers_source", "course_url", "source", "notes",
}


@dataclass(frozen=True)
class Event:
    slug: str
    name: str
    distance_m: float
    finishers: int
    finishers_year: int
    finishers_source: str
    course_url: str | None = None
    source: str | None = None


@dataclass(frozen=True)
class Race:
    slug: str
    name: str
    city: str
    state: str
    month: int
    website: str
    course_url: str | None
    events: tuple[Event, ...]


def event_slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def load(path: Path) -> list[Race]:
    """Read the races. Raise ValueError that lists every problem in the file."""
    entries = yaml.safe_load(path.read_text()) or []
    problems: list[str] = []
    races: list[Race] = []
    seen: set[str] = set()
    for position, entry in enumerate(entries, start=1):
        label = f"entry {position} ({entry.get('slug', '?')})" if isinstance(entry, dict) else f"entry {position}"
        found = race_problems(entry, path.parent)
        if not found and entry["slug"] in seen:
            found = ["slug is used twice"]
        if found:
            problems.extend(f"{label}: {problem}" for problem in found)
            continue
        seen.add(entry["slug"])
        races.append(build_race(entry))
    if problems:
        raise ValueError("\n".join(problems))
    return races


def race_problems(entry, root: Path) -> list[str]:
    if not isinstance(entry, dict):
        return ["is not a mapping"]
    problems = [f"unknown key {key!r}" for key in sorted(set(entry) - RACE_KEYS)]
    required = ("slug", "name", "city", "state", "month", "website", "events")
    problems += [f"missing {key}" for key in required if not entry.get(key)]
    if problems:
        return problems
    if not SLUG.match(str(entry["slug"])):
        problems.append("slug must be lowercase words joined by hyphens")
    if entry["state"] not in STATES:
        problems.append(f"unknown state {entry['state']!r}")
    if not isinstance(entry["month"], int) or not 1 <= entry["month"] <= 12:
        problems.append("month must be 1 to 12")
    problems += url_problems(entry, ("website", "course_url"))
    if not isinstance(entry["events"], list):
        return problems + ["events must be a list"]
    event_slugs = set()
    for event in entry["events"]:
        event_label = f"event {event.get('name', '?')!r}" if isinstance(event, dict) else "event"
        problems += [f"{event_label}: {problem}" for problem in event_problems(event, root)]
        if isinstance(event, dict) and event.get("name"):
            slug = event_slug(str(event["name"]))
            if slug in event_slugs:
                problems.append(f"{event_label}: two events have the same name")
            event_slugs.add(slug)
    return problems


def event_problems(event, root: Path) -> list[str]:
    if not isinstance(event, dict):
        return ["is not a mapping"]
    problems = [f"unknown key {key!r}" for key in sorted(set(event) - EVENT_KEYS)]
    problems += [
        f"missing {key}"
        for key in ("name", "distance_m", "finishers", "finishers_year", "finishers_source")
        if event.get(key) in (None, "")
    ]
    if problems:
        return problems
    if not isinstance(event["distance_m"], (int, float)) or event["distance_m"] <= 0:
        problems.append("distance_m must be a positive number")
    if not isinstance(event["finishers"], int) or event["finishers"] < MIN_FINISHERS:
        problems.append(f"finishers must be at least {MIN_FINISHERS}")
    if not isinstance(event["finishers_year"], int) or not 2000 <= event["finishers_year"] <= 2100:
        problems.append("finishers_year must be a year")
    problems += url_problems(event, ("finishers_source", "course_url"))
    source = event.get("source")
    if source is not None and not str(source).startswith(("http://", "https://", "manual/")):
        problems.append("source must be a URL or a path under manual/")
    elif source is not None and str(source).startswith("manual/") and not (root / source).is_file():
        problems.append(f"{source} does not exist")
    return problems


def url_problems(entry: dict, keys: tuple[str, ...]) -> list[str]:
    return [
        f"{key} must start with http:// or https://"
        for key in keys
        if entry.get(key) is not None and not str(entry[key]).startswith(("http://", "https://"))
    ]


def build_race(entry: dict) -> Race:
    events = tuple(
        Event(
            slug=event_slug(event["name"]),
            name=event["name"],
            distance_m=float(event["distance_m"]),
            finishers=event["finishers"],
            finishers_year=event["finishers_year"],
            finishers_source=event["finishers_source"],
            course_url=event.get("course_url"),
            source=event.get("source"),
        )
        for event in entry["events"]
    )
    return Race(
        slug=entry["slug"],
        name=entry["name"],
        city=entry["city"],
        state=entry["state"],
        month=entry["month"],
        website=entry["website"],
        course_url=entry.get("course_url"),
        events=events,
    )
