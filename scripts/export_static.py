#!/usr/bin/env python3
"""Render the Flask site into a static Cloudflare Pages artifact."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import CSP_POLICY, WORKOUTS_PAGE_ACTIVITY_LIMIT, app, get_workout_data  # noqa: E402


HTML_ROUTES = {
    "/": "index.html",
    "/links": "links/index.html",
    "/projects": "projects/index.html",
    "/folloze-gtm": "folloze-gtm/index.html",
    "/workouts": "workouts/index.html",
}


def write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def write_text(path: Path, content: str) -> None:
    write_bytes(path, content.encode("utf-8"))


def normalize_html(content: bytes) -> bytes:
    text = content.decode("utf-8")
    return ("\n".join(line.rstrip() for line in text.splitlines()) + "\n").encode("utf-8")


def export_static(output_dir: Path) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    shutil.copytree(ROOT / "static", output_dir / "static")

    with app.test_client() as client:
        for route, relative_path in HTML_ROUTES.items():
            response = client.get(route)
            if response.status_code != 200:
                raise RuntimeError(f"{route} returned {response.status_code}")
            write_bytes(output_dir / relative_path, normalize_html(response.data))

    outbound_source = ROOT / "static" / "projects" / "folloze-outbound-engine"
    outbound_target = output_dir / "projects" / "folloze-outbound-intent-loop"
    if outbound_source.exists():
        shutil.copytree(outbound_source, outbound_target, dirs_exist_ok=True)

    write_text(
        output_dir / "api" / "workouts.json",
        json.dumps(get_workout_data(limit=WORKOUTS_PAGE_ACTIVITY_LIMIT), indent=2) + "\n",
    )

    write_text(
        output_dir / "_redirects",
        "\n".join(
            [
                "/work /projects 301",
                "/api/workouts /api/workouts.json 200",
                "/* /index.html 404",
                "",
            ]
        ),
    )

    write_text(
        output_dir / "_headers",
        "\n".join(
            [
                "/*",
                "  X-Content-Type-Options: nosniff",
                "  X-Frame-Options: DENY",
                "  Referrer-Policy: strict-origin-when-cross-origin",
                "  Permissions-Policy: geolocation=(), microphone=(), camera=()",
                f"  Content-Security-Policy: {CSP_POLICY}",
                "",
                "/api/workouts.json",
                "  Content-Type: application/json; charset=utf-8",
                "",
            ]
        ),
    )


def main() -> None:
    output_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist-cloudflare"
    export_static(output_dir.resolve())
    print(f"Exported static site to {output_dir.resolve()}")


if __name__ == "__main__":
    main()
