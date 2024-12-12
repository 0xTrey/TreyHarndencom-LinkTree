import os
import logging
from flask import Flask, render_template, request, jsonify
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
@app.route('/track-click', methods=['POST'])
def track_click():
    try:
        data = request.get_json()
        link_name = data.get('link_name')
        
        if not link_name:
            return jsonify({'error': 'Link name is required'}), 400
            
        click = LinkClick(link_name=link_name)
        db.session.add(click)
        db.session.commit()
        
        return jsonify({'message': 'Click tracked successfully'}), 200
    except Exception as e:
        logging.error(f"Error tracking click: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500


with app.app_context():
    import models
    db.create_all()
