
import os
import subprocess
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from app import app
from models import db

if __name__ == "__main__":
    # Initialize database with app context
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            
    # Start with production configuration
    port = int(os.environ.get('PORT', 80))
    workers = int(os.environ.get('GUNICORN_WORKERS', 4))
    
    cmd = [
        "gunicorn",
        "app:app",
        f"--bind=0.0.0.0:{port}",
        f"--workers={workers}",
        "--timeout=120",
        "--log-level=info",
        "--preload"
    ]
    
    os.execvp(cmd[0], cmd)
