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
    app = None
    try:
        app = Flask(__name__)
        logger.info("Flask application instance created")
        
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
        env = os.environ.get('FLASK_ENV', 'development')
        logger.info(f"Application environment: {env}")
        
        # Get database URL from environment with better error handling
        logger.info("Checking DATABASE_URL environment variable...")
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            error_msg = "DATABASE_URL environment variable is not set"
            logger.critical(error_msg)
            raise ValueError(error_msg)
            
        logger.info("Database URL found, configuring connection...")
        
        # Ensure the database URL starts with postgresql://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
            logger.info("Converted postgres:// to postgresql:// in database URL")
        
        # Configure SQLAlchemy with optimized settings
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_size': 10,
            'max_overflow': 20,
            'pool_timeout': 30,
            'connect_args': {
                'connect_timeout': 10,
                'application_name': 'flask_app'
            }
        }
        
        # Import and initialize database
        from models import db, LinkClick
        db.init_app(app)
        
        # Initialize database tables within app context
        with app.app_context():
            try:
                # Verify database connection with retry
                retries = 3
                for attempt in range(retries):
                    try:
                        db.session.execute(text('SELECT 1'))
                        db.session.commit()
                        logger.info("Database connection verified successfully")
                        break
                    except Exception as conn_error:
                        if attempt == retries - 1:
                            logger.error(f"Failed to verify database connection after {retries} attempts: {str(conn_error)}")
                            raise
                        logger.warning(f"Database connection attempt {attempt + 1} failed, retrying...")
                        db.session.rollback()
                
                # Create tables
                db.create_all()
                db.session.commit()
                logger.info("Database tables initialized successfully")
                
            except Exception as e:
                logger.error(f"Database initialization error: {str(e)}")
                db.session.rollback()
                if app:
                    app.config['DATABASE_READY'] = False
                raise
    
    except Exception as e:
        logger.error(f"Application configuration error: {str(e)}")
        if app:
            app.config['DATABASE_READY'] = False
        raise
    
    if app:
        app.config['DATABASE_READY'] = True
        logger.info("Application configured successfully with database connection")
    
    return app
    
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
            with app.app_context():
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
