from app import app

if __name__ == "__main__":
    # Configure server for HTTP only
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    app.run(
        host='0.0.0.0',
        port=5000,
        ssl_context=None,
        debug=True
    )
