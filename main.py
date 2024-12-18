
import os
import subprocess
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from app import app

if __name__ == "__main__":
    # Initial database setup with single worker

    # Start with single worker for DB initialization
    logger.info("Starting database initialization with single worker...")
    init_process = subprocess.Popen([
        "gunicorn", "app:app",
        "--bind", "0.0.0.0:80",
        "--workers", "1",
        "--timeout", "120",
        "--log-level", "debug"
    ])
    
    # Wait for DB initialization
    time.sleep(15)  # Increased wait time for proper initialization
    
    # Kill single worker process
    init_process.terminate()
    init_process.wait()  # Wait for process to completely terminate
    
    logger.info("Database initialized, starting with multiple workers...")
    # Start normal operation with multiple workers
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    os.system("gunicorn 'app:app' --bind '0.0.0.0:80' --workers 4 --timeout 120 --log-level debug")
