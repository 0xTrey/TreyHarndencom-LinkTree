# Current Status

Last updated: 2026-11-03

## Blender V3 Release Candidate

- Branch: `codex/treyharnden-v3-local`
- Worktree: `/Users/treyharnden/Projects/TreyHarndencom-V3-Preview`
- Preview: `http://127.0.0.1:5097/`
- Scope: actual Blender-authored alpine terrain with Three.js interaction,
  linked stations, responsive composition, reduced-motion and rendered-image
  fallbacks, current `/now` and `/friends` pages, and complete static export.
- State: Trey approved production publication on November 3. Build, preservation
  and fallback checks passed. Deployment and public verification are pending.
- Review package: `docs/blender-review/README.md`
- Release receipts: `docs/blender-review/release-2026-11-03/`
- Blender 5.2.2 LTS created the editable scene, GLB model, and fallback render.
  Source and regeneration script are under `assets/blender` and `scripts`.

## Personal Directory Credibility Pages

- Source commit: `03e6a3958fdaf22d1d2a263359f4f31a31ea1739`
- Public `/now` and `/friends` routes, footer links, responsive styles, and static
  artifacts were added on 2026-09-17.
- The V3 branch includes those routes so a later review cannot regress the current
  public site.

## Field Systems V2

- Branch: `codex/house-of-growth-v2`
- Source commit: `9e9a5ece6b97937993d03e2f8273715fd91caf29`
- Local preview: `http://127.0.0.1:5005/`
- Design direction: Field Systems, translated from the validated House of Growth
  brand harvests in `research/brand-harvest/`.
- Scope: Home, Systems, Projects, Training, Links, shared navigation/footer, and
  Cloudflare static export.
- Publication state: the split-screen portrait hero was deployed to the existing
  Cloudflare Pages production project on 2026-08-27. No DNS or custom-domain
  configuration was changed.

## Live State

- Production domain: `https://treyharnden.com`
- Last recorded production deployment: `4ce0f0d0-a093-4fbc-ac54-af85ee71e9e9`
- Immutable deployment URL:
  `https://4ce0f0d0.treyharndencom-linktree.pages.dev`
- Canonical project route: `https://treyharnden.com/projects`
- Legacy `/work` redirects to `/projects`
- Apex and `www` are proxied Cloudflare CNAME records targeting
  `treyharndencom-linktree.pages.dev`.
- The live site is already independent of Replit. A Vercel project and verification
  records still exist as legacy/fallback state, but they are not the production DNS
  target.

## What This Branch Preserves

`codex/replit-migration-archive` captures the previously uncommitted local source and
static-export work that accumulated after `main` commit `119ce64`, including:

1. The deployed Projects-page changes documented in the earlier status record.
2. The workouts page and file-backed workout snapshot.
3. The static Cloudflare export workflow and generated `dist-cloudflare` output.
4. The Folloze GTM/project pages and their local assets.
5. The current Cloudflare Pages configuration.

The GitHub history already contains the original Replit lineage and publication
commits. This branch preserves the later local-only state without rewriting that
history.

## Verification

- `uv run python scripts/export_static.py` passed on 2026-08-27.
- `uv run python -m compileall -q app.py models.py utils.py scripts` passed.
- Redacted Gitleaks scans of reachable Git history and the current worktree reported
  zero findings.
- The apex domain, `www`, and immutable Pages URL returned identical homepage HTML,
  stylesheet, and optimized portrait checksums after deployment.
- `/`, `/links`, `/projects`, `/folloze-gtm`, `/workouts`, and `/api/workouts` returned
  HTTP 200 from all three production hosts.
- On 2026-09-17, `/now` and `/friends` returned HTTP 200 with matching HTML
  checksums from the immutable deployment, apex domain, and `www`.
- On 2026-11-02, the local V3 static build passed seven-route desktop, mobile,
  short-phone, and zoom-reflow checks. See `docs/v3-review/README.md`.

## Deploy Workflow

Build the static output:

```bash
uv run python scripts/export_static.py
```

After visual review, deploy the generated site to the existing Cloudflare Pages
project:

```bash
npx wrangler pages deploy dist-cloudflare --project-name treyharndencom-linktree
```

The 2026-08-27 production deployment used the existing project and production branch:

```bash
npx wrangler pages deploy dist-cloudflare \
  --project-name treyharndencom-linktree \
  --branch main \
  --commit-hash 9e9a5ece6b97937993d03e2f8273715fd91caf29
```

## Good Next Checks

- Complete the authorized Blender release, then record its exact source commit,
  deployment ID and public verification. Preserve the prior deployment for rollback.
- The GitHub default branch remains a legacy archive. Production release source
  is tracked on `codex/treyharnden-v3-local`; do not overwrite unrelated branches.
- Remove obsolete Vercel verification/fallback state only after confirming it is no
  longer wanted.
