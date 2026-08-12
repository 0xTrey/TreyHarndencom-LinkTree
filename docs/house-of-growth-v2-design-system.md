# TreyHarnden.com V2 - Field Systems Design Direction

## Source references

- House of Growth: <https://www.housesofgrowth.com/>
- House of Growth for Folloze: <https://experience.folloze.com/house-of-growth-for-folloze>
- Structured harvests: `research/brand-harvest/houses-of-growth/` and `research/brand-harvest/house-of-growth-folloze/`

Both harvest bundles passed the Brand Harvester validation gate on August 12, 2026. Each bundle contains desktop/mobile source screenshots, structured source evidence, candidate tokens, and an asset manifest.

## Translation, not duplication

The rebuild borrows the source system's design grammar without copying its page, logo, claims, or proprietary hero art. The original Trey-specific concept is **Field Systems**: an operating manual for AI-assisted GTM work, public experiments, mountain training, and field notes.

## Core visual system

### Personality

- Industrial editorial, direct, and slightly retro.
- More operating manual than personal portfolio.
- Technical enough for systems work; physical enough for mountain and training content.
- Dense with evidence, but never arranged as a conventional dashboard.

### Color

| Role | Token | Value |
| --- | --- | --- |
| Primary ink | `--ink` | `#11110f` |
| Deep background | `--ink-deep` | `#090a09` |
| Secondary dark | `--charcoal` | `#1b1c1a` |
| Light field | `--paper` | `#e3e3df` |
| Signal / progress | `--mint` | `#08dfad` |
| Action / emphasis | `--rust` | `#df4008` |

Mint communicates live systems, readiness, and progress. Rust is reserved for action, navigation state, and emphasis. Light sections interrupt the dark rhythm so the site does not collapse into a one-note black/green terminal theme.

### Type

- Display: Black Ops One, self-hosted under the SIL Open Font License.
- Body and UI: IBM Plex Mono, self-hosted under the SIL Open Font License.
- Display copy is short, uppercase, and line-broken deliberately.
- Body copy stays compact and factual; labels use the same mono face at smaller sizes.

### Geometry

- Square corners throughout.
- One-pixel rules create rhythm and structure.
- Sections are full-width bands with a restrained `1280px` content rail.
- Repeated items are rows or columns, not floating cards.
- Images are documentary and framed as field evidence, never generic stock decoration.

### Motion

- A single reveal system brings sections in as they enter the viewport.
- Hover states flip row surfaces to mint or rust for a clear, high-contrast response.
- Reduced-motion preferences remove the transitions.

## Page outline

### Home

1. Full-bleed Trey portrait with literal name, concise positioning, and two routes.
2. Signal strip: active projects, days alive, lifetime on-foot miles, current-year workouts.
3. System directory: Folloze GTM, side projects, Elevation Engine, public journal, workouts.
4. Training chapter with real snapshot metrics and the Mount Rainier image.
5. Public field-log summary.
6. Direct booking band.

### Folloze GTM

1. Systems-first masthead and proof strip.
2. Eight system records with problem, impact, stack, and repository boundary.
3. Public Folloze project directory.

### Projects

1. Side-project masthead and category index.
2. Elevation Engine client-work directory.
3. Independent experiments directory.
4. Route into the dedicated Folloze GTM page.

### Training

1. Training masthead and snapshot provenance.
2. Lifetime/year/30-day metrics.
3. Five most recent activities.
4. Four-week, year, and all-time sport totals.
5. Running personal bests.

### Links

1. Compact contact masthead.
2. One large, scannable directory for journal, calendar, profiles, Strava, and GitHub.
3. Direct booking band.

## Guardrails

- Keep production deployment separate from this branch until local desktop/mobile QA is accepted.
- Do not reuse House of Growth logos, client proof, copy, or hero imagery.
- Preserve workout snapshot provenance and do not imply unsupported live API access.
- Keep the October 1, 1995 life counter driven by browser-local Central Time logic.
- New pages should use the existing bands, rules, display type, mono labels, and mint/rust semantics before introducing another component style.
