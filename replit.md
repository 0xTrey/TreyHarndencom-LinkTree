# replit.md

## Overview

This project is a multi-page personal website for Trey Harnden, hosted at treyharnden.com. The application features five pages: Home, Links (shareable link tree), Journal (Notion embed), Work (professional links), and Stats (sobriety/milestone trackers). It serves as both a professional presence and a personal accountability tool.

## Recent Changes

- **Feb 2026**: Refactored from single-page link tree to multi-page site with 5 routes (/, /links, /journal, /work, /stats)
- Added sticky navigation bar with active state indicators and mobile hamburger menu
- Centralized all link URLs, milestone dates, and site config in `SITE_CONFIG` dict in `app.py`
- Added Notion iframe embed on /journal with loading state, timeout detection, and fallback banner
- Moved milestone counters from homepage to /stats page with inclusive counting microcopy
- Added GitHub button to /links, /work, and /journal pages
- Added per-page SEO (title, meta description, OpenGraph tags on /links)
- Added /track-click endpoint for link click tracking

## User Preferences

Preferred communication style: Simple, everyday language.

## Project Architecture

### Routes
- `/` — Home page with two CTAs (Journal, Work) and a stats snapshot row
- `/links` — Link tree page with profile, all social links, and GitHub button
- `/journal` — Public journal with Notion iframe embed and fallback link
- `/work` — Professional links (LinkedIn, ABM Playbook, Book A Call, GitHub)
- `/stats` — Personal milestone counters (days of life, alcohol free, cannabis free)
- `/api/sobriety_data` — JSON API for real-time counter updates
- `/track-click` — POST endpoint for click tracking
- `/health` — Health check endpoint

### Configuration
All link URLs, milestone dates, and site metadata are centralized in `SITE_CONFIG` at the top of `app.py`. To change link URLs or add new links, edit this dictionary.

### Frontend Architecture
- **Template Structure**: Jinja2 base template (`base.html`) with nav bar, extended by page templates (`home.html`, `links.html`, `journal.html`, `work.html`, `stats.html`)
- **Styling**: Bootstrap 5 dark theme + custom CSS (`static/css/style.css`) with blue gradient background and button hover animations
- **JavaScript**: `static/js/main.js` — SobrietyTracker class for real-time counter updates (only initializes on /stats), click tracking on all pages, journal iframe timeout detection
- **Responsive Design**: Mobile-first with hamburger nav, responsive grid for stat cards

### Backend Architecture
- **Framework**: Flask with application factory pattern (`create_app()`)
- **Database**: PostgreSQL (Neon-backed) via `DATABASE_URL` env var, SQLite fallback for dev
- **ORM**: SQLAlchemy with `LinkClick` model for click tracking (`models.py`)
- **Server**: Gunicorn with 4 workers, launched via `main.py`
- **Security**: ProxyFix, CORS, secure session cookies, HTTPS enforcement

### File Structure
```
app.py              — Flask app with SITE_CONFIG, routes, and create_app()
main.py             — Gunicorn launcher
models.py           — SQLAlchemy models (LinkClick)
templates/
  base.html         — Base layout with nav bar, SEO meta, analytics
  home.html         — Home page (CTAs + stats snapshot)
  links.html        — Link tree page
  journal.html      — Notion embed page
  work.html         — Professional links page
  stats.html        — Milestone counters page
static/
  css/style.css     — All custom styles
  js/main.js        — Counter updates, click tracking, journal embed
  images/           — Profile photo
```

## External Dependencies

### Third-Party Services
- **Domain**: Cloudflare DNS/SSL for treyharnden.com
- **Analytics**: Google Analytics (G-FT0YPCYY8N)
- **CDN**: Bootstrap 5.3.0, Font Awesome 6.4.0
- **Journal**: Notion public page embed

### Python Libraries
- Flask 3.1.0+, Flask-CORS, Flask-SQLAlchemy 3.1.1+
- SQLAlchemy 2.0.36+, psycopg2-binary
- Gunicorn, Werkzeug, email-validator
