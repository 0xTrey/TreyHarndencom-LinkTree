# Blender Field Atlas Release

Trey approved publishing the current immersive version to `treyharnden.com` on November 3, 2026.

- Target: existing Cloudflare Pages project `treyharndencom-linktree`, production branch `main`, account `0xTrey`. No DNS, custom-domain or access changes.
- Source branch: `codex/treyharnden-v3-local`. The older GitHub default branch is not replaced by this release.
- Previous production deployment: `4ce0f0d0-a093-4fbc-ac54-af85ee71e9e9`, source `03e6a39`, immutable URL `https://4ce0f0d0.treyharndencom-linktree.pages.dev`.
- Preflight: `preflight.json` records current public route hashes, the exact 41-file release artifact, and hashes/status of unrelated dirty production-worktree files.
- Preservation: existing public links, `/now` and `/friends` main copy, and the August workout API snapshot match. The September workout refresh in the original worktree remains unpublished and untouched.
- Checks: static build, Python/JavaScript syntax, asset provenance/parity, fallback tests, responsive browser review and source whitespace checks passed. Generated Three.js GLSL whitespace is preserved using two scoped `.gitattributes` entries. Staged and new-commit Gitleaks scans found no secrets.

Rollback uses the existing prior Pages deployment. Its ID is recorded above; no rollback is requested or performed by this preparation.

## Published Result

- Source: `2aafcf3588cba8b65c7acb107f081ce3016568db` on `codex/treyharnden-v3-local`, committed and pushed. The preceding implementation commit is `99f4231dfb06794d4074f7dc5fdd4adb05f8d418`.
- Clean checkout: npm install/build, Blender provenance, static export and fallback tests passed. All 41 exported files matched the preflight artifact byte-for-byte.
- Deployment: `ebcf5d5b-6f39-4e1d-bfcb-797044d8cd36`, environment Production, Pages branch `main`, source `2aafcf3`, Wrangler 4.157.0.
- Public: [apex](https://treyharnden.com/), [www](https://www.treyharnden.com/), and [immutable deployment](https://ebcf5d5b.treyharndencom-linktree.pages.dev/) passed exact route and critical-asset checksum comparison. `/work` still resolves to Projects. CSP and nosniff headers are present. Full receipt: `live.json`.
- Browser: live desktop 1440 by 900 and mobile 390 by 844 show all 13 3D meshes with nonblank GPU samples, no horizontal overflow and no broken images. Faster motion, pause/resume, keyboard rotation/reset, Projects station navigation, mobile menu/Escape, reduced motion and static fallback passed. No runtime exception or console issue was captured. Receipt: `live-browser.json`; screenshots: `live-desktop.png` and `live-mobile.png`.
- Analytics: the existing Google Analytics collection request returned HTTP 204. This confirms transport acknowledgment, not reporting ingestion, attribution or business impact.
- Preservation: original production-worktree status and file hashes still match preflight. Its separate workout refresh was not deployed. No DNS, sharing, permission, paid-service or external-message action occurred.

Wrangler warned that the legacy `wrangler.toml` lacks `pages_build_output_dir`; it used the explicit artifact directory, project and branch supplied by the deployment command. Cloudflare readback and public parity verified the intended target.

This release is published, not merely saved or locally tested. Real-user performance, adoption and impact remain unmeasured. The receipt follow-up commit changes documentation only and does not require another deployment.
