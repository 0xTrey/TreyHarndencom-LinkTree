"""Verify Blender asset provenance, GLB structure, navigation, and export parity."""

import hashlib
import json
from pathlib import Path
import struct


ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / "assets/blender/manifest.json").read_text())
assert hashlib.sha256((ROOT / manifest["source"]).read_bytes()).hexdigest() == manifest["blend_sha256"]
assert hashlib.sha256((ROOT / manifest["generator"]).read_bytes()).hexdigest() == manifest["generator_sha256"]
for filename, evidence in manifest["outputs"].items():
    data = (ROOT / "static/models" / filename).read_bytes()
    assert len(data) == evidence["bytes"]
    assert hashlib.sha256(data).hexdigest() == evidence["sha256"]

glb = (ROOT / "static/models/field-atlas.glb").read_bytes()
magic, version, length = struct.unpack_from("<4sII", glb)
assert magic == b"glTF" and version == 2 and length == len(glb)
json_length, chunk_type = struct.unpack_from("<II", glb, 12)
assert chunk_type == 0x4E4F534A
document = json.loads(glb[20:20+json_length])
assert "Blender" in document["asset"]["generator"]
assert len(document["meshes"]) >= 10
assert not any("uri" in buffer for buffer in document["buffers"])
assert not document.get("images"), "The original scene should not need external textures."
links = {node["extras"]["label"]: node["extras"]["href"] for node in document["nodes"] if node.get("extras", {}).get("href")}
assert links == {"Systems": "/folloze-gtm", "Projects": "/projects", "Training": "/workouts"}
assert 10000 < manifest["triangles"] < 200000
for filename in ("models/field-atlas.glb", "models/field-atlas-poster.png", "js/field-atlas.js", "js/field-atlas.js.LEGAL.txt", "css/field-atlas.css"):
    assert (ROOT / "static" / filename).read_bytes() == (ROOT / "dist-cloudflare/static" / filename).read_bytes(), filename
html = (ROOT / "dist-cloudflare/index.html").read_text()
assert 'data-field-atlas' in html and 'js/field-atlas.js' in html
assert 'data-hero-field' not in html and 'js/hero-field.js' not in html
assert html.index('<h1') < html.index('class="atlas-visual"')
print(f"PASS: Blender provenance, {len(document['meshes'])} GLB meshes, {manifest['triangles']:,} triangles, three route markers, local asset parity, headline-first composition")
