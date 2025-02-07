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
    logger.info("Flask application instance created")
    
    # Configure ProxyFix for proper header handling
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Security configurations
    app.config.update(
        SECRET_KEY=os.environ.get('FLASK_SECRET_KEY', os.urandom(24)),
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
            # Safely log DB connection info without exposing credentials
            db_type = database_url.split('://')[0] if '://' in database_url else 'unknown'
            db_host = database_url.split('@')[1].split('/')[0] if '@' in database_url else 'unknown'
            logger.info(f"Database configuration: type={db_type}, host={db_host}")
            # Ensure the database URL starts with postgresql://
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
                logger.info("Converted postgres:// to postgresql:// in database URL")
            
            # PostgreSQL-specific configuration
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
            
        logger.info("Configuring database connection...")
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
    except Exception as e:
        logger.error(f"Error configuring database: {str(e)}")
        logger.warning("Falling back to SQLite in-memory database")
        database_url = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300
        }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300
    }
    
    # Import and initialize database
    from models import db
    db.init_app(app)
    
    # Initialize database tables within app context
    with app.app_context():
        try:
            # Verify database connection with retry
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
                    # Create tables only if connection is successful
                    db.create_all()
                    db.session.commit()
                    logger.info("Database tables initialized successfully")
                except Exception as e:
                    logger.warning(f"Failed to create database tables: {str(e)}")
                    db.session.rollback()
            
        except Exception as e:
            logger.warning(f"Database initialization warning: {str(e)}")
            if 'db.session' in locals():
                db.session.rollback()

    # Social links data
    app.config['social_links'] = [
        {'name': 'Personal Website', 'url': 'https://harnden.notion.site/My-Second-Brain-a2bcac8bd3424b6bbd838c709dc1bb73', 'icon': ''},
        {'name': 'Book A Call', 'url': 'https://calendly.com/harnden', 'icon': ''},
        {'name': 'X (Twitter)', 'url': 'https://x.com/Trey_Harnden', 'icon': 'fa-x-twitter'},
        {'name': 'LinkedIn', 'url': 'https://www.linkedin.com/in/treyharnden/', 'icon': 'fa-linkedin'},
        {'name': 'Strava', 'url': 'https://www.strava.com/athletes/34654738', 'icon': 'fa-strava'},
        {'name': 'Meditation Timer', 'url': 'https://meditation-master-harndentrey.replit.app/', 'icon': ''}
    ]

    @app.route('/')
    def index():
        try:
            return render_template('index.html', social_links=app.config['social_links'])
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

    @app.route('/test_db')
    def test_db():
        """Test database connectivity and concurrent access"""
        start_time = datetime.utcnow()
        try:
            # Test database connection with session handling
            with db.session.begin():
                # Execute simple query
                result = db.session.execute(text('SELECT 1')).scalar()
                end_time = datetime.utcnow()
                response_time = (end_time - start_time).total_seconds()
                
                return jsonify({
                    'status': 'success',
                    'database': 'connected',
                    'query_result': result,
                    'response_time_seconds': response_time,
                    'timestamp': end_time.isoformat(),
                    'worker_pid': os.getpid()
                }), 200
        except Exception as e:
            logger.error(f"Database test failed: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 500
    logger.info("Application configured successfully with database connection")
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port)