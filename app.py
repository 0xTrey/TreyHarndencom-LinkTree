import logging
import os
from flask import Flask, render_template, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure ProxyFix for proper handling of protocols and hosts behind proxies
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Security configurations
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', os.urandom(24)),
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    PREFERRED_URL_SCHEME='https'
)

# Configure domain settings
PRIMARY_DOMAIN = os.environ.get('CUSTOM_DOMAIN', 'treyharnden.com')
REPLIT_DOMAIN = f"harndentrey.repl.co"
REPLIT_ID = os.environ.get('REPL_ID', '')

def setup_domains():
    """Configure allowed domains for the application."""
    logger.info("Setting up domain configuration...")
    allowed_origins = {
        f"https://{PRIMARY_DOMAIN}",
        f"https://www.{PRIMARY_DOMAIN}",
        f"https://{REPLIT_DOMAIN}",
        "https://*.repl.co",
        "https://*.repl.dev"
    }
    logger.info(f"Domain configuration: {allowed_origins}")
    return list(allowed_origins)

# Set up allowed origins
ALLOWED_ORIGINS = setup_domains()

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": ALLOWED_ORIGINS,
        "supports_credentials": True
    }
})

# Configure domain settings
app.config.update(
    PRIMARY_DOMAIN=PRIMARY_DOMAIN,
    PREFERRED_URL_SCHEME='https'
)

# Add domain redirect middleware
@app.before_request
def redirect_to_primary_domain():
    """Handle domain redirects and protocol upgrades."""
    if request.method == 'OPTIONS':
        return None

    host = request.headers.get('Host', '')
    logger.info(f"Processing request for host: {host}")
    
    # Skip redirects for Replit domains and local development
    if '.repl.co' in host or '.repl.dev' in host:
        logger.debug(f"Skipping redirect for development domain: {host}")
        return None
        
    # Force HTTPS
    if request.headers.get('X-Forwarded-Proto', 'http') == 'http':
        url = request.url.replace('http://', 'https://', 1)
        logger.info(f"Redirecting HTTP to HTTPS: {url}")
        return redirect(url, code=301)

    # Handle www subdomain
    if host.startswith('www.'):
        target = request.url.replace('www.', '', 1)
        logger.info(f"Redirecting www to non-www: {target}")
        return redirect(target, code=301)

    return None

# Add security headers
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    headers = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }
    response.headers.update(headers)
    return response

# Database configuration
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    raise ValueError("DATABASE_URL environment variable is not set")

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Social links data
social_links = [
    {'name': 'Personal Website', 'url': 'https://harnden.notion.site/My-Second-Brain-a2bcac8bd3424b6bbd838c709dc1bb73', 'icon': ''},
    {'name': 'Book A Call', 'url': 'https://calendly.com/harnden/consulting-intro-call', 'icon': ''},
    {'name': 'X (Twitter)', 'url': 'https://x.com/Trey_Harnden', 'icon': 'fa-x-twitter'},
    {'name': 'LinkedIn', 'url': 'https://www.linkedin.com/in/treyharnden/', 'icon': 'fa-linkedin'},
    {'name': 'Strava', 'url': 'https://www.strava.com/athletes/34654738', 'icon': 'fa-strava'}
]

class LinkClick(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link_name = db.Column(db.String(64), nullable=False)
    clicked_at = db.Column(db.DateTime, default=db.func.current_timestamp())

@app.route('/')
def index():
    try:
        host = request.headers.get('Host', '')
        protocol = request.headers.get('X-Forwarded-Proto', 'http')
        logger.info(f"Incoming request - Host: {host}, Protocol: {protocol}")
        return render_template('index.html', social_links=social_links)
    except Exception as e:
        logger.error(f"Error rendering index page: {str(e)}")
        return "An error occurred", 500

@app.route('/track-click', methods=['POST'])
def track_click():
    try:
        data = request.get_json()
        link_name = data.get('link_name')
        
        if not link_name:
            return jsonify({'error': 'Link name is required'}), 400
            
        click = LinkClick(link_name=link_name)
        db.session.add(click)
        db.session.commit()
        
        return jsonify({'message': 'Click tracked successfully'}), 200
    except Exception as e:
        logger.error(f"Error tracking click: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)