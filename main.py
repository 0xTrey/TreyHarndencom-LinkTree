from app import app

if __name__ == "__main__":
    # Force HTTP for development
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    app.run(host="0.0.0.0", port=5000, debug=True)
