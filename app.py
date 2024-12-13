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

# Initialize Flask app with explicit static folder
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching during development

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
PRIMARY_DOMAIN = 'treyharnden.com'
REPLIT_SLUG = os.environ.get('REPL_SLUG', 'trey-harndencom-link-tree-harndentrey')
REPLIT_OWNER = os.environ.get('REPL_OWNER', 'treyharnden')
FULL_REPLIT_DOMAIN = f"{REPLIT_SLUG}.replit.app"

ALLOWED_HOSTS = [
    'treyharnden.com',
    'www.treyharnden.com',
    FULL_REPLIT_DOMAIN,
    '34.111.179.208',
    '*'  # Temporarily allow all during DNS propagation
]

# Remove SERVER_NAME to allow flexible domain handling
app.config.update(
    PREFERRED_URL_SCHEME='https'
)

# Configure Cloudflare proxy settings
PROXY_ALLOWED_IPS = [
    '173.245.48.0/20',
    '103.21.244.0/22',
    '103.22.200.0/22',
    '103.31.4.0/22',
    '141.101.64.0/18',
    '108.162.192.0/18',
    '190.93.240.0/20',
    '188.114.96.0/20',
    '197.234.240.0/22',
    '198.41.128.0/17',
    '162.158.0.0/15',
    '104.16.0.0/13',
    '104.24.0.0/14',
    '172.64.0.0/13',
    '131.0.72.0/22',
    '159.89.214.31/32',  # Added Replit's IP
]

# Ensure Cloudflare headers are trusted
app.config['PREFERRED_URL_SCHEME'] = 'https'

# Enhanced logging for debugging
logging.getLogger('werkzeug').setLevel(logging.DEBUG)
logging.getLogger('gunicorn.access').setLevel(logging.DEBUG)
logging.getLogger('gunicorn.error').setLevel(logging.DEBUG)

# Enhanced logging for domain debugging
logging.getLogger('werkzeug').setLevel(logging.DEBUG)

def setup_domains():
    """Configure allowed domains for the application."""
    logger.info("Setting up domain configuration...")
    allowed_origins = {
        "https://treyharnden.com",
        "https://www.treyharnden.com",
        f"https://{FULL_REPLIT_DOMAIN}"
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
    forwarded_for = request.headers.get('X-Forwarded-For', '')
    cf_visitor = request.headers.get('CF-Visitor', '')
    cf_connecting_ip = request.headers.get('CF-Connecting-IP', '')
    
    logger.info(f"""
    Request Details:
    - Host: {host}
    - X-Forwarded-For: {forwarded_for}
    - CF-Visitor: {cf_visitor}
    - CF-Connecting-IP: {cf_connecting_ip}
    - Path: {request.path}
    - Method: {request.method}
    """)
    
    # Handle Cloudflare headers
    cf_visitor = request.headers.get('CF-Visitor', '')
    if cf_visitor and '"scheme":"http"' in cf_visitor:
        url = request.url.replace('http://', 'https://', 1)
        logger.info(f"Redirecting HTTP to HTTPS via Cloudflare: {url}")
        return redirect(url, code=301)

    # During DNS propagation, allow all hosts but log the details
    logger.info(f"""
    Detailed Request Info:
    - Host: {host}
    - CF-Visitor: {cf_visitor}
    - CF-Connecting-IP: {request.headers.get('CF-Connecting-IP', '')}
    - X-Forwarded-For: {request.headers.get('X-Forwarded-For', '')}
    - X-Forwarded-Proto: {request.headers.get('X-Forwarded-Proto', '')}
    """)
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

# Ensure proper URL format for SQLAlchemy
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

try:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
except Exception as e:
    logger.error(f"Error configuring database: {str(e)}")
    raise
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
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )