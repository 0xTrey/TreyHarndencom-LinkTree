import os
import time
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import text as sqlalchemy_text

# Initialize SQLAlchemy without binding to app
db = SQLAlchemy()

def init_db(app, max_retries=3):
    """Initialize database with error handling and retries"""
    for attempt in range(max_retries):
        try:
            # Get database URL from environment
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                app.logger.error("DATABASE_URL environment variable is not set")
                raise ValueError("DATABASE_URL environment variable is not set")

            # Configure SQLAlchemy
            app.config.update(
                SQLALCHEMY_DATABASE_URI=database_url,
                SQLALCHEMY_TRACK_MODIFICATIONS=False,
                SQLALCHEMY_ENGINE_OPTIONS={
                    'pool_pre_ping': True,
                    'pool_size': 5,
                    'pool_recycle': 300,
                    'pool_timeout': 30
                }
            )

            # Initialize the app with database
            db.init_app(app)
            
            # Test the connection
            with app.app_context():
                db.session.execute(sqlalchemy_text('SELECT 1'))
                db.session.commit()
                app.logger.info("Database connection successful")
                return True

        except Exception as e:
            app.logger.error(f"Database initialization error (attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise
    
    return False

class LinkClick(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link_name = db.Column(db.String(64), nullable=False)
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow)
