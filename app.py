import logging
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime, date
from sqlalchemy import text

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SITE_CONFIG = {
    'name': 'Trey Harnden',
    'bio': 'Ski mountaineer and technology enthusiast exploring how AI can help people live healthier, more intentional lives. I journal daily and share my life very transparently on my Public Journal. Connect with me on any social platform or book a call if you want to chat about ABM, AI, or life in general.',
    'avatar': 'images/Trey Rainier Headshot.jpeg',
    'github_url': 'https://github.com/treyharnden',
    'notion_embed_url': 'https://harnden.notion.site/My-Second-Brain-a2bcac8bd3424b6bbd838c709dc1bb73',
    'social_links': [
        {'name': 'Public Journal', 'url': 'https://harnden.notion.site/My-Second-Brain-a2bcac8bd3424b6bbd838c709dc1bb73', 'icon': '', 'category': 'personal'},
        {'name': 'Book A Call', 'url': 'https://app.reclaim.ai/m/harnden', 'icon': '', 'category': 'professional'},
        {'name': 'X (Twitter)', 'url': 'https://x.com/Trey_Harnden', 'icon': 'fa-x-twitter', 'category': 'social'},
        {'name': 'LinkedIn', 'url': 'https://www.linkedin.com/in/treyharnden/', 'icon': 'fa-linkedin', 'category': 'professional'},
        {'name': 'Strava', 'url': 'https://www.strava.com/athletes/34654738', 'icon': 'fa-strava', 'category': 'social'},
    ],
    'work_links': [
        {'name': 'LinkedIn', 'url': 'https://www.linkedin.com/in/treyharnden/', 'icon': 'fa-linkedin'},
        {'name': 'ABM Playbook Generator', 'url': 'https://abm-playbook.com/', 'icon': ''},
        {'name': 'Book A Call', 'url': 'https://app.reclaim.ai/m/harnden', 'icon': ''},
    ],
    'milestones': {
        'birth_date': date(1995, 10, 1),
        'alcohol_free_date': date(2023, 1, 22),
        'marijuana_free_date': date(2025, 6, 24),
    },
}


def calculate_days_since(start_date):
    today = date.today()
    return (today - start_date).days


def get_sobriety_data():
    milestones = SITE_CONFIG['milestones']
    return {
        'days_of_life': calculate_days_since(milestones['birth_date']),
        'days_alcohol_free': calculate_days_since(milestones['alcohol_free_date']),
        'days_marijuana_free': calculate_days_since(milestones['marijuana_free_date']),
    }


def create_app():
    app = Flask(__name__)
    logger.info("Flask application instance created")

    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    app.config.update(
        SECRET_KEY=os.environ.get('FLASK_SECRET_KEY', os.urandom(24)),
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        PREFERRED_URL_SCHEME='https'
    )

    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    env = os.environ.get('FLASK_ENV', 'development')
    logger.info(f"Application environment: {env}")

    logger.info("Checking DATABASE_URL environment variable...")
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            logger.warning("DATABASE_URL not set, falling back to SQLite")
            database_url = 'sqlite:///:memory:'
            app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
                'pool_pre_ping': True,
                'pool_recycle': 300
            }
        else:
            db_type = database_url.split('://')[0] if '://' in database_url else 'unknown'
            db_host = database_url.split('@')[1].split('/')[0] if '@' in database_url else 'unknown'
            logger.info(f"Database configuration: type={db_type}, host={db_host}")
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)

            app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
                'pool_size': 5,
                'max_overflow': 10,
                'pool_timeout': 30,
                'pool_pre_ping': True,
                'pool_recycle': 300,
                'connect_args': {
                    'connect_timeout': 10,
                    'application_name': 'flask_app'
                }
            }

        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    except Exception as e:
        logger.error(f"Error configuring database: {str(e)}")
        database_url = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300
        }
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    from models import db
    db.init_app(app)

    with app.app_context():
        try:
            retries = 3
            connected = False
            for attempt in range(retries):
                try:
                    db.session.execute(text('SELECT 1'))
                    db.session.commit()
                    logger.info("Database connection verified successfully")
                    connected = True
                    break
                except Exception as conn_error:
                    if attempt == retries - 1:
                        logger.warning(f"Database connection not available after {retries} attempts: {str(conn_error)}")
                    else:
                        logger.warning(f"Database connection attempt {attempt + 1} failed, retrying...")
                    db.session.rollback()

            if connected:
                try:
                    db.create_all()
                    db.session.commit()
                    logger.info("Database tables initialized successfully")
                except Exception as e:
                    logger.warning(f"Failed to create database tables: {str(e)}")
                    db.session.rollback()

        except Exception as e:
            logger.warning(f"Database initialization warning: {str(e)}")

    @app.context_processor
    def inject_config():
        return {'site': SITE_CONFIG}

    @app.route('/')
    def home():
        try:
            return render_template('home.html',
                                 page_title='Trey Harnden',
                                 meta_description='Ski mountaineer and technology enthusiast exploring AI, health, and intentional living.',
                                 active_nav='home')
        except Exception as e:
            logger.error(f"Error rendering home page: {str(e)}")
            return "Internal Server Error", 500

    @app.route('/links')
    def links():
        try:
            return render_template('links.html',
                                 social_links=SITE_CONFIG['social_links'],
                                 page_title='Links - Trey Harnden',
                                 meta_description='Connect with Trey Harnden on social media, book a call, or explore his public journal.',
                                 active_nav='links',
                                 og_title='Trey Harnden - Links',
                                 og_description='Connect with Trey Harnden on social media, book a call, or explore his public journal.',
                                 og_type='profile')
        except Exception as e:
            logger.error(f"Error rendering links page: {str(e)}")
            return "Internal Server Error", 500

    @app.route('/journal')
    def journal():
        try:
            return render_template('journal.html',
                                 page_title='Journal - Trey Harnden',
                                 meta_description='Trey Harnden\'s public journal — thoughts on AI, health, sobriety, and intentional living.',
                                 active_nav='journal')
        except Exception as e:
            logger.error(f"Error rendering journal page: {str(e)}")
            return "Internal Server Error", 500

    @app.route('/work')
    def work():
        try:
            return render_template('work.html',
                                 work_links=SITE_CONFIG['work_links'],
                                 page_title='Work - Trey Harnden',
                                 meta_description='Professional links and resources from Trey Harnden — ABM, AI, and go-to-market strategy.',
                                 active_nav='work')
        except Exception as e:
            logger.error(f"Error rendering work page: {str(e)}")
            return "Internal Server Error", 500

    @app.route('/stats')
    def stats():
        try:
            sobriety_data = get_sobriety_data()
            milestones = SITE_CONFIG['milestones']
            return render_template('stats.html',
                                 sobriety_data=sobriety_data,
                                 milestones=milestones,
                                 page_title='Stats - Trey Harnden',
                                 meta_description='Personal milestone trackers — days of life, sobriety counters, and more.',
                                 active_nav='stats')
        except Exception as e:
            logger.error(f"Error rendering stats page: {str(e)}")
            return "Internal Server Error", 500

    @app.route('/api/sobriety_data')
    def api_sobriety_data():
        try:
            return jsonify(get_sobriety_data())
        except Exception as e:
            logger.error(f"Error getting sobriety data: {str(e)}")
            return jsonify({'error': 'Failed to get sobriety data'}), 500

    @app.route('/track-click', methods=['POST'])
    def track_click():
        try:
            data = request.get_json()
            if not data or 'link_name' not in data:
                return jsonify({'error': 'Missing link_name'}), 400
            from models import LinkClick
            LinkClick.add_click(data['link_name'])
            return jsonify({'status': 'ok'}), 200
        except Exception as e:
            logger.error(f"Error tracking click: {str(e)}")
            return jsonify({'error': 'Failed to track click'}), 500

    @app.route('/health')
    def health_check():
        try:
            db.session.execute(text('SELECT 1'))
            db.session.commit()
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                'status': 'unhealthy',
                'database': 'disconnected',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 500

    logger.info("Application configured successfully with database connection")
    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port)
