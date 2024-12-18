
from app import app

if __name__ == "__main__":
    # Initial database setup with single worker
    import os
    import subprocess
    import time

    # Start with single worker for DB initialization
    init_process = subprocess.Popen([
        "gunicorn", "app:app",
        "--bind", "0.0.0.0:80",
        "--workers", "1",
        "--timeout", "120"
    ])
    
    # Wait for DB initialization
    time.sleep(10)
    
    # Kill single worker process
    init_process.terminate()
    
    # Start normal operation with multiple workers
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    os.system("gunicorn 'app:app' --bind '0.0.0.0:80' --workers 4 --timeout 120")
