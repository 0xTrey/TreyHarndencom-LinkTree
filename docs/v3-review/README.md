# treyharnden.com V3 local review

Superseded by [the actual Blender Field Atlas](../blender-review/README.md). The screenshots below document the earlier shader-only proposal, not the current homepage.

This is a local review build. It is not deployed or pushed.

- Branch: `codex/treyharnden-v3-local`
- Worktree: `/Users/treyharnden/Projects/TreyHarndencom-V3-Preview`
- Preview: `http://127.0.0.1:5097/`
- Baseline: split portrait production commit `dfd8d72`, plus the current public `/now` and `/friends` source from `03e6a39`

## What changed

- The split portrait hero now stacks at 840px, grows with its content, and keeps the next metrics strip visible at the tested desktop and mobile heights.
- The copy panel uses a lightweight interactive field adapted from the existing project-owned liquid preview. Pointer movement creates a restrained wake, while a visible control pauses and resumes motion.
- The portrait uses responsive sources instead of sending the 1.5 MB source to every viewport.
- Long copy, long CTA labels, failed images, narrow grids, touch navigation, reduced motion, and zoom reflow have explicit fallbacks.
- Headlines lead every content header. Operational labels stay in a side column on wide screens and follow the supporting body on narrow screens.
- Active navigation uses `aria-current`. The skip link moves keyboard focus to the main region. The mobile menu closes with Escape and restores focus.
- Current public routes, workout provenance, project facts, copy, palette, type, and portrait direction are preserved.
- Visual numbering uses `1` through `9`, without leading zeros. Training placeholders use `N/A`, without em dashes.

## Portrait assets

All derivatives come from the existing project-owned source at `static/images/headshot-professional-v1-web.jpg`.

| File | Use | Size |
| --- | --- | ---: |
| `headshot-professional-v1-720.avif` | Phones up to 640px | 60,534 bytes |
| `headshot-professional-v1-720.jpg` | Base responsive JPEG | 175,650 bytes |
| `headshot-professional-v1-960.jpg` | Medium responsive JPEG | 359,591 bytes |
| `headshot-professional-v1-1280.jpg` | Large responsive JPEG | 591,397 bytes |
| `headshot-professional-v1-web.jpg` | Master web source and highest-density fallback | 1,547,382 bytes |

Regenerate the derivatives and static build from the repo root:

```bash
uv run python scripts/build_site_images.py
uv run python scripts/export_static.py
uv run python -m compileall -q app.py models.py utils.py scripts
```

The image script uses the macOS `sips` binary and repo-relative paths. The static exporter copies the generated image files into `dist-cloudflare`.

## Blender decision

Blender 5.2.2 LTS is installed, but the site repos contain no project-owned `.blend`, model, asset library, or third-party license record. No Blender asset was created or used in this pass.

The existing project-owned liquid field was a better fit than a new 3D asset. This pass adapts that idea into a smaller homepage-only WebGL field at `static/js/hero-field.js`, with its presentation in `static/css/hero-field.css`. It loads only on the homepage, pauses outside the viewport or when the tab is hidden, honors reduced-motion preferences, and falls back to a static CSS grid when WebGL is unavailable. The implementation is committed source code, so no binary motion asset or external runtime is required.

The source reference was `/Users/treyharnden/Projects/TreyHarndencom-Liquid-Preview/static/js/liquid-field.js` at commit `2621f53`. No third-party model, material, image, or shader asset was added. A future 3D asset should start with a committed procedural source scene, regeneration script, and clear reason for the asset to exist.

Stageshow was not used because this page needs a real personal identity and functional navigation, not an authored product illustration.

## Verification

Completed November 2, 2026 against the generated `dist-cloudflare` artifact.

| Check | Result |
| --- | --- |
| Desktop, 1440 by 900 | Split hero, no overflow, no broken images, 48px of the metrics strip visible |
| Landscape, 1024 by 768 | Split hero, single-line name, full torso crop, no overflow, 48px of the metrics strip visible |
| Tablet, 768 by 1024 | Stacked hero, stable portrait paint, no overflow |
| Mobile, 390 by 844 | Mobile AVIF, no overflow, 35px of the metrics strip visible |
| Short phone, 320 by 568 | Both CTA labels fit, portrait strip is stable, 41px of the metrics strip visible |
| Zoom proxy, 195 by 422 | All seven routes reflow without horizontal overflow |
| Header order | Headline and supporting body precede operational labels on narrow screens |
| Long-copy stress | Hero and buttons grow without clipping or overlapping the portrait |
| Image failure | Initials fallback appears and retains the portrait frame |
| Reduced motion | Reveal targets remain visible with animation disabled |
| Interactive field | Pointer input creates a wake; pause and resume update the control state and label |
| WebGL fallback | Static field remains legible and the unavailable motion control stays hidden |
| Keyboard | Skip link focuses `main`; mobile Escape closes the menu and restores toggle focus |
| Console | No warnings or errors on a clean local load |
| Static output | Seven routes and responsive assets return HTTP 200; source and exported CSS/JS checksums match |

Large AVIF derivatives were not retained. Chrome decoded them but did not paint them reliably during tablet QA. AVIF is limited to the verified 720px mobile source, with JPEGs above that breakpoint.

## Screenshots

| View | Current production | Local V3 |
| --- | --- | --- |
| Desktop | [1440 by 900](before-desktop-1440x900.png) | [1440 by 900](after-desktop-1440x900.png) |
| Mobile | [390 by 844](before-mobile-390x844.png) | [390 by 844](after-mobile-390x844.png) |

Additional local checks: [1024 by 768](after-landscape-1024x768.png), [768 by 1024](after-tablet-768x1024.png), and [320 by 568](after-narrow-320x568.png).

## Review boundary

The remaining decision is visual approval. Publication, a remote push, Cloudflare changes, and production verification require a separate action.
