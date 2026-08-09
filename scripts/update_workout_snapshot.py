#!/usr/bin/env python3
"""Safely merge trusted workout snapshot updates into the file-backed snapshot."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = ROOT / "data" / "workouts_snapshot.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def deep_merge(base: dict, override: dict) -> dict:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def validate_snapshot(snapshot: dict) -> None:
    required_top = {"summary", "activities", "year_label", "source_note"}
    missing = sorted(required_top - set(snapshot))
    if missing:
        raise ValueError(f"Snapshot is missing required top-level keys: {', '.join(missing)}")

    summary = snapshot.get("summary")
    if not isinstance(summary, dict):
        raise ValueError("Snapshot summary must be an object.")

    required_summary = {
        "lifetime_foot_miles",
        "lifetime_workouts",
        "lifetime_run_miles",
        "workouts_year",
        "workouts_30",
        "distance_30",
        "time_30",
    }
    missing_summary = sorted(required_summary - set(summary))
    if missing_summary:
        raise ValueError(
            "Snapshot summary is missing required keys: " + ", ".join(missing_summary)
        )

    activities = snapshot.get("activities")
    if not isinstance(activities, list):
        raise ValueError("Snapshot activities must be a list.")


def write_snapshot(path: Path, snapshot: dict) -> None:
    validate_snapshot(snapshot)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, indent=2) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge a trusted JSON patch into data/workouts_snapshot.json."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to a JSON patch file, or '-' to read JSON from stdin.",
    )
    parser.add_argument(
        "--output",
        default=str(SNAPSHOT_PATH),
        help="Snapshot output path. Defaults to data/workouts_snapshot.json.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = Path(args.output).resolve()
    if output_path.exists():
        current = load_json(output_path)
    elif SNAPSHOT_PATH.exists():
        current = load_json(SNAPSHOT_PATH)
    else:
        current = {}

    if args.input == "-":
        patch_data = json.loads(sys.stdin.read())
    else:
        patch_data = load_json(Path(args.input).resolve())

    merged = deep_merge(current, patch_data)
    write_snapshot(output_path, merged)
    print(f"Updated workout snapshot at {output_path}")


if __name__ == "__main__":
    main()
