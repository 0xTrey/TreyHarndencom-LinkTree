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


class IntegrationToken(db.Model):
    """Stores rotating OAuth tokens for connected services."""
    __tablename__ = 'integration_tokens'

    service = db.Column(db.String(32), primary_key=True)
    access_token = db.Column(db.Text, nullable=True)
    refresh_token = db.Column(db.Text, nullable=True)
    expires_at = db.Column(db.Integer, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @classmethod
    def get_service(cls, service):
        try:
            return cls.query.filter_by(service=service).one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving token for service {service}: {str(e)}")
            raise

    @classmethod
    def upsert_service(cls, service, access_token=None, refresh_token=None, expires_at=None):
        try:
            token = cls.get_service(service) or cls(service=service)
            token.access_token = access_token
            token.refresh_token = refresh_token
            token.expires_at = expires_at
            db.session.add(token)
            db.session.commit()
            logger.info(f"Updated token for service: {service}")
            return token
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error updating token for service {service}: {str(e)}")
            raise
