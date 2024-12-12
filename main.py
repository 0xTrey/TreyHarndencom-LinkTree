from app import app

if __name__ == "__main__":
    # Force HTTP for development
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.run(host="0.0.0.0", port=5000, debug=True, ssl_context=None)
