import logging
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///links.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Force HTTP configuration
app.config.update(
    PREFERRED_URL_SCHEME='http',
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    SERVER_NAME=None
)
db = SQLAlchemy(app)

# Sample social links data
social_links = [
    {'name': 'Twitter', 'url': 'https://twitter.com/johndoe', 'icon': 'fa-twitter'},
    {'name': 'LinkedIn', 'url': 'https://linkedin.com/in/johndoe', 'icon': 'fa-linkedin'},
    {'name': 'GitHub', 'url': 'https://github.com/johndoe', 'icon': 'fa-github'},
    {'name': 'Instagram', 'url': 'https://instagram.com/johndoe', 'icon': 'fa-instagram'}
]

class LinkClick(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link_name = db.Column(db.String(64), nullable=False)
    clicked_at = db.Column(db.DateTime, default=db.func.current_timestamp())

@app.route('/')
def index():
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

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)