import logging
import os
import json
import subprocess
import base64
import copy
import hashlib
import hmac
import secrets
from pathlib import Path
from urllib import error, parse, request as url_request
from flask import Flask, render_template, request, jsonify, redirect, send_from_directory, url_for, has_app_context, has_request_context, current_app
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime, date, timedelta, timezone
from zoneinfo import ZoneInfo
from sqlalchemy import text

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
US_CENTRAL_TZ = ZoneInfo("America/Chicago")
STRAVA_KEYCHAIN_SERVICE = 'treyharnden.com/strava'
STRAVA_DEFAULT_SCOPE = 'read,activity:read_all'
STRAVA_CACHE_SECONDS = int(os.environ.get('STRAVA_CACHE_SECONDS', '3600'))
STRAVA_ACTIVITY_HISTORY_MAX_PAGES = int(os.environ.get('STRAVA_ACTIVITY_HISTORY_MAX_PAGES', '30'))
WORKOUTS_PAGE_ACTIVITY_LIMIT = 5
WORKOUTS_USE_STATIC_SNAPSHOT = os.environ.get('WORKOUTS_USE_STATIC_SNAPSHOT', 'true').lower() not in {'0', 'false', 'no'}
STRAVA_FOOT_SPORT_TYPES = {'run', 'trailrun', 'virtualrun', 'walk', 'hike'}
STRAVA_WORKOUT_CACHE = {
    'expires_at': 0,
    'data': None,
}
WORKOUTS_SNAPSHOT_PATH = Path(__file__).resolve().parent / 'data' / 'workouts_snapshot.json'

SITE_CONFIG = {
    'name': 'Trey Harnden',
    'bio': 'Sup, I\'m Trey. Huge fan of public parks, all things mountains, and make you sweat spicy food. I am a software newb using AI to build tools and agents for B2B sales and ABM. Generally a huge fan of building/learning in public, so check out my links page to see what I am building or where I am adventuring.',
    'avatar': 'images/trey-rainier-headshot.jpeg',
    'github_url': 'https://github.com/0xTrey',
    'notion_embed_url': 'https://harnden.notion.site/My-Second-Brain-a2bcac8bd3424b6bbd838c709dc1bb73',
    'strava_profile_url': 'https://www.strava.com/athletes/34654738',
    'social_links': [
        {'name': 'Public Journal', 'url': 'https://harnden.notion.site/My-Second-Brain-a2bcac8bd3424b6bbd838c709dc1bb73', 'icon': 'fas fa-book-open', 'category': 'personal'},
        {'name': 'Book A Call', 'url': 'https://app.reclaim.ai/m/harnden', 'icon': 'fas fa-calendar-alt', 'category': 'professional'},
        {'name': 'X (Twitter)', 'url': 'https://x.com/Trey_Harnden', 'icon': 'x-logo', 'category': 'social'},
        {'name': 'LinkedIn', 'url': 'https://www.linkedin.com/in/treyharnden/', 'icon': 'fab fa-linkedin', 'category': 'professional'},
        {'name': 'Strava', 'url': 'https://www.strava.com/athletes/34654738', 'icon': 'fab fa-strava', 'category': 'social'},
    ],
    'project_links': [
        {'name': 'ABM Playbook Generator', 'url': 'https://abm-playbook.folloze.com/', 'icon': 'fas fa-rocket', 'section': 'folloze'},
        {'name': 'Folloze Skills', 'url': 'https://github.com/0xTrey/Folloze-Skills', 'icon': 'fas fa-toolbox', 'section': 'folloze'},
        {'name': 'Folloze Link Builder', 'url': 'https://folloze-link-builder.vercel.app/', 'icon': 'fas fa-link', 'section': 'folloze'},
        {'name': 'Folloze Blog', 'url': 'https://www.folloze-blog.com/', 'icon': 'fas fa-newspaper', 'section': 'folloze'},
        {'name': 'Outbound Email Engine', 'url': '/projects/folloze-outbound-intent-loop', 'icon': 'fas fa-project-diagram', 'section': 'folloze'},
        {'name': 'Elevation Engine', 'url': 'https://www.elevationengine.co/', 'icon': 'fas fa-mountain', 'section': 'elevation-engine'},
        {'name': 'Premium Flooring MKE', 'url': 'https://www.premiumflooringmke.com/', 'icon': 'fas fa-border-all', 'section': 'elevation-engine'},
        {'name': 'High Caliber Tree Service', 'url': 'https://highcalibertreeservice.com/', 'icon': 'fas fa-tree', 'section': 'elevation-engine'},
        {'name': 'All Seasons Website Rebuild', 'url': 'https://all-seasons-landscape-solutions.vercel.app/', 'icon': 'fas fa-seedling', 'section': 'elevation-engine'},
        {'name': 'All Seasons Voice Agent: +1 (414) 501-5097', 'url': 'tel:+14145015097', 'icon': 'fas fa-phone-volume', 'section': 'elevation-engine'},
        {'name': 'Epredia Kalamazoo Surplus Demo', 'url': 'https://epredia-kalamazoo-surplus-demo.vercel.app/', 'icon': 'fas fa-microscope', 'section': 'elevation-engine'},
        {'name': 'Dialectic Daily (Sunset)', 'url': 'https://dialectic-daily.com/', 'icon': 'fas fa-lightbulb', 'section': 'random'},
    ],
    'milestones': {
        'birth_date': date(1995, 10, 1),
        'alcohol_free_date': date(2023, 1, 22),
    },
}

AI_GTM_PROJECTS = [
    {
        'number': '01',
        'name': 'Folloze Content Engine',
        'category': 'AEO / GEO pipeline',
        'icon': 'fas fa-newspaper',
        'summary': 'A Python publishing system that turns scheduled product-marketing topics into researched, optimized Folloze Insights articles with HTML, JSON-LD, scoring, and deployment artifacts.',
        'impact': 'It moved content from one-off drafting into a daily engine with canary checks, auto-promotion, deployment verification, and same-day social briefs for downstream distribution.',
        'stack': ['Python', 'LLMs', 'JSON-LD', 'Vercel'],
        'repo_url': 'https://github.com/0xTrey/folloze-content-engine',
        'repo_label': 'Public GitHub',
        'track_name': 'GitHub: Folloze Content Engine',
    },
    {
        'number': '02',
        'name': 'Folloze AEO/GEO Blog Engine',
        'category': 'LLM citation surface',
        'icon': 'fas fa-sitemap',
        'summary': 'A machine-first content pipeline for folloze-abm.com focused on rankings, alternatives, comparisons, glossary, and methodology pages.',
        'impact': 'It extends discoverability beyond blog posts into structured citation surfaces for ChatGPT, Perplexity, Gemini, Claude, Google AI Overviews, and traditional search.',
        'stack': ['Python', 'Schema', 'Vercel', 'Cloudflare'],
        'repo_url': None,
        'repo_label': 'Local/internal project',
        'repo_icon': 'fas fa-folder-tree',
    },
    {
        'number': '03',
        'name': 'Folloze LinkedIn Engine',
        'category': 'Executive content system',
        'icon': 'fab fa-linkedin',
        'summary': 'A downstream adaptation layer that reads the same-day Folloze social brief and turns it into role-specific LinkedIn drafts for individual stakeholders.',
        'impact': 'It preserves the blog as the source of truth while applying voice, cadence, audience, feedback history, and post tracking so the output does not feel like generic AI social copy.',
        'stack': ['Docs', 'Gmail', 'LLMs', 'Content Ops'],
        'repo_url': 'https://github.com/0xTrey/folloze-linkedin-engine',
        'repo_label': 'Public GitHub',
        'track_name': 'GitHub: Folloze LinkedIn Engine',
    },
    {
        'number': '04',
        'name': 'Folloze Outbound Engine',
        'category': 'AI SDR operations',
        'icon': 'fas fa-route',
        'summary': 'An API-driven outbound loop across Apollo, email reveal, account research, bounded AI personalization, Smartlead enrollment, Salesforce context, Folloze engagement data, and Neon state.',
        'impact': 'It replaced manual list building and ad hoc copy with launch-readiness checks, freshness gates, pause controls, incident logs, delivery telemetry, and automated blocker repair.',
        'stack': ['Apollo', 'Smartlead', 'Salesforce', 'Neon'],
        'repo_url': 'https://github.com/0xTrey/folloze-outbound-engine-public',
        'repo_label': 'Public GitHub',
        'track_name': 'GitHub: Folloze Outbound Engine Public',
    },
    {
        'number': '05',
        'name': 'Post-Call Deal Room Autopilot',
        'category': 'Buyer-safe follow-up',
        'icon': 'fas fa-door-open',
        'summary': 'A seller-reviewed package generator that ingests call notes, Granola/Zoom recaps, CRM summaries, email context, attendees, and approved assets.',
        'impact': 'It produces an internal deal brief, buyer-safe deal-room plan, follow-up draft, approval checklist, and analytics plan with fact classification and leak checks before anything faces a buyer.',
        'stack': ['Granola', 'Zoom', 'Drive', 'Folloze API'],
        'repo_url': None,
        'repo_label': 'Local/internal project',
        'repo_icon': 'fas fa-folder-tree',
    },
    {
        'number': '06',
        'name': 'Timely Extractor',
        'category': 'Local activity ledger',
        'icon': 'fas fa-wave-square',
        'summary': 'A local-first collector for frontmost app focus, shell commands, file activity, screenshot/OCR metadata, derived sessions, and daily action summaries.',
        'impact': 'It creates the instrumentation layer needed to discover repeatable work, generate weekly automation recommendations, and ground agent follow-up in actual machine activity.',
        'stack': ['macOS', 'LaunchAgents', 'OCR', 'SQLite'],
        'repo_url': None,
        'repo_label': 'Private GitHub repo',
        'repo_icon': 'fas fa-lock',
    },
    {
        'number': '07',
        'name': 'Folloze Automated Demo Environment Builder',
        'category': 'Demo environment builder',
        'icon': 'fas fa-layer-group',
        'summary': 'An automated builder workflow for spinning up customer-specific Folloze demo environments from account context, research notes, self-contained page templates, and campaign sheet metadata.',
        'impact': 'It turns one-off demo-board creation into a repeatable factory with local QA scripts, Folloze MCP save/publish steps, and tracker updates for accounts like Stratasys, Aprio, AlphaSense, Invoca, DigiCert, Caterpillar, and Bank of America.',
        'stack': ['Folloze MCP', 'HTML/CSS/JS', 'QA Automation', 'Sheets'],
        'repo_url': None,
        'repo_label': 'Private GitHub repo',
        'repo_icon': 'fas fa-lock',
    },
    {
        'number': '08',
        'name': 'Folloze Sales Automation Stack',
        'category': 'AE operating system',
        'icon': 'fas fa-briefcase',
        'summary': 'A personal sales automation stack for deal research, meeting intelligence, Granola-grounded follow-up drafts, daily account briefings, Salesforce validation, and Google Doc deal notes.',
        'impact': 'It turns scattered account signals and meeting context into seller-ready briefs, follow-up emails, prep notes, and resource-center continuity while preserving approval gates for sends.',
        'stack': ['OpenClaw', 'Codex', 'Granola', 'Salesforce'],
        'repo_url': None,
        'repo_label': 'Private GitHub repo',
        'repo_icon': 'fas fa-lock',
    },
]

CSP_POLICY = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://www.google-analytics.com https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline' https://cdn.replit.com https://cdnjs.cloudflare.com; "
    "img-src 'self' data: https:; "
    "font-src 'self' https://cdnjs.cloudflare.com data:; "
    "connect-src 'self' https://www.google-analytics.com https://region1.google-analytics.com; "
    "frame-src https://harnden.notion.site; "
    "object-src 'none'; "
    "base-uri 'self'; "
    "form-action 'self'; "
    "frame-ancestors 'none'; "
    "upgrade-insecure-requests"
)

TRACKABLE_LINK_NAMES = {
    link["name"] for link in SITE_CONFIG["social_links"] + SITE_CONFIG["project_links"] if link.get("name")
}
TRACKABLE_LINK_NAMES.add("GitHub")
TRACKABLE_LINK_NAMES.add("Workouts")
TRACKABLE_LINK_NAMES.add("Folloze GTM")
TRACKABLE_LINK_NAMES.add("Side Projects")
TRACKABLE_LINK_NAMES.update(
    project["track_name"] for project in AI_GTM_PROJECTS if project.get("track_name")
)


def calculate_days_since(start_date):
    today = datetime.now(US_CENTRAL_TZ).date()
    return (today - start_date).days + 1


def get_milestone_data():
    milestones = SITE_CONFIG['milestones']
    return {
        'life_start_date': milestones['birth_date'].isoformat(),
        'days_of_life': calculate_days_since(milestones['birth_date']),
        'days_alcohol_free': calculate_days_since(milestones['alcohol_free_date']),
    }


def format_duration(seconds):
    if not seconds:
        return '0m'
    hours, remainder = divmod(int(seconds), 3600)
    minutes = remainder // 60
    if hours:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def format_distance_miles(meters):
    return f"{(float(meters or 0) / 1609.344):.1f} mi"


def format_elevation_feet(meters):
    return f"{round(float(meters or 0) * 3.28084):,} ft"


def format_miles_whole(meters):
    return f"{round(float(meters or 0) / 1609.344):,} mi"


def request_json(url, method='GET', headers=None, data=None, timeout=8):
    payload = None
    request_headers = headers or {}
    if data is not None:
        payload = parse.urlencode(data).encode('utf-8')
        request_headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            **request_headers,
        }
    req = url_request.Request(url, data=payload, headers=request_headers, method=method)
    with url_request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode('utf-8'))


def clear_strava_workout_cache():
    STRAVA_WORKOUT_CACHE['expires_at'] = 0
    STRAVA_WORKOUT_CACHE['data'] = None


def get_strava_client_config():
    return (
        get_strava_config_value('STRAVA_CLIENT_ID', 'client_id'),
        get_strava_config_value('STRAVA_CLIENT_SECRET', 'client_secret'),
    )


def get_strava_redirect_uri():
    configured_uri = os.environ.get('STRAVA_REDIRECT_URI')
    if configured_uri:
        return configured_uri
    return url_for('strava_callback', _external=True)


def make_strava_state():
    secret = current_app.config.get('SECRET_KEY') or 'strava-local'
    if isinstance(secret, str):
        secret = secret.encode('utf-8')
    issued_at = str(int(datetime.now(timezone.utc).timestamp()))
    nonce = secrets.token_urlsafe(16)
    payload = f"{issued_at}:{nonce}"
    signature = hmac.new(secret, payload.encode('utf-8'), hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(f"{payload}:{signature}".encode('utf-8')).decode('utf-8')


def is_valid_strava_state(state, max_age_seconds=900):
    if not state:
        return False
    try:
        decoded = base64.urlsafe_b64decode(state.encode('utf-8')).decode('utf-8')
        issued_at, nonce, signature = decoded.split(':', 2)
        payload = f"{issued_at}:{nonce}"
        secret = current_app.config.get('SECRET_KEY') or 'strava-local'
        if isinstance(secret, str):
            secret = secret.encode('utf-8')
        expected = hmac.new(secret, payload.encode('utf-8'), hashlib.sha256).hexdigest()
        age = int(datetime.now(timezone.utc).timestamp()) - int(issued_at)
        return hmac.compare_digest(signature, expected) and 0 <= age <= max_age_seconds
    except Exception:
        return False


def get_local_strava_connect_url():
    if not has_request_context():
        return None
    return url_for('strava_connect')


def get_keychain_strava_value(account):
    if not account or os.name != 'posix' or not os.path.exists('/usr/bin/security'):
        return None
    try:
        result = subprocess.run(
            [
                '/usr/bin/security',
                'find-generic-password',
                '-s',
                STRAVA_KEYCHAIN_SERVICE,
                '-a',
                account,
                '-w',
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=3,
            check=False,
        )
    except Exception as exc:
        logger.debug(f"Unable to read Strava {account} from Keychain: {str(exc)}")
        return None

    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def set_keychain_strava_value(account, value):
    if not account or not value or os.name != 'posix' or not os.path.exists('/usr/bin/security'):
        return False
    try:
        result = subprocess.run(
            [
                '/usr/bin/security',
                'add-generic-password',
                '-U',
                '-s',
                STRAVA_KEYCHAIN_SERVICE,
                '-a',
                account,
                '-w',
                str(value),
                '-T',
                '/usr/bin/security',
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=3,
            check=False,
        )
        return result.returncode == 0
    except Exception as exc:
        logger.debug(f"Unable to update Strava {account} in Keychain: {str(exc)}")
        return False


def get_strava_config_value(env_name, keychain_account):
    return os.environ.get(env_name) or get_keychain_strava_value(keychain_account)


def parse_strava_expiry(raw_value):
    if not raw_value:
        return None
    try:
        return int(raw_value)
    except (TypeError, ValueError):
        pass
    try:
        return int(datetime.fromisoformat(str(raw_value).replace('Z', '+00:00')).timestamp())
    except ValueError:
        return None


def get_keychain_strava_token():
    return {
        'access_token': get_keychain_strava_value('access_token'),
        'refresh_token': get_keychain_strava_value('refresh_token'),
        'expires_at': parse_strava_expiry(get_keychain_strava_value('access_token_expires_at')),
        'scope': get_keychain_strava_value('scope'),
    }


def save_keychain_strava_token(token_data):
    if not token_data:
        return
    key_map = {
        'access_token': 'access_token',
        'refresh_token': 'refresh_token',
        'expires_at': 'access_token_expires_at',
        'scope': 'scope',
    }
    for token_key, keychain_account in key_map.items():
        value = token_data.get(token_key)
        if value:
            set_keychain_strava_value(keychain_account, value)


def get_strava_scope():
    return os.environ.get('STRAVA_SCOPE') or get_keychain_strava_value('scope')


def get_saved_strava_token():
    if not has_app_context():
        return None
    try:
        from models import IntegrationToken
        return IntegrationToken.get_service('strava')
    except Exception as exc:
        logger.warning(f"Unable to load saved Strava token: {str(exc)}")
        return None


def save_strava_token(token_data):
    save_keychain_strava_token(token_data)
    clear_strava_workout_cache()
    try:
        from models import IntegrationToken
        return IntegrationToken.upsert_service(
            'strava',
            access_token=token_data.get('access_token'),
            refresh_token=token_data.get('refresh_token'),
            expires_at=token_data.get('expires_at'),
        )
    except Exception as exc:
        logger.warning(f"Unable to persist refreshed Strava token: {str(exc)}")
        return None


def get_strava_access_token():
    client_id, client_secret = get_strava_client_config()
    saved_token = get_saved_strava_token()
    keychain_token = get_keychain_strava_token()
    now = int(datetime.now(timezone.utc).timestamp())

    if saved_token and saved_token.access_token and saved_token.expires_at and saved_token.expires_at > now + 600:
        return saved_token.access_token, None

    if keychain_token['access_token'] and keychain_token['expires_at'] and keychain_token['expires_at'] > now + 600:
        return keychain_token['access_token'], None

    refresh_token = (
        saved_token.refresh_token if saved_token and saved_token.refresh_token
        else keychain_token['refresh_token'] or os.environ.get('STRAVA_REFRESH_TOKEN')
    )
    if client_id and client_secret and refresh_token:
        try:
            token_data = request_json(
                'https://www.strava.com/oauth/token',
                method='POST',
                data={
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'grant_type': 'refresh_token',
                    'refresh_token': refresh_token,
                },
            )
            save_strava_token(token_data)
            return token_data.get('access_token'), None
        except error.HTTPError as exc:
            return None, f"Strava token refresh failed with HTTP {exc.code}."
        except Exception as exc:
            return None, f"Strava token refresh failed: {str(exc)}"

    access_token = get_strava_config_value('STRAVA_ACCESS_TOKEN', 'access_token')
    if access_token:
        return access_token, None

    return None, 'Training feed is ready; backend sync will populate recent activity.'


def normalize_strava_activity(activity):
    activity_id = activity.get('id')
    start_date = activity.get('start_date_local') or activity.get('start_date')
    date_label = 'recent'
    if start_date:
        try:
            date_label = datetime.fromisoformat(start_date.replace('Z', '+00:00')).strftime('%b %-d')
        except ValueError:
            date_label = start_date[:10]

    external_id = activity.get('external_id') or ''
    device_name = activity.get('device_name') or ''
    device_label = device_name or ('Garmin' if 'garmin' in external_id.lower() else '')
    return {
        'name': activity.get('name') or 'Workout',
        'sport_type': activity.get('sport_type') or activity.get('type') or 'Workout',
        'date': date_label,
        'distance': format_distance_miles(activity.get('distance')),
        'duration': format_duration(activity.get('moving_time') or activity.get('elapsed_time')),
        'elevation': format_elevation_feet(activity.get('total_elevation_gain')),
        'device': device_label,
        'url': f"https://www.strava.com/activities/{activity_id}" if activity_id else SITE_CONFIG['strava_profile_url'],
    }


def get_default_workout_data(source_note=None):
    return {
        'connected': False,
        'source': 'Strava / Garmin training display',
        'source_note': source_note or 'Backend sync will populate this display after Strava and Garmin-connected activity are available.',
        'connect_url': None,
        'summary': {
            'lifetime_foot_miles': 'pending',
            'lifetime_workouts': 'pending',
            'lifetime_run_miles': 'pending',
            'workouts_year': 'pending',
            'workouts_30': 'pending',
            'distance_30': 'pending',
            'time_30': 'pending',
        },
        'year_label': str(datetime.now(US_CENTRAL_TZ).year),
        'activities': [],
        'strava_profile_url': SITE_CONFIG['strava_profile_url'],
    }


DEFAULT_STATIC_WORKOUT_SNAPSHOT = {
    'connected': True,
    'snapshot': True,
    'source': 'Training snapshot',
    'source_note': 'Visible Strava profile stats captured on July 22, 2026 from an authenticated browser session. Hike was not exposed in the profile tabs, so on-foot totals currently reflect visible Walk + Run only.',
    'connect_url': None,
    'summary': {
        'lifetime_foot_miles': '7,541.4 mi',
        'lifetime_workouts': '3,155',
        'lifetime_run_miles': '2,837.6 mi',
        'workouts_year': '422',
        'workouts_30': '54',
        'distance_30': '136.0 mi',
        'time_30': '43h 54m',
    },
    'year_label': '2026',
    'activities': [
        {
            'date': 'Jul 22',
            'name': 'Morning Walk',
            'sport_type': 'Walk',
            'device': '',
            'distance': '2.46 mi',
            'duration': '46m 37s',
            'elevation': '—',
            'url': 'https://strava.com/activities/19416855943',
        },
        {
            'date': 'Jul 21',
            'name': 'Afternoon Walk',
            'sport_type': 'Walk',
            'device': '',
            'distance': '1.40 mi',
            'duration': '31m 9s',
            'elevation': '—',
            'url': 'https://strava.com/activities/19409642381',
        },
        {
            'date': 'Jul 21',
            'name': 'Lunch Walk',
            'sport_type': 'Walk',
            'device': '',
            'distance': '1.00 mi',
            'duration': '20m 52s',
            'elevation': '—',
            'url': 'https://strava.com/activities/19406175729',
        },
        {
            'date': 'Jul 21',
            'name': 'Morning Walk',
            'sport_type': 'Walk',
            'device': '',
            'distance': '3.25 mi',
            'duration': '1h 6m',
            'elevation': '—',
            'url': 'https://strava.com/activities/19403672958',
        },
        {
            'date': 'Jul 21',
            'name': 'Morning Weight Training',
            'sport_type': 'Weight Training',
            'device': '',
            'distance': '—',
            'duration': '26m 53s',
            'elevation': '—',
            'url': 'https://strava.com/activities/19401932069',
        },
    ],
    'strava_profile_url': SITE_CONFIG['strava_profile_url'],
    'stat_groups': [
        {
            'name': 'Running',
            'icon': 'fas fa-shoe-prints',
            'recent': [
                {'label': 'Activities / Week', 'value': '4'},
                {'label': 'Avg Distance / Week', 'value': '12.1 mi'},
                {'label': 'Avg Time / Week', 'value': '2h 8m'},
                {'label': 'Elev Gain / Week', 'value': '200 ft'},
            ],
            'year': [
                {'label': 'Activities', 'value': '75'},
                {'label': 'Distance', 'value': '264.2 mi'},
                {'label': 'Time', 'value': '45h 47m'},
                {'label': 'Elev Gain', 'value': '5,095 ft'},
            ],
            'all_time': [
                {'label': 'Activities', 'value': '577'},
                {'label': 'Distance', 'value': '2,837.6 mi'},
                {'label': 'Time', 'value': '487h 47m'},
                {'label': 'Elev Gain', 'value': '147,141 ft'},
            ],
        },
        {
            'name': 'Walking',
            'icon': 'fas fa-person-walking',
            'recent': [
                {'label': 'Activities / Week', 'value': '11'},
                {'label': 'Avg Distance / Week', 'value': '21.9 mi'},
                {'label': 'Avg Time / Week', 'value': '7h 39m'},
                {'label': 'Elev Gain / Week', 'value': '267 ft'},
            ],
            'year': [
                {'label': 'Activities', 'value': '274'},
                {'label': 'Distance', 'value': '406.8 mi'},
                {'label': 'Time', 'value': '148h 59m'},
                {'label': 'Elev Gain', 'value': '4,715 ft'},
            ],
            'all_time': [
                {'label': 'Activities', 'value': '1,959'},
                {'label': 'Distance', 'value': '4,703.8 mi'},
                {'label': 'Time', 'value': '1,597h 50m'},
                {'label': 'Elev Gain', 'value': '234,645 ft'},
            ],
        },
        {
            'name': 'Weight Training',
            'icon': 'fas fa-dumbbell',
            'recent': [
                {'label': 'Activities / Week', 'value': '2'},
                {'label': 'Avg Time / Week', 'value': '1h 10m'},
            ],
            'year': [
                {'label': 'Activities', 'value': '72'},
                {'label': 'Time', 'value': '59h 19m'},
            ],
            'all_time': [
                {'label': 'Activities', 'value': '555'},
                {'label': 'Time', 'value': '568h 59m'},
            ],
        },
        {
            'name': 'Ride',
            'icon': 'fas fa-bicycle',
            'recent': [
                {'label': 'Activities / Week', 'value': '0'},
                {'label': 'Avg Distance / Week', 'value': '0.2 mi'},
                {'label': 'Avg Time / Week', 'value': '1m 36s'},
                {'label': 'Elev Gain / Week', 'value': '5 ft'},
            ],
            'year': [
                {'label': 'Activities', 'value': '1'},
                {'label': 'Distance', 'value': '1.0 mi'},
                {'label': 'Time', 'value': '6m 26s'},
                {'label': 'Elev Gain', 'value': '20 ft'},
            ],
            'all_time': [
                {'label': 'Activities', 'value': '64'},
                {'label': 'Distance', 'value': '478.2 mi'},
                {'label': 'Time', 'value': '38h 42m'},
                {'label': 'Elev Gain', 'value': '6,072 ft'},
            ],
        },
    ],
    'best_efforts': [
        {'label': '400m', 'value': '1:23'},
        {'label': '1/2 mile', 'value': '3:28'},
        {'label': '1K', 'value': '4:21'},
        {'label': '1 mile', 'value': '7:07'},
        {'label': '2 mile', 'value': '14:34'},
        {'label': '5K', 'value': '23:01'},
        {'label': '10K', 'value': '47:43'},
        {'label': '15K', 'value': '1:16:27'},
        {'label': '10 mile', 'value': '1:22:04'},
        {'label': '20K', 'value': '1:43:07'},
        {'label': 'Half-Marathon', 'value': '1:49:11'},
        {'label': '30K', 'value': '2:41:09'},
        {'label': 'Marathon', 'value': '3:48:06'},
    ],
}


def get_static_workout_snapshot():
    snapshot = copy.deepcopy(DEFAULT_STATIC_WORKOUT_SNAPSHOT)
    if not WORKOUTS_SNAPSHOT_PATH.exists():
        return snapshot
    try:
        file_snapshot = json.loads(WORKOUTS_SNAPSHOT_PATH.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning(f"Unable to load workout snapshot file: {str(exc)}")
        return snapshot
    if not isinstance(file_snapshot, dict):
        logger.warning("Workout snapshot file is not a JSON object; using built-in fallback.")
        return snapshot
    return merge_workout_snapshot(snapshot, file_snapshot)


def merge_workout_snapshot(base_snapshot, override_snapshot):
    merged = copy.deepcopy(base_snapshot)
    for key, value in override_snapshot.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_workout_snapshot(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def with_activity_limit(workout_data, limit):
    limited = copy.deepcopy(workout_data)
    limited['activities'] = limited.get('activities', [])[:limit]
    return limited


def get_strava_scope_values():
    scope = get_strava_scope() or ''
    return {value.strip() for value in scope.replace(' ', ',').split(',') if value.strip()}


def has_strava_activity_scope():
    return not get_strava_scope_values().isdisjoint({'activity:read', 'activity:read_all'})


def request_strava_activities(access_token, after=None, before=None, per_page=200, max_pages=1):
    activities = []
    for page in range(1, max_pages + 1):
        params_data = {'page': page, 'per_page': per_page}
        if after is not None:
            params_data['after'] = int(after)
        if before is not None:
            params_data['before'] = int(before)
        params = parse.urlencode(params_data)
        page_data = request_json(
            f"https://www.strava.com/api/v3/athlete/activities?{params}",
            headers={'Authorization': f"Bearer {access_token}"},
        )
        if not isinstance(page_data, list) or not page_data:
            break
        activities.extend(page_data)
        if len(page_data) < per_page:
            break
    return activities


def request_strava_athlete(access_token):
    return request_json(
        "https://www.strava.com/api/v3/athlete",
        headers={'Authorization': f"Bearer {access_token}"},
    )


def request_strava_athlete_stats(access_token, athlete_id):
    return request_json(
        f"https://www.strava.com/api/v3/athletes/{athlete_id}/stats",
        headers={'Authorization': f"Bearer {access_token}"},
    )


def get_strava_year_start_epoch():
    now = datetime.now(US_CENTRAL_TZ)
    start = datetime(now.year, 1, 1, tzinfo=US_CENTRAL_TZ)
    return int(start.astimezone(timezone.utc).timestamp())


def get_activity_start_datetime(activity):
    start_date = activity.get('start_date') or activity.get('start_date_local')
    if not start_date:
        return None
    try:
        parsed = datetime.fromisoformat(str(start_date).replace('Z', '+00:00'))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=US_CENTRAL_TZ)
    return parsed.astimezone(timezone.utc)


def get_activity_sport_key(activity):
    sport_type = activity.get('sport_type') or activity.get('type') or ''
    return str(sport_type).replace('_', '').replace(' ', '').lower()


def is_foot_activity(activity):
    return get_activity_sport_key(activity) in STRAVA_FOOT_SPORT_TYPES


def filter_activities_since(activities, after_datetime):
    return [
        activity for activity in activities
        if (get_activity_start_datetime(activity) or datetime.min.replace(tzinfo=timezone.utc)) >= after_datetime
    ]


def sort_activities_by_start_desc(activities):
    return sorted(
        activities,
        key=lambda activity: get_activity_start_datetime(activity) or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )


def get_workout_data_uncached():
    if WORKOUTS_USE_STATIC_SNAPSHOT:
        return get_static_workout_snapshot()

    access_token, token_error = get_strava_access_token()
    if token_error:
        logger.info(token_error)
    snapshot_data = get_static_workout_snapshot()
    if not access_token:
        return snapshot_data

    try:
        all_activities = request_strava_activities(
            access_token,
            after=0,
            per_page=200,
            max_pages=STRAVA_ACTIVITY_HISTORY_MAX_PAGES,
        )
    except error.HTTPError as exc:
        if exc.code in (401, 403) and not has_strava_activity_scope():
            logger.info("Strava activity scope is unavailable; using static workout snapshot.")
        else:
            logger.info(f"Strava activities request failed with HTTP {exc.code}.")
        return snapshot_data
    except Exception as exc:
        logger.info(f"Strava activities request failed: {str(exc)}")
        return snapshot_data

    sorted_activities = sort_activities_by_start_desc(all_activities)
    now = datetime.now(timezone.utc)
    year_start = datetime.fromtimestamp(get_strava_year_start_epoch(), tz=timezone.utc)
    recent_start = now - timedelta(days=30)
    year_activities = filter_activities_since(sorted_activities, year_start)
    activities = filter_activities_since(sorted_activities, recent_start)
    foot_activities = [activity for activity in sorted_activities if is_foot_activity(activity)]
    recent_foot_activities = [activity for activity in activities if is_foot_activity(activity)]
    lifetime_foot_distance = sum(float(activity.get('distance') or 0) for activity in foot_activities)
    total_distance = sum(float(activity.get('distance') or 0) for activity in recent_foot_activities)
    total_time = sum(int(activity.get('moving_time') or activity.get('elapsed_time') or 0) for activity in activities)
    has_garmin = any(
        'garmin' in str(activity.get('external_id', '')).lower()
        or 'garmin' in str(activity.get('device_name', '')).lower()
        for activity in sorted_activities[:50]
    )
    stats_note = 'Lifetime foot miles include Strava Run, Walk, Hike, Trail Run, and Virtual Run activities.'
    if len(all_activities) >= STRAVA_ACTIVITY_HISTORY_MAX_PAGES * 200:
        stats_note += ' Activity history reached the configured page limit.'
    return {
        'connected': True,
        'source': 'Strava + Garmin device data' if has_garmin else 'Strava',
        'source_note': stats_note,
        'connect_url': None,
        'summary': {
            'lifetime_foot_miles': format_miles_whole(lifetime_foot_distance),
            'lifetime_workouts': f"{len(sorted_activities):,}",
            'lifetime_run_miles': format_miles_whole(lifetime_foot_distance),
            'workouts_year': f"{len(year_activities):,}",
            'workouts_30': str(len(activities)),
            'distance_30': format_distance_miles(total_distance),
            'time_30': format_duration(total_time),
        },
        'year_label': str(datetime.now(US_CENTRAL_TZ).year),
        'activities': [normalize_strava_activity(activity) for activity in activities],
        'strava_profile_url': SITE_CONFIG['strava_profile_url'],
    }


def get_workout_data(limit=6):
    now = int(datetime.now(timezone.utc).timestamp())
    if STRAVA_WORKOUT_CACHE['data'] and STRAVA_WORKOUT_CACHE['expires_at'] > now:
        return with_activity_limit(STRAVA_WORKOUT_CACHE['data'], limit)

    workout_data = get_workout_data_uncached()
    STRAVA_WORKOUT_CACHE['data'] = workout_data
    STRAVA_WORKOUT_CACHE['expires_at'] = now + STRAVA_CACHE_SECONDS
    return with_activity_limit(workout_data, limit)


def get_operator_home_data():
    project_links = {link['name']: link for link in SITE_CONFIG['project_links']}
    milestone_data = get_milestone_data()
    workout_data = get_workout_data(limit=3)
    training_value = (
        f"{workout_data['summary']['workouts_year']} workouts / {workout_data['year_label']}"
        if workout_data['connected'] else 'Strava/Garmin ready'
    )
    return {
        'status_items': [
            {
                'label': 'Shipping',
                'value': f"{len(SITE_CONFIG['project_links'])} public projects",
                'tone': 'green',
            },
            {
                'label': 'Learning',
                'value': 'AI + GTM systems',
                'tone': 'amber',
            },
            {
                'label': 'Training',
                'value': training_value,
                'tone': 'orange',
            },
            {
                'label': 'Exploring',
                'value': 'public parks + mountains',
                'tone': 'green',
            },
        ],
        'nodes': [
            {
                'key': 'folloze-gtm',
                'name': 'Folloze GTM Engineering',
                'track_name': 'Folloze GTM',
                'description': 'AI-assisted content, outbound, demo, and seller systems.',
                'url': '/folloze-gtm',
                'icon': 'fas fa-diagram-project',
            },
            {
                'key': 'side-projects',
                'name': 'Side Projects',
                'track_name': 'Side Projects',
                'description': 'Client builds, experiments, and independent projects.',
                'url': '/projects',
                'icon': 'fas fa-compass-drafting',
            },
            {
                'key': 'elevation-engine',
                'name': 'Elevation Engine',
                'track_name': 'Elevation Engine',
                'description': 'Client sites, demos, and AI-assisted delivery work.',
                'url': project_links['Elevation Engine']['url'],
                'icon': 'fas fa-mountain',
            },
            {
                'key': 'public-journal',
                'name': 'Public Journal',
                'track_name': 'Public Journal',
                'description': 'Notes, experiments, lessons learned, and field logs.',
                'url': SITE_CONFIG['notion_embed_url'],
                'icon': 'fas fa-book-open',
            },
            {
                'key': 'workouts',
                'name': 'Workouts',
                'track_name': 'Workouts',
                'description': 'Training snapshot, PRs, and public activity widgets.',
                'url': '/workouts',
                'icon': 'fas fa-person-running',
            },
        ],
        'logs': [
            {
                'date': 'active',
                'text': 'Building AI-assisted Folloze GTM systems and public experiments.',
            },
            {
                'date': 'projects',
                'text': 'Folloze GTM, Elevation Engine work, and side projects stay easy to reach.',
            },
            {
                'date': 'journal',
                'text': 'Operating notes live in the public second brain.',
            },
            {
                'date': 'training',
                'text': workout_data['source_note'] or f"Workout snapshot is available from {workout_data['source']}.",
            },
        ],
        'milestone_data': milestone_data,
        'workout_data': workout_data,
    }


def create_app():
    app = Flask(__name__)
    logger.info("Flask application instance created")

    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    app.config.update(
        SECRET_KEY=os.environ.get('FLASK_SECRET_KEY', os.urandom(24)),
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PREFERRED_URL_SCHEME='https'
    )

    env = os.environ.get('FLASK_ENV', 'development')
    logger.info(f"Application environment: {env}")

    logger.info("Checking DATABASE_URL environment variable...")
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            logger.warning("DATABASE_URL not set, falling back to SQLite")
            database_url = 'sqlite:///:memory:'
            app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
                'pool_pre_ping': True,
                'pool_recycle': 300
            }
        else:
            db_type = database_url.split('://')[0] if '://' in database_url else 'unknown'
            db_host = database_url.split('@')[1].split('/')[0] if '@' in database_url else 'unknown'
            logger.info(f"Database configuration: type={db_type}, host={db_host}")
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)

            app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
                'pool_size': 5,
                'max_overflow': 10,
                'pool_timeout': 30,
                'pool_pre_ping': True,
                'pool_recycle': 300,
                'connect_args': {
                    'connect_timeout': 10,
                    'application_name': 'flask_app'
                }
            }

        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    except Exception as e:
        logger.error(f"Error configuring database: {str(e)}")
        database_url = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300
        }
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    from models import db
    db.init_app(app)

    with app.app_context():
        try:
            retries = 3
            connected = False
            for attempt in range(retries):
                try:
                    db.session.execute(text('SELECT 1'))
                    db.session.commit()
                    logger.info("Database connection verified successfully")
                    connected = True
                    break
                except Exception as conn_error:
                    if attempt == retries - 1:
                        logger.warning(f"Database connection not available after {retries} attempts: {str(conn_error)}")
                    else:
                        logger.warning(f"Database connection attempt {attempt + 1} failed, retrying...")
                    db.session.rollback()

            if connected:
                try:
                    db.create_all()
                    db.session.commit()
                    logger.info("Database tables initialized successfully")
                except Exception as e:
                    logger.warning(f"Failed to create database tables: {str(e)}")
                    db.session.rollback()

        except Exception as e:
            logger.warning(f"Database initialization warning: {str(e)}")

    @app.context_processor
    def inject_config():
        return {'site': SITE_CONFIG}

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('X-Frame-Options', 'DENY')
        response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        response.headers.setdefault('Permissions-Policy', 'geolocation=(), microphone=(), camera=()')
        response.headers.setdefault('Content-Security-Policy', CSP_POLICY)
        return response

    @app.route('/')
    def home():
        try:
            operator_home = get_operator_home_data()
            return render_template('home.html',
                                 operator_home=operator_home,
                                 page_title='Trey Harnden',
                                 meta_description='Trey Harnden builds AI-assisted GTM systems, public experiments, and mountain-minded operating notes.',
                                 active_nav='home')
        except Exception as e:
            logger.error(f"Error rendering home page: {str(e)}")
            return "Internal Server Error", 500

    @app.route('/links')
    def links():
        try:
            return render_template('links.html',
                                 social_links=SITE_CONFIG['social_links'],
                                 project_links=SITE_CONFIG['project_links'],
                                 page_title='Links - Trey Harnden',
                                 meta_description='Connect with Trey Harnden on social media, book a call, or explore his public journal.',
                                 active_nav='links',
                                 og_title='Trey Harnden - Links',
                                 og_description='Connect with Trey Harnden on social media, book a call, or explore his public journal.',
                                 og_type='profile')
        except Exception as e:
            logger.error(f"Error rendering links page: {str(e)}")
            return "Internal Server Error", 500

    @app.route('/projects')
    def projects():
        try:
            project_links = SITE_CONFIG['project_links']
            section_order = [
                (
                    'elevation-engine',
                    'Elevation Engine Client Work',
                    'Client sites, demos, and delivery work built through Elevation Engine.'
                ),
                (
                    'random',
                    'Random Projects',
                    'Independent experiments that do not fit anywhere else yet.'
                ),
            ]
            project_sections = [
                {
                    'key': key,
                    'title': title,
                    'description': description,
                    'links': [link for link in project_links if link.get('section') == key],
                }
                for key, title, description in section_order
            ]
            section_lookup = {section['key']: section for section in project_sections}
            return render_template('projects.html',
                                 left_section=section_lookup['elevation-engine'],
                                 bottom_right_section=section_lookup['random'],
                                 page_title='Side Projects - Trey Harnden',
                                 meta_description='Side projects, client work, and independent experiments from Trey Harnden.',
                                 active_nav='projects')
        except Exception as e:
            logger.error(f"Error rendering projects page: {str(e)}")
            return "Internal Server Error", 500

    @app.route('/folloze-gtm')
    def folloze_gtm():
        try:
            folloze_links = [
                link for link in SITE_CONFIG['project_links'] if link.get('section') == 'folloze'
            ]
            folloze_section = {
                'title': 'Folloze Projects',
                'description': 'Public pages, tools, and demos tied to Folloze ABM, AI, and go-to-market execution.',
                'links': folloze_links,
            }
            public_repo_count = len([project for project in AI_GTM_PROJECTS if project.get('repo_url')])
            return render_template('folloze_gtm.html',
                                 folloze_section=folloze_section,
                                 ai_gtm_projects=AI_GTM_PROJECTS,
                                 ai_gtm_public_repo_count=public_repo_count,
                                 page_title='Folloze GTM - Trey Harnden',
                                 meta_description='Folloze GTM systems from Trey Harnden, including AI content engines, outbound systems, demo builders, and seller automation workflows.',
                                 active_nav='folloze-gtm')
        except Exception as e:
            logger.error(f"Error rendering Folloze GTM page: {str(e)}")
            return "Internal Server Error", 500

    @app.route('/work')
    def work():
        return redirect(url_for('projects'), code=301)

    @app.route('/projects/folloze-outbound-intent-loop')
    def folloze_outbound_intent_loop():
        return send_from_directory(
            os.path.join(app.static_folder, 'projects', 'folloze-outbound-engine'),
            'index.html'
        )

    @app.route('/strava/connect')
    def strava_connect():
        client_id, client_secret = get_strava_client_config()
        if not client_id or not client_secret:
            return "Strava client configuration is missing.", 500

        params = parse.urlencode({
            'client_id': client_id,
            'redirect_uri': get_strava_redirect_uri(),
            'response_type': 'code',
            'approval_prompt': 'force',
            'scope': STRAVA_DEFAULT_SCOPE,
            'state': make_strava_state(),
        })
        return redirect(f"https://www.strava.com/oauth/authorize?{params}")

    @app.route('/strava/callback')
    def strava_callback():
        if request.args.get('error'):
            logger.warning(f"Strava authorization denied: {request.args.get('error')}")
            return redirect(url_for('workouts'))

        if not is_valid_strava_state(request.args.get('state')):
            return "Invalid Strava authorization state.", 400

        code = request.args.get('code')
        scope = request.args.get('scope') or STRAVA_DEFAULT_SCOPE
        if not code:
            return "Missing Strava authorization code.", 400

        client_id, client_secret = get_strava_client_config()
        try:
            token_data = request_json(
                'https://www.strava.com/oauth/token',
                method='POST',
                data={
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'grant_type': 'authorization_code',
                    'code': code,
                },
            )
            token_data['scope'] = scope
            save_strava_token(token_data)
        except error.HTTPError as exc:
            logger.error(f"Strava authorization exchange failed with HTTP {exc.code}")
            return "Strava authorization exchange failed.", 502
        except Exception as exc:
            logger.error(f"Strava authorization exchange failed: {str(exc)}")
            return "Strava authorization exchange failed.", 502

        return redirect(url_for('workouts'))

    @app.route('/workouts')
    def workouts():
        try:
            workout_data = get_workout_data(limit=WORKOUTS_PAGE_ACTIVITY_LIMIT)
            return render_template('workouts.html',
                                 workout_data=workout_data,
                                 page_title='Workouts - Trey Harnden',
                                 meta_description='Recent training activity from Trey Harnden, designed to sync from Strava and Garmin-connected workouts.',
                                 active_nav='workouts')
        except Exception as e:
            logger.error(f"Error rendering workouts page: {str(e)}")
            return "Internal Server Error", 500

    @app.route('/api/workouts')
    def api_workouts():
        try:
            return jsonify(get_workout_data(limit=WORKOUTS_PAGE_ACTIVITY_LIMIT))
        except Exception as e:
            logger.error(f"Error getting workout data: {str(e)}")
            return jsonify({'error': 'Failed to get workout data'}), 500

    @app.route('/track-click', methods=['POST'])
    def track_click():
        try:
            data = request.get_json(silent=True) or {}
            link_name = str(data.get('link_name', '')).strip()
            if not link_name:
                return jsonify({'error': 'Missing link_name'}), 400
            if len(link_name) > 64:
                return jsonify({'error': 'link_name is too long'}), 400
            if link_name not in TRACKABLE_LINK_NAMES:
                return jsonify({'error': 'Invalid link_name'}), 400
            from models import LinkClick
            LinkClick.add_click(link_name)
            return jsonify({'status': 'ok'}), 200
        except Exception as e:
            logger.error(f"Error tracking click: {str(e)}")
            return jsonify({'error': 'Failed to track click'}), 500

    @app.route('/health')
    def health_check():
        try:
            db.session.execute(text('SELECT 1'))
            db.session.commit()
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                'status': 'unhealthy',
                'database': 'disconnected',
                'error': 'Database check failed',
                'timestamp': datetime.utcnow().isoformat()
            }), 500

    logger.info("Application configured successfully with database connection")
    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port)
