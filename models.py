import logging
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import text

# Initialize SQLAlchemy
db = SQLAlchemy()
logger = logging.getLogger(__name__)

class LinkClick(db.Model):
    """Model for tracking link clicks"""
    id = db.Column(db.Integer, primary_key=True)
    link_name = db.Column(db.String(64), nullable=False)
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow)
