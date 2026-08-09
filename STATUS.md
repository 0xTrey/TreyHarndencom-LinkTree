# Current Status

Last updated: 2026-08-09

## Live State

- Production domain: `https://treyharnden.com`
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

- `uv run python scripts/export_static.py` passed on 2026-08-09.
- Redacted Gitleaks scans of reachable Git history and the current worktree reported
  zero findings.
- Live CSS is byte-identical to the regenerated local CSS and the public routes are
  from the same source family.
- Live HTML, JavaScript, and workout JSON are not all byte-identical to the regenerated
  export, so this archive does not claim to be the exact currently deployed snapshot.

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

No production deployment was performed while creating this preservation branch; the
current production domain was already on Cloudflare Pages.

## Good Next Checks

- Review and merge this branch into `main` when the accumulated site changes are
  accepted.
- Run a final desktop/mobile visual pass before publishing a newly generated static
  export.
- Remove obsolete Vercel verification/fallback state only after confirming it is no
  longer wanted.
