# replit.md

## Overview

This project is a multi-page personal website for Trey Harnden, hosted at treyharnden.com. The application features pages for Home, Links (shareable link tree), Projects, and Workouts. It serves as both a professional presence and a public operating log.

## Recent Changes

- **Feb 2026**: Refactored from single-page link tree to a multi-page site
- Added sticky navigation bar with active state indicators and mobile hamburger menu
- Centralized all link URLs, milestone dates, and site config in `SITE_CONFIG` dict in `app.py`
- **Mar 2026**: Renamed `/work` to `/projects` with a `/work` redirect, refreshed the nav/home CTA, and expanded the project list on both `/projects` and `/links`
- **Mar 2026**: Reworked `/projects` into a split hero layout with intro copy and a clickable ABM preview on the left, `Folloze Projects` on the right, and separate lower sections for `Elevation Engine Client Work` and `Random Projects`
- **May 2026**: Rebuilt the homepage as the Mountain Operator / Topo Terminal interface, removed `/stats`, removed cannabis tracking, and added `/workouts` plus `/api/workouts` for Strava/Garmin-ready training data.
- Added grouped project inventory:
  - `Folloze Projects`: ABM Playbook Generator, Folloze Link Builder, Folloze Blog
  - `Elevation Engine Client Work`: Elevation Engine, Premium Flooring MKE, High Caliber Tree Service, Epredia Kalamazoo Surplus Demo
  - `Random Projects`: Dialectic Daily
- Added GitHub button to /links
- Added per-page SEO (title, meta description, OpenGraph tags on /links)
- Added /track-click endpoint for link click tracking
- Updated click tracking to bind to all `a[data-link-name]` anchors so non-button links like the ABM screenshot still track correctly

## User Preferences

Preferred communication style: Simple, everyday language.

## Project Architecture

### Routes
- `/` — Mountain Operator / Topo Terminal home page with project route map, basecamp milestones, and workout-ready training status
- `/links` — Link tree page with social links plus current project links
- `/projects` — Project showcase page with:
  - Split hero: intro copy + clickable ABM preview on the left, `Folloze Projects` on the right
  - Lower sections: `Elevation Engine Client Work` and `Random Projects`
- `/work` — Legacy redirect to `/projects`
- `/workouts` — Training log surface designed to sync from Strava and Garmin-connected workouts
- `/api/workouts` — JSON API for recent workout summaries and activities
- `/track-click` — POST endpoint for click tracking
- `/health` — Health check endpoint

### Configuration
All link URLs, milestone dates, Strava profile URL, and site metadata are centralized in `SITE_CONFIG` at the top of `app.py`. Project groupings are driven by the `section` field on each item in `project_links`. Strava OAuth credentials are read from environment variables and rotating tokens are stored in the database.

### Frontend Architecture
- **Template Structure**: Jinja2 base template (`base.html`) with nav bar, extended by page templates (`home.html`, `links.html`, `projects.html`, `workouts.html`)
- **Styling**: Bootstrap 5 dark theme + custom CSS (`static/css/style.css`) with the Mountain Operator terminal system, route-map homepage, project layouts, and workout console
- **JavaScript**: `static/js/main.js` — click tracking on all anchors with `data-link-name` plus Notion embed fallback handling
- **Responsive Design**: Mobile-first with hamburger nav, responsive route cards, and stacked workout rows

### Backend Architecture
- **Framework**: Flask with application factory pattern (`create_app()`)
- **Database**: PostgreSQL (Neon-backed) via `DATABASE_URL` env var, SQLite fallback for dev
- **ORM**: SQLAlchemy with `LinkClick` for click tracking and `IntegrationToken` for rotating OAuth tokens (`models.py`)
- **Server**: Gunicorn with 4 workers, launched via `main.py`
- **Security**: ProxyFix, CORS, secure session cookies, HTTPS enforcement

### File Structure
```
app.py              — Flask app with SITE_CONFIG, routes, and create_app()
main.py             — Gunicorn launcher
models.py           — SQLAlchemy models (LinkClick, IntegrationToken)
templates/
  base.html         — Base layout with nav bar, SEO meta, analytics
  home.html         — Mountain Operator / Topo Terminal home page
  links.html        — Link tree page
  projects.html     — Project showcase page
  workouts.html     — Workout/training log page
static/
  css/style.css     — All custom styles
  js/main.js        — Click tracking and journal embed fallback
  images/           — Profile photo
```

## Deployment Notes

- Production domain: `https://treyharnden.com`
- Canonical projects route: `https://treyharnden.com/projects`
- Linked Vercel project: `treyharndencom-linktree`
- Typical deploy command from repo root: `vercel deploy --prod --yes`
- This repo currently has local changes that have been deployed but not committed yet

## External Dependencies

### Third-Party Services
- **Domain**: Cloudflare DNS/SSL for treyharnden.com
- **Analytics**: Google Analytics (G-FT0YPCYY8N)
- **CDN**: Bootstrap 5.3.0, Font Awesome 6.4.0
- **Journal**: Notion public page embed
- **Workouts**: Strava API via OAuth refresh token; Garmin workout data can appear when Garmin Connect syncs to Strava or through a future approved Garmin/export feed

### Python Libraries
- Flask 3.1.0+, Flask-CORS, Flask-SQLAlchemy 3.1.1+
- SQLAlchemy 2.0.36+, psycopg2-binary
- Gunicorn, Werkzeug, email-validator
