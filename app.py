import logging
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime
from sqlalchemy import text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configure ProxyFix for proper header handling
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Security configurations
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY', os.urandom(24)),
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        PREFERRED_URL_SCHEME='https'
    )
    
    # Configure CORS
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    
    # Configure database
    logger.info("Checking DATABASE_URL environment variable...")
    if not os.environ.get('DATABASE_URL'):
        logger.critical("DATABASE_URL environment variable is not set")
        raise ValueError("DATABASE_URL environment variable is not set in the environment")
        
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Import and initialize database
    from models import db
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            raise
    
    # Social links data
    social_links = [
        {'name': 'Personal Website', 'url': 'https://harnden.notion.site/My-Second-Brain-a2bcac8bd3424b6bbd838c709dc1bb73', 'icon': ''},
        {'name': 'Book A Call', 'url': 'https://calendly.com/harnden/consulting-intro-call', 'icon': ''},
        {'name': 'X (Twitter)', 'url': 'https://x.com/Trey_Harnden', 'icon': 'fa-x-twitter'},
        {'name': 'LinkedIn', 'url': 'https://www.linkedin.com/in/treyharnden/', 'icon': 'fa-linkedin'},
        {'name': 'Strava', 'url': 'https://www.strava.com/athletes/34654738', 'icon': 'fa-strava'}
    ]
    
    @app.route('/')
    def index():
        try:
            return render_template('index.html', social_links=social_links)
        except Exception as e:
            logger.error(f"Error rendering index page: {str(e)}")
            return "Internal Server Error", 500
    
    @app.route('/health')
    def health_check():
        """Health check endpoint that verifies database connection"""
        try:
            # Test database connection
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
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 500

    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port)