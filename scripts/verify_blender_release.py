"""Record production preservation before release and exact public parity afterward."""

import argparse
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist-cloudflare"
RECEIPTS = ROOT / "docs/blender-review/release-2026-11-03"
PRIMARY = ROOT.parent / "TreyHarndencom-LinkTree"
ROUTES = {"/": "index.html", "/now": "now/index.html", "/friends": "friends/index.html",
          "/projects": "projects/index.html", "/links": "links/index.html",
          "/workouts": "workouts/index.html", "/folloze-gtm": "folloze-gtm/index.html",
          "/api/workouts": "api/workouts.json"}
ASSETS = ("css/style.css", "css/field-atlas.css", "js/main.js", "js/field-atlas.js",
          "models/field-atlas.glb", "models/field-atlas-poster.png")


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Page(HTMLParser):
    def __init__(self, body):
        super().__init__()
        self.links, self.main, self.in_main = set(), [], False
        self.feed(body.decode())

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if tag == "main":
            self.in_main = True
        if tag == "a" and attributes.get("href"):
            self.links.add(attributes["href"])

    def handle_endtag(self, tag):
        if tag == "main":
            self.in_main = False

    def handle_data(self, text):
        if self.in_main and text.strip():
            self.main.append(" ".join(text.split()))


def fetch(url):
    with urlopen(Request(url, headers={"User-Agent": "FieldAtlasReleaseVerifier/1.0"}), timeout=30) as response:
        return response.read(), response.status, dict(response.headers)


def primary_state():
    status = subprocess.check_output(["git", "status", "--porcelain", "-z"], cwd=PRIMARY).decode()
    paths = [row[3:] for row in status.split("\0") if row]
    hashes = {name: sha((PRIMARY / name).read_bytes()) for name in paths if (PRIMARY / name).is_file()}
    return {"status": status.replace("\0", "\n"), "sha256": hashes}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("preflight", "live"))
    parser.add_argument("hosts", nargs="*", default=["https://treyharnden.com"])
    args = parser.parse_args()
    receipt = {"observed_at": datetime.now(timezone.utc).isoformat(), "mode": args.mode, "hosts": {}}
    for host in args.hosts:
        observations = {}
        for route, relative in ROUTES.items():
            body, status, headers = fetch(host.rstrip("/") + route)
            local = (DIST / relative).read_bytes()
            assert status == 200, (host, route, status)
            if args.mode == "live":
                assert body == local, f"Public content differs: {host}{route}"
            elif route != "/api/workouts":
                public_page, release_page = Page(body), Page(local)
                missing = public_page.links - release_page.links
                assert not missing, f"Lost links on {route}: {sorted(missing)}"
                if route in ("/now", "/friends"):
                    assert public_page.main == release_page.main, f"Changed accepted copy: {route}"
            else:
                assert json.loads(body) == json.loads(local), "Workout data differs from production"
            observations[route] = {"status": status, "bytes": len(body), "sha256": sha(body)}
        if args.mode == "live":
            for relative in ASSETS:
                route = "/static/" + relative
                body, status, headers = fetch(host.rstrip("/") + route)
                assert status == 200 and body == (DIST / "static" / relative).read_bytes(), route
                observations[route] = {"status": status, "bytes": len(body), "sha256": sha(body),
                                       "content_type": headers.get("Content-Type")}
            body, status, headers = fetch(host.rstrip("/") + "/work")
            assert body == (DIST / "projects/index.html").read_bytes(), "Legacy /work redirect regressed"
            _, _, headers = fetch(host.rstrip("/") + "/")
            lower_headers = {key.lower(): value for key, value in headers.items()}
            assert "default-src 'self'" in lower_headers.get("content-security-policy", "")
            assert lower_headers.get("x-content-type-options") == "nosniff"
        receipt["hosts"][host] = observations

    files = {str(path.relative_to(DIST)): {"bytes": path.stat().st_size, "sha256": sha(path.read_bytes())}
             for path in sorted(DIST.rglob("*")) if path.is_file()}
    assert max(item["bytes"] for item in files.values()) < 25 * 1024 * 1024
    assert len(files) < 20000
    receipt["artifact"] = files
    receipt["primary_worktree"] = primary_state()
    if args.mode == "live":
        baseline = json.loads((RECEIPTS / "preflight.json").read_text())
        assert receipt["primary_worktree"] == baseline["primary_worktree"], "Unrelated primary worktree changed"
        assert files == baseline["artifact"], "Artifact changed after preflight"
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    (RECEIPTS / f"{args.mode}.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"PASS: {args.mode}, {len(args.hosts)} hosts, {len(files)} artifact files, primary worktree preserved")


if __name__ == "__main__":
    main()
