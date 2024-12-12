from app import app
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure app to work with HTTP proxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)

if __name__ == "__main__":
    # Force HTTP for development
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    
    # Explicitly disable SSL
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        ssl_context=None,
        use_reloader=True
    )
