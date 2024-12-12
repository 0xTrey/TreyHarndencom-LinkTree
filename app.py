import os
import logging
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///links.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)

@app.route('/')
def index():
    social_links = [
        {
            'name': 'Twitter',
            'url': 'https://twitter.com/yourusername',
            'icon': 'fa-twitter'
        },
        {
            'name': 'Instagram',
            'url': 'https://instagram.com/yourusername',
            'icon': 'fa-instagram'
        },
        {
            'name': 'LinkedIn',
            'url': 'https://linkedin.com/in/yourusername',
            'icon': 'fa-linkedin'
        },
        {
            'name': 'GitHub',
            'url': 'https://github.com/yourusername',
            'icon': 'fa-github'
        }
    ]
    return render_template('index.html', social_links=social_links)

with app.app_context():
    import models
    db.create_all()
