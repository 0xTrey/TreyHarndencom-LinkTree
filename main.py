
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
    import socket
    import sys
    from contextlib import closing
    
    def find_free_port(start_port, max_attempts=10):
        """Find a free port starting from start_port"""
        for port_num in range(start_port, start_port + max_attempts):
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                try:
                    sock.bind(('0.0.0.0', port_num))
                    sock.listen(1)
                    return port_num
                except socket.error:
                    continue
        return None

    # Initialize database with app context (only in parent process)
    if os.environ.get('GUNICORN_WORKER_ID') != '1':
        with app.app_context():
            try:
                db.create_all()
                logger.info("Database initialized successfully")
            except Exception as e:
                logger.error(f"Database initialization error: {e}")
                sys.exit(1)
    
    # Find available port
    preferred_port = int(os.environ.get('PORT', 5000))
    port = find_free_port(preferred_port)
    if port is None:
        logger.error(f"Could not find a free port after trying {preferred_port} through {preferred_port + 9}")
        sys.exit(1)
    
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
