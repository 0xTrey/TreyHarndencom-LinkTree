# Field Atlas: Blender homepage

Local preview: http://127.0.0.1:5097/

This supersedes the shader-only V3 proposal. The homepage uses an original Blender-authored mountain landscape, exported as a real 3D model and rendered interactively with Three.js. Trey approved this immersive version, and it was published and verified at [treyharnden.com](https://treyharnden.com/) on November 3. Source commit: `2aafcf3588cba8b65c7acb107f081ce3016568db`. Release evidence is in [release-2026-11-03](release-2026-11-03/README.md).

## Experience

- Sculpted alpine terrain, elevation contours, summit route, and survey stations.
- Drag or use the arrow keys to rotate. Reset restores the original camera.
- Linked stations open Systems, Projects, and Training.
- Slow ambient movement can be paused. Reduced motion starts paused.
- A Blender-rendered image remains visible during loading and if 3D is unavailable.
- Data-saver mode skips the 3D download. `?atlas=static` requests the static version.
- The name, copy, navigation, journal link, metrics, and other pages remain available.

## November 3 Immersive Pass

The mountain is framed closer and extends beyond the right and lower hero edges on desktop. Phone layouts keep the closer framing without increasing the hero height. The fallback render is enlarged to match.

Ambient movement keeps the same gentle travel but runs about 44% quicker: a full back-and-forth sweep takes about 27 seconds instead of 39. Drag sensitivity, pause, reset, and reduced-motion behavior are unchanged. The renderer retains its drawing buffer so a paused scene remains visible during browser compositing and screenshots.

Six sizes passed: 1920 by 1080, 1440 by 900, 1024 by 768, 768 by 1024, 390 by 844, and 320 by 568. No horizontal overflow, broken images, or station-label overlap with the copy. Nonblank GPU samples and visible metrics-strip hints were confirmed at each size. Static build, asset parity, fallback, syntax, and whitespace checks passed.

Current screenshots: [desktop](immersive-1440x900.png), [wide desktop](immersive-1920x1080.png), [landscape](immersive-1024x768.png), [tablet](immersive-768x1024.png), [phone](immersive-390x844.png), and [short phone](immersive-320x568.png). Measurements: `immersive-responsive-receipt.json`. November 2 screenshots below remain the earlier baseline.

This focused change stayed in Codex. It was approved for publication on November 3; see the separate release receipts for current save and live state.

## Source And Build

- Editable scene: `assets/blender/field-atlas.blend`
- Procedural source: `scripts/build_field_atlas.py`
- Export and provenance: `assets/blender/manifest.json`
- Web model: `static/models/field-atlas.glb`
- Static fallback: `static/models/field-atlas-poster.png`
- Interaction source: `src/field-atlas.js`
- Scene styling: `static/css/field-atlas.css`

Run from this repository, using the installed Blender binary:

```sh
blender --background --python scripts/build_field_atlas.py
npm ci --ignore-scripts
npm run build:atlas
env -u DATABASE_URL uv run python scripts/export_static.py
uv run python scripts/verify_field_atlas.py
node scripts/test_atlas_fallback.mjs
```

On this Mac, Blender is `/Applications/Blender.app/Contents/MacOS/Blender` (5.2.2 LTS). The generator resolves all assets relative to the repository. Blender's script creates the geometry, materials, lighting, camera, GLB, rendered fallback, and source hashes. The .blend file opens independently for editing.

The landscape is original artwork, not a geographic map or a real training route. No third-party model, texture, paid asset, or external API is used. Three.js uses MIT; Lucide uses ISC with MIT notices for inherited icons. Versions are pinned in `package-lock.json`, with full dependency licenses retained beside the browser bundle. [Three.js GLTFLoader](https://threejs.org/docs/#GLTFLoader) loads the Blender export.

## Verification

Verified November 2, 2026:

- Blender generated and reopened the source scene. Two seeded exports produced identical GLB geometry and checksums.
- All seven site routes and the model, poster, script, and stylesheet returned HTTP 200.
- Five viewports passed: 1440 by 900, 1024 by 768, 768 by 1024, 390 by 844, and 320 by 568. No horizontal overflow or broken images. The metrics strip remains visible at each size.
- GPU pixel samples confirm nonblank 3D at every size. The scene contains 13 exported meshes and 126,776 triangles.
- Drag changed the camera from `15,15,18` to `22.252,11.982,11.342`; reset restored the initial view. Arrow-key rotation, pause/resume, and the Projects station link passed.
- Reduced motion starts paused. The browser static-mode check showed the loaded poster, hidden controls, and an unfocusable canvas. Separate tests cover unavailable WebGL and data-saver mode.
- Asset hashes, Blender source provenance, source/export parity, JavaScript/Python syntax, and Git whitespace checks passed.

Screenshots: [desktop](atlas-1440x900.png), [landscape](atlas-1024x768.png), [tablet](atlas-768x1024.png), [phone](atlas-390x844.png), [short phone](atlas-320x568.png), and [static fallback](static-fallback.png). Measurements: `responsive-receipt.json`.

Implementation stayed in Codex for iterative scene composition and browser review. No Cursor or helper agent was dispatched. Trey approved the November 3 immersive pass. Preflight confirmed all production links, current personal pages, and the exact existing workout snapshot are preserved; the separate uncommitted workout refresh is excluded.

The model is about 5.6 MB uncompressed, plus a 648 KB JavaScript bundle. Real-user performance and business impact remain unmeasured.
