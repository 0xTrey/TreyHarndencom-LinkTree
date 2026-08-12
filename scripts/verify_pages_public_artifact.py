#!/usr/bin/env python3
"""Verify the checked-in public Cloudflare Pages recovery artifact."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "recovery/cloudflare-pages/cccdee7a-2286-4a95-b514-5b36ab2bf45a/manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    manifest = json.loads(MANIFEST.read_text())
    failures: list[str] = []
    for item in manifest["files"]:
        path = MANIFEST.parent / "site" / item["path"]
        if not path.is_file():
            failures.append(f"missing {item['path']}")
        elif sha256(path) != item["sha256"]:
            failures.append(f"hash mismatch {item['path']}")

    expected = {item["path"] for item in manifest["files"]}
    actual = {
        path.relative_to(MANIFEST.parent / "site").as_posix()
        for path in (MANIFEST.parent / "site").rglob("*")
        if path.is_file()
    }
    for path in sorted(actual - expected):
        failures.append(f"unmanifested {path}")

    if failures:
        raise SystemExit("\n".join(failures))
    print(f"Verified {len(expected)} recovered public Pages files.")


if __name__ == "__main__":
    main()
