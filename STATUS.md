# Current Status

Last updated: 2026-08-12

## Field Systems V2

- Branch: `codex/house-of-growth-v2`
- Source commit: `3b23524322c5c087a912cb9c07481b1756dc46f9`
- Local preview: `http://127.0.0.1:5005/`
- Design direction: Field Systems, translated from the validated House of Growth
  brand harvests in `research/brand-harvest/`.
- Scope: Home, Systems, Projects, Training, Links, shared navigation/footer, and
  Cloudflare static export.
- Publication state: deployed to the existing Cloudflare Pages production project on
  2026-08-12. No DNS or custom-domain configuration was changed.

## Live State

- Production domain: `https://treyharnden.com`
- Production deployment: `f10b09c0-e590-4651-9102-ea19dd690923`
- Immutable deployment URL:
  `https://f10b09c0.treyharndencom-linktree.pages.dev`
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

- `uv run python scripts/export_static.py` passed on 2026-08-12.
- `uv run python -m compileall -q app.py models.py utils.py scripts` passed.
- Redacted Gitleaks scans of reachable Git history and the current worktree reported
  zero findings.
- The apex domain, `www`, and immutable Pages URL returned identical homepage HTML and
  stylesheet checksums after deployment.
- `/`, `/links`, `/projects`, `/folloze-gtm`, `/workouts`, and `/api/workouts` returned
  HTTP 200 from all three production hosts.

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

The 2026-08-12 production deployment used the existing project and production branch:

```bash
npx wrangler pages deploy dist-cloudflare \
  --project-name treyharndencom-linktree \
  --branch main \
  --commit-hash 3b23524322c5c087a912cb9c07481b1756dc46f9
```

## Good Next Checks

- Review and merge this branch into `main` so the default Git branch matches the live
  production deployment.
- Remove obsolete Vercel verification/fallback state only after confirming it is no
  longer wanted.
