
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import text as sqlalchemy_text

# Initialize SQLAlchemy without binding to app
db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the app context"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            app.logger.error("DATABASE_URL environment variable is not set")
            raise ValueError("DATABASE_URL environment variable is not set")

        app.logger.info("Configuring database connection...")
        
        # Ensure proper URL format for SQLAlchemy
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)

        # Add SSL mode for Replit PostgreSQL
        if 'sslmode=' not in database_url:
            database_url = database_url + ('&' if '?' in database_url else '?') + 'sslmode=require'

        # Configure SQLAlchemy with production-ready settings
        app.config.update(
            SQLALCHEMY_DATABASE_URI=database_url,
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            SQLALCHEMY_ENGINE_OPTIONS={
                'pool_pre_ping': True,
                'pool_size': 10,
                'max_overflow': 20,
                'pool_recycle': 300,
                'pool_timeout': 30,
                'connect_args': {
                    'connect_timeout': 10,
                    'application_name': 'flask_app',
                    'keepalives': 1,
                    'keepalives_idle': 30,
                    'keepalives_interval': 10,
                    'keepalives_count': 5,
                    'sslmode': 'require'
                }
            }
        )

        # Initialize the app
        db.init_app(app)
        
        # Test the connection with explicit transaction handling
        with app.app_context():
            try:
                db.session.execute(sqlalchemy_text('SELECT 1'))
                db.session.commit()
                app.logger.info("Database connection test successful")
            except Exception as conn_error:
                db.session.rollback()
                app.logger.error(f"Database connection test failed: {str(conn_error)}")
                raise
            
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
