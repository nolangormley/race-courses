"""Write the dataset files: one GPX per course, index.json and COVERAGE.md."""

import json
from collections import Counter
from collections.abc import Sequence
from datetime import date
from pathlib import Path
from xml.etree import ElementTree

from race_courses.models import Point
from race_courses.settings import USER_AGENT

GPX_NS = "http://www.topografix.com/GPX/1/1"
PUBLISHED = ("ok", "warn", "stale")


def gpx_bytes(points: Sequence[Point], title: str, description: str, link: str, day: date) -> bytes:
    ElementTree.register_namespace("", GPX_NS)
    root = ElementTree.Element(f"{{{GPX_NS}}}gpx", {"version": "1.1", "creator": USER_AGENT})
    metadata = ElementTree.SubElement(root, f"{{{GPX_NS}}}metadata")
    ElementTree.SubElement(metadata, f"{{{GPX_NS}}}name").text = title
    ElementTree.SubElement(metadata, f"{{{GPX_NS}}}desc").text = description
    link_element = ElementTree.SubElement(metadata, f"{{{GPX_NS}}}link", {"href": link})
    ElementTree.SubElement(link_element, f"{{{GPX_NS}}}text").text = title
    ElementTree.SubElement(metadata, f"{{{GPX_NS}}}time").text = f"{day.isoformat()}T00:00:00Z"
    track = ElementTree.SubElement(root, f"{{{GPX_NS}}}trk")
    ElementTree.SubElement(track, f"{{{GPX_NS}}}name").text = title
    segment = ElementTree.SubElement(track, f"{{{GPX_NS}}}trkseg")
    for point in points:
        position = {"lat": f"{point.lat:.6f}", "lon": f"{point.lon:.6f}"}
        element = ElementTree.SubElement(segment, f"{{{GPX_NS}}}trkpt", position)
        if point.ele is not None:
            ElementTree.SubElement(element, f"{{{GPX_NS}}}ele").text = f"{point.ele:.1f}"
    ElementTree.indent(root, space=" ")
    return ElementTree.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"


def write_index(path: Path, entries: list[dict]) -> None:
    ordered = sorted(entries, key=lambda entry: (entry["state"], entry["race"], entry["event"]))
    path.write_text(json.dumps(ordered, indent=1, ensure_ascii=False) + "\n")


def read_index(path: Path) -> dict[tuple[str, str], dict]:
    if not path.exists():
        return {}
    return {(entry["race"], entry["event"]): entry for entry in json.loads(path.read_text())}


def prune(root: Path, entries: list[dict]) -> list[Path]:
    """Delete course files that no index entry names. Return the deleted paths."""
    kept = {root / entry["file"] for entry in entries if entry.get("file")}
    courses = root / "courses"
    if not courses.exists():
        return []
    removed = [path for path in courses.rglob("*.gpx") if path not in kept]
    for path in removed:
        path.unlink()
    for folder in sorted(courses.rglob("*"), key=lambda folder: len(folder.parts), reverse=True):
        if folder.is_dir() and not any(folder.iterdir()):
            folder.rmdir()
    return removed


def coverage_markdown(entries: list[dict], day: date) -> str:
    statuses = Counter(entry["status"] for entry in entries)
    published = sum(statuses[status] for status in PUBLISHED)
    races = len({entry["race"] for entry in entries})
    lines = [
        "# Coverage",
        "",
        f"Weekly crawl of {day.isoformat()}: {races} races, {len(entries)} events, "
        f"{published} courses published ({published / max(1, len(entries)):.0%}).",
        "",
        "| Status | Events | Meaning |",
        "| --- | ---: | --- |",
    ]
    meanings = {
        "ok": "Course found; length within 3% of the race distance.",
        "warn": "Course found; check it (length within 8%, or joined from part of a larger map).",
        "stale": "File from an earlier crawl; the latest crawl did not confirm it.",
        "unsupported": "Only a map type the crawler cannot read (PDF, image, Strava, ...).",
        "no-source": "No course map found on the organizer's site.",
        "no-match": "Maps found, but no line matches the race distance.",
        "reject": "A line matches, but it failed a check.",
        "error": "The site could not be read (robots.txt, blocked, or down).",
    }
    for status, meaning in meanings.items():
        if statuses[status]:
            lines.append(f"| {status} | {statuses[status]} | {meaning} |")
    kinds = Counter(kind for entry in entries if entry["status"] == "unsupported" for kind in entry.get("found", []))
    if kinds:
        counts = ", ".join(f"{kind} {count}" for kind, count in kinds.most_common())
        lines += ["", f"Map types on pages without a readable course: {counts}."]
    missing = [entry for entry in entries if entry["status"] not in PUBLISHED]
    if missing:
        lines += [
            "",
            "## Not covered yet",
            "",
            "A hand-traced GPX in `manual/` can cover any of these; see the README.",
            "",
            "| State | Race | Event | Status | Detail |",
            "| --- | --- | --- | --- | --- |",
        ]
        for entry in sorted(missing, key=lambda entry: (entry["state"], entry["race"], entry["event"])):
            race = f"[{entry['name']}]({entry['page']})" if entry.get("page") else entry["name"]
            detail = entry.get("detail", "").replace("|", "/")
            lines.append(f"| {entry['state']} | {race} | {entry['event_name']} | {entry['status']} | {detail} |")
    return "\n".join(lines) + "\n"
