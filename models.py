import logging
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text, inspect

# Initialize SQLAlchemy with minimal configuration
db = SQLAlchemy()
logger = logging.getLogger(__name__)

class LinkClick(db.Model):
    """Model for tracking link clicks"""
    __tablename__ = 'link_clicks'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    link_name = db.Column(db.String(64), nullable=False, index=True)
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __init__(self, link_name):
        self.link_name = link_name
    
    def __repr__(self):
        return f'<LinkClick {self.link_name} at {self.clicked_at}>'
    
    @classmethod
    def get_all_clicks(cls):
        """Get all link clicks ordered by timestamp"""
        try:
            return cls.query.order_by(cls.clicked_at.desc()).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving link clicks: {str(e)}")
            raise
            
    @classmethod
    def add_click(cls, link_name):
        """Record a new link click"""
        try:
            click = cls(link_name=link_name)
            db.session.add(click)
            db.session.commit()
            logger.info(f"Recorded click for link: {link_name}")
            return click
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error recording link click: {str(e)}")
            raise
