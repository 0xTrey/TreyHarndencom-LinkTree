import logging
import os
from flask import Flask, render_template, request, jsonify
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
def validate_domain(domain):
    """Validate and format domain string."""
    if not domain:
        return None
    
    domain = domain.strip().lower()
    
    # Remove protocol if present
    if domain.startswith(('http://', 'https://')):
        domain = domain.split('://', 1)[1]
    
    # Remove trailing slashes
    domain = domain.rstrip('/')
    
    # Basic domain validation
    if not all(c.isalnum() or c in '-._' for c in domain.replace('/', '')):
        logger.warning(f"Invalid domain format: {domain}")
        return None
        
    return domain

def setup_domains():
    """Configure allowed domains for the application."""
    logger.info("Setting up domain configuration...")
    allowed_origins = set()
    
    try:
        # Get Replit domain
        repl_slug = os.environ.get('REPL_SLUG', 'workspace')
        repl_owner = os.environ.get('REPL_OWNER', 'harndentrey')
        replit_domain = f"{repl_slug}.{repl_owner}.repl.co"
        allowed_origins.add(f"https://{replit_domain}")
        logger.info(f"Added Replit domain: {replit_domain}")
        
        # Add custom domain if specified
        custom_domain = validate_domain(os.environ.get('CUSTOM_DOMAIN', ''))
        if custom_domain:
            allowed_origins.add(f"https://{custom_domain}")
            logger.info(f"Added custom domain: {custom_domain}")
        
        # Add additional domains
        additional_domains = os.environ.get('ADDITIONAL_DOMAINS', '').strip()
        if additional_domains:
            for domain in additional_domains.split(','):
                domain = validate_domain(domain)
                if domain:
                    allowed_origins.add(f"https://{domain}")
                    logger.info(f"Added additional domain: {domain}")
    
    except Exception as e:
        logger.error(f"Error setting up domains: {str(e)}")
        # Fallback to Replit domain only
        allowed_origins = {f"https://{repl_slug}.{repl_owner}.repl.co"}
    
    return list(allowed_origins)

# Set up allowed origins
ALLOWED_ORIGINS = setup_domains()

# Configure CORS with security settings
cors_config = {
    "resources": {
        r"/*": {
            "origins": ALLOWED_ORIGINS,
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "max_age": 3600,
            "expose_headers": ["Content-Type", "Content-Length"]
        }
    },
    "vary_header": True
}

try:
    CORS(app, **cors_config)
    logger.info("CORS configuration applied successfully")
except Exception as e:
    logger.error(f"Error configuring CORS: {str(e)}")
    # Fallback to basic CORS configuration
    CORS(app)

# Log configured domains
logger.info(f"Configured domains: {', '.join(ALLOWED_ORIGINS)}")

# Don't set SERVER_NAME to allow both custom domain and Replit domain access
app.config['SERVER_NAME'] = None

# Add security headers
@app.after_request
def add_security_headers(response):
    try:
        # Generate CSP with all allowed origins
        connect_src = ["'self'"] + ALLOWED_ORIGINS
        trusted_cdn_domains = [
            "cdn.jsdelivr.net",
            "cdnjs.cloudflare.com",
            "cdn.replit.com"
        ]
        
        csp_directives = [
            "default-src 'self'",
            f"connect-src {' '.join(connect_src)}",
            f"img-src 'self' data: {' '.join(trusted_cdn_domains)}",
            f"script-src 'self' 'unsafe-inline' {' '.join(trusted_cdn_domains)}",
            f"style-src 'self' 'unsafe-inline' {' '.join(trusted_cdn_domains)}",
            f"font-src 'self' {' '.join(trusted_cdn_domains)}",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'"
        ]
        
        # Security headers with logging
        headers = {
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Content-Security-Policy': '; '.join(csp_directives),
            'Permissions-Policy': 'geolocation=(), camera=(), microphone=()',
            'Cross-Origin-Opener-Policy': 'same-origin'
        }
        
        response.headers.update(headers)
        logger.debug(f"Security headers added successfully for path: {request.path}")
        
    except Exception as e:
        logger.error(f"Error adding security headers: {str(e)}")
        
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
        logger.info("Rendering index page")
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
