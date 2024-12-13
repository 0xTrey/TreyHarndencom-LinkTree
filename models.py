import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import text
import logging
from typing import Optional

# Initialize SQLAlchemy without binding to app
db = SQLAlchemy()

logger = logging.getLogger(__name__)

def validate_database_url() -> Optional[str]:
    """Validate and return the database URL from environment variables."""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        logger.critical("DATABASE_URL environment variable is not set")
        return None
    
    # Log success but not the actual URL for security
    logger.info("Successfully retrieved DATABASE_URL from environment")
    return database_url

from utils import retry_database_operation, is_retriable_error

@retry_database_operation(
    max_retries=5,
    initial_delay=1.0,
    exponential_base=2.0,
    max_delay=30.0,
    jitter=0.1
)
def test_database_connection(app):
    """Test database connection with retry mechanism."""
    with app.app_context():
        db.session.execute(text('SELECT 1'))
        db.session.commit()

def init_db(app, max_retries: int = 5) -> bool:
    """Initialize database with comprehensive retry mechanism and proper error handling."""
    
    # Check if database is already initialized
    if hasattr(app, '_database_initialized'):
        return True
        
    for attempt in range(max_retries):
        try:
            # Validate database URL
            database_url = validate_database_url()
            if not database_url:
                raise ValueError("DATABASE_URL environment variable is not set")
            
            # Configure SQLAlchemy with optimized settings
            app.config['SQLALCHEMY_DATABASE_URI'] = database_url
            app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
            app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
                'pool_size': 5,
                'max_overflow': 10,
                'pool_timeout': 30,
                'pool_recycle': 1800,
                'pool_pre_ping': True,
                'echo_pool': True if app.debug else False
            }
            
            # Initialize Flask-SQLAlchemy
            logger.info(f"Initializing Flask-SQLAlchemy (attempt {attempt + 1}/{max_retries})...")
            db.init_app(app)
            
            # Test database connection with retry mechanism
            logger.info(f"Testing database connection (attempt {attempt + 1}/{max_retries})...")
            with app.app_context():
                test_database_connection(app)
                logger.info("Database connection test successful")
                
                # Create tables
                logger.info("Creating database tables...")
                db.create_all()
                logger.info("Database tables created successfully")
            
            # Mark database as initialized
            setattr(app, '_database_initialized', True)
            return True
            
        except Exception as e:
            error_message = str(e)
            is_retriable = is_retriable_error(e)
            
            if attempt < max_retries - 1 and is_retriable:
                delay = (2 ** attempt) + random.uniform(0, 0.1)  # Exponential backoff with jitter
                logger.warning(
                    f"Database initialization attempt {attempt + 1}/{max_retries} failed: {error_message}. "
                    f"Retrying in {delay:.2f} seconds..."
                )
                time.sleep(delay)
                continue
            
            logger.error(
                f"Database initialization failed after {attempt + 1} attempts: {error_message}. "
                f"Error is {'retriable' if is_retriable else 'non-retriable'}"
            )
            
            if app.config.get('FLASK_ENV') == 'production' and not is_retriable:
                raise
            return False
            
    return False

class LinkClick(db.Model):
    """Model for tracking link clicks"""
    id = db.Column(db.Integer, primary_key=True)
    link_name = db.Column(db.String(64), nullable=False)
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow)
