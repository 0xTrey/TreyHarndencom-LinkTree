
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy without binding to app
db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the app context"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")

        # Ensure proper URL format for SQLAlchemy
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)

        # Add SSL mode for Replit PostgreSQL
        if '?' not in database_url:
            database_url += '?sslmode=require'
        elif 'sslmode=' not in database_url:
            database_url += '&sslmode=require'

        app.logger.info(f"Configuring database connection...")
        
        # Configure SQLAlchemy with production-ready settings
        app.config.update(
            SQLALCHEMY_DATABASE_URI=database_url,
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            SQLALCHEMY_ENGINE_OPTIONS={
                'pool_pre_ping': True,
                'pool_size': 5,
                'max_overflow': 10,
                'pool_recycle': 300,
                'pool_timeout': 30,
                'connect_args': {
                    'connect_timeout': 10,
                    'application_name': 'flask_app'
                }
            }
        )

        # Initialize the app
        db.init_app(app)
        
        # Test the connection
        with app.app_context():
            # Simple connection test
            db.session.execute('SELECT 1')
            db.session.commit()
            app.logger.info("Database connection test successful")
            
        return True

    except Exception as e:
        app.logger.error(f"Database initialization error: {str(e)}")
        if hasattr(e, 'orig'):
            app.logger.error(f"Original error: {str(e.orig)}")
        raise

class LinkClick(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link_name = db.Column(db.String(64), nullable=False)
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow)
