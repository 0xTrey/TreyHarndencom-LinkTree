import logging
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy import text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    # Initialize Flask app
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    
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
    
    # Import database models
    from models import db, init_db, LinkClick
    
    # Initialize database with proper error handling
    if not init_db(app):
        logger.error("Failed to initialize database")
        if os.environ.get('FLASK_ENV') == 'production':
            raise RuntimeError("Database initialization failed in production")
    
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
        return render_template('index.html', social_links=social_links)

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

    @app.route('/health')
    def health_check():
        try:
            db.session.execute(text('SELECT 1'))
            db.session.commit()
            return jsonify({'status': 'healthy', 'database': 'connected'}), 200
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port)
