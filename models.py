import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import text
import logging

# Initialize SQLAlchemy without binding to app
db = SQLAlchemy()

from utils import retry_database_operation

@retry_database_operation(max_retries=3, initial_delay=1.0)
def test_database_connection(app_context):
    """Test database connection with retry mechanism"""
    with app_context:
        try:
            db.session.execute(text('SELECT 1'))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise

@retry_database_operation(max_retries=3, initial_delay=2.0)
def initialize_database_tables(app_context):
    """Initialize database tables with retry mechanism"""
    with app_context:
        try:
            db.create_all()
        except Exception as e:
            db.session.rollback()
            raise

def init_db(app):
    """Initialize database with retry mechanism and proper error handling"""
    try:
        database_url = os.environ['DATABASE_URL']
        app.logger.info("Found DATABASE_URL in environment variables")
        
        # Configure SQLAlchemy
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_size': 5,
            'max_overflow': 10,
            'pool_timeout': 30,
            'pool_recycle': 1800,
        }
        
        # Initialize Flask-SQLAlchemy
        app.logger.info("Initializing Flask-SQLAlchemy...")
        db.init_app(app)
        
        # Test connection with retries
        app.logger.info("Testing database connection...")
        test_database_connection(app.app_context())
        app.logger.info("Database connection test successful")
        
        # Initialize tables with retries
        app.logger.info("Initializing database tables...")
        initialize_database_tables(app.app_context())
        app.logger.info("Database tables initialized successfully")
        
        return True
        
    except KeyError as e:
        app.logger.critical("DATABASE_URL environment variable is not set")
        if app.config.get('FLASK_ENV') == 'production':
            raise ValueError("DATABASE_URL environment variable is not set")
        return False
    except Exception as e:
        app.logger.error(f"Database initialization error: {str(e)}")
        if app.config.get('FLASK_ENV') == 'production':
            raise
        return False

class LinkClick(db.Model):
    """Model for tracking link clicks"""
    id = db.Column(db.Integer, primary_key=True)
    link_name = db.Column(db.String(64), nullable=False)
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow)
