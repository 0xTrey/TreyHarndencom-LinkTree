# Current Status

Last updated: 2026-09-19

## Liquid Field V2

- Branch: `codex/liquid-field-preview`
- Published source commit: `08e2cbac1f2d29501523a445463b6a09b4e157f1`
- Public preview: `https://v2.treyharnden.com/`
- Separate Cloudflare Pages project: `treyharndencom-v2`
- Immutable deployment: `https://eb974fe6.treyharndencom-v2.pages.dev/`
- The new look and cursor-responsive field cover Home, Systems, Projects,
  Training, Links, Now, and Friends. Motion can be switched off in the footer.
- The `v2` DNS record is a DNS-only CNAME to `treyharndencom-v2.pages.dev`.
  Cloudflare reported the custom domain active on 2026-09-19.
- This release did not change the existing `treyharndencom-linktree` Pages
  project or the apex and `www` DNS records. The apex homepage SHA-256 stayed
  `10c84b652096ecbb79133c87dbdf19def9e23671c437a20df74026b4c5a537ff`
  before and after the `v2` release.
- All seven public routes and both liquid-field assets returned HTTP 200 from
  `v2.treyharnden.com`. The `v2` homepage matched the Pages deployment byte for
  byte, and desktop and mobile browser checks found no horizontal overflow.

## Personal Directory Credibility Pages

- Branch: `codex/personal-web-directories`
- Source commit: `03e6a3958fdaf22d1d2a263359f4f31a31ea1739`
- Added public `/now` and `/friends` routes, matching static-export artifacts,
  footer discovery links, and responsive page styles.
- The `/friends` page links back to SlashFriends and PersonalWebsites.org. The
  `/now` page credits Derek Sivers' now-page movement.
- Published to the existing Cloudflare Pages production project on 2026-09-17.
- PersonalWebsites.org submission completed on 2026-09-17. The confirmation page
  and email receipt both report that `treyharnden.com` is pending manual review.
- SlashFriends submission completed on 2026-09-17. The directory immediately
  listed `https://treyharnden.com/friends/`, and a live check confirmed its card
  appears with Featured status because the page links back to SlashFriends.
- NowNowNow submission completed on 2026-09-17 by replying to Derek Sivers with
  `https://treyharnden.com/now`. Gmail confirmed the message was sent. The public
  listing remains pending Derek's manual addition and any profile follow-up.

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
- Production deployment: `4ce0f0d0-a093-4fbc-ac54-af85ee71e9e9`
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
- Desktop and mobile browser QA confirmed the new pages are readable, responsive,
  and expose the intended outbound links.
- Every person and directory URL linked from `/friends` returned HTTP 200 before
  publication.

## Deploy Workflow

Build the static output:

```bash
uv run python scripts/export_static.py
```

After visual review, deploy this branch's generated site to the separate v2
Cloudflare Pages project:

```bash
env -u CLOUDFLARE_API_TOKEN npx wrangler pages deploy dist-cloudflare \
  --project-name treyharndencom-v2 --branch main
```

The following command targets the existing apex production project. Do not use
it for v2 updates:

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

- Monitor PersonalWebsites.org for approval and Derek Sivers for the NowNowNow
  listing or profile questions. Record either listing as public only after a live
  directory check.
- Review and merge this branch into `main` so the default Git branch matches the live
  production deployment.
- Remove obsolete Vercel verification/fallback state only after confirming it is no
  longer wanted.
