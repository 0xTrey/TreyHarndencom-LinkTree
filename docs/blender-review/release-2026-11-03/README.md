# Blender Field Atlas Release

Trey approved publishing the current immersive version to `treyharnden.com` on November 3, 2026.

- Target: existing Cloudflare Pages project `treyharndencom-linktree`, production branch `main`, account `0xTrey`. No DNS, custom-domain or access changes.
- Source branch: `codex/treyharnden-v3-local`. The older GitHub default branch is not replaced by this release.
- Previous production deployment: `4ce0f0d0-a093-4fbc-ac54-af85ee71e9e9`, source `03e6a39`, immutable URL `https://4ce0f0d0.treyharndencom-linktree.pages.dev`.
- Preflight: `preflight.json` records current public route hashes, the exact 41-file release artifact, and hashes/status of unrelated dirty production-worktree files.
- Preservation: existing public links, `/now` and `/friends` main copy, and the August workout API snapshot match. The September workout refresh in the original worktree remains unpublished and untouched.
- Checks: static build, Python/JavaScript syntax, asset provenance/parity, fallback tests, responsive browser review and Git whitespace passed. The release must also pass a staged secret scan before push.
- Publication, public verification, browser checks, analytics observation and remote save state will be recorded separately after execution.

Rollback uses the existing prior Pages deployment. Its ID is recorded above; no rollback is requested or performed by this preparation.
