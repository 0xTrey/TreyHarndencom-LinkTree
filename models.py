import os
import time
import random
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
    logger.info("Checking DATABASE_URL environment variable...")
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        logger.critical("DATABASE_URL environment variable is not set")
        return None
    
    if not database_url.startswith('postgresql://'):
        logger.critical("DATABASE_URL must start with 'postgresql://'")
        return None
    
    # Log success but not the actual URL for security
    logger.info("Successfully validated DATABASE_URL format")
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

@retry_database_operation(max_retries=5, initial_delay=1.0)
def init_db(app, max_retries: int = 5) -> bool:
    """Initialize database with retry mechanism and proper error handling."""
    logger.info("Starting database initialization process...")
    
    try:
        # Validate database URL
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            logger.critical("DATABASE_URL environment variable is not set")
            raise ValueError("DATABASE_URL environment variable is not set")
            
        logger.info("Database URL found, configuring SQLAlchemy...")
        
        # Configure SQLAlchemy with minimal settings
        app.config.update(
            SQLALCHEMY_DATABASE_URI=database_url,
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            SQLALCHEMY_ENGINE_OPTIONS={
                'pool_pre_ping': True
            }
        )
        
        # Initialize Flask-SQLAlchemy
        logger.info("Initializing Flask-SQLAlchemy...")
        db.init_app(app)
        
        # Test database connection
        with app.app_context():
            logger.info("Testing database connection...")
            db.session.execute(text('SELECT 1'))
            db.session.commit()
            logger.info("Database connection test successful")
            
            # Create tables
            logger.info("Creating database tables...")
            db.create_all()
            logger.info("Database tables created successfully")
            
        logger.info("Database initialization completed successfully")
        return True
        
    except Exception as e:
        error_msg = f"Database initialization failed: {str(e)}"
        logger.error(error_msg)
        if app.config.get('FLASK_ENV') == 'production':
            logger.critical("Critical: Failed to initialize database in production")
            raise ValueError(error_msg)
        return False

class LinkClick(db.Model):
    """Model for tracking link clicks"""
    id = db.Column(db.Integer, primary_key=True)
    link_name = db.Column(db.String(64), nullable=False)
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow)
