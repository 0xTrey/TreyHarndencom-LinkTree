
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
    import sys
    
    # Initialize database with app context (only in parent process)
    if os.environ.get('GUNICORN_WORKER_ID') != '1':
        with app.app_context():
            try:
                db.create_all()
                logger.info("Database initialized successfully")
            except Exception as e:
                logger.error(f"Database initialization error: {e}")
                sys.exit(1)
    
    # Always use port 5000 as required by system
    port = 5000
    workers = int(os.environ.get('GUNICORN_WORKERS', 4))
    
    cmd = [
        "gunicorn",
        "app:app",
        f"--bind=0.0.0.0:{port}",
        f"--workers={workers}",
        "--timeout=120",
        "--log-level=info",
        "--preload",
        "--worker-class=sync"
    ]
    
    logger.info(f"Starting Gunicorn on port {port} with {workers} workers")
    os.execvp(cmd[0], cmd)
