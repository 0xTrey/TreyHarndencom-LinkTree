import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import text
import logging

# Initialize SQLAlchemy without binding to app
db = SQLAlchemy()

def init_db(app):
    """Initialize database with proper error handling and logging"""
    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    try:
        db.init_app(app)
        
        # Create tables and test connection within app context
        with app.app_context():
            # Test connection before creating tables
            db.session.execute(text('SELECT 1'))
            db.session.commit()
            
            # Create tables if they don't exist
            db.create_all()
            
            app.logger.info("Database connection successful")
            return True
    except Exception as e:
        app.logger.error(f"Database connection failed: {str(e)}")
        if app.config.get('FLASK_ENV') == 'production':
            raise
        return False

class LinkClick(db.Model):
    """Model for tracking link clicks"""
    id = db.Column(db.Integer, primary_key=True)
    link_name = db.Column(db.String(64), nullable=False)
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow)
