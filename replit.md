# replit.md

## Overview

This project is a personal website and link tree application for Trey Harnden, hosted at treyharnden.com. The application features two main components: a social links section that allows visitors to navigate to various profiles and platforms, and a personal milestones tracker that displays real-time counters for sobriety achievements and life metrics. The application serves as both a professional presence and a personal accountability tool.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
The application uses a server-side rendered approach with Flask templates and vanilla JavaScript for dynamic functionality. The frontend consists of:

- **Template Structure**: Uses Jinja2 templating with a base template (`base.html`) that provides the common HTML structure and extends to specific page templates like `index.html`
- **Styling**: Implements a modern, responsive design using Bootstrap 5 with custom CSS for unique styling elements like gradient backgrounds and profile images
- **Dynamic Components**: Features a MetricCounter JavaScript class that handles real-time updates for sobriety tracking counters with automatic refresh intervals and visual feedback animations
- **Responsive Design**: Mobile-first approach with special optimizations for different screen sizes

### Backend Architecture
The backend is built with Flask following a modular application factory pattern:

- **Application Factory**: Uses `create_app()` function to configure the Flask application with proper security headers, CORS settings, and proxy handling
- **Database Integration**: SQLAlchemy with Flask-SQLAlchemy for ORM functionality, featuring a `LinkClick` model for tracking user interactions
- **Error Handling**: Comprehensive logging throughout the application with retry mechanisms for database operations
- **Development vs Production**: Environment-aware configuration with different database handling for development and production environments

### Data Storage Solutions
The application uses a flexible database configuration:

- **Primary Database**: Configured to use PostgreSQL in production via the `DATABASE_URL` environment variable
- **Fallback Database**: Falls back to SQLite in-memory database for development when PostgreSQL is not available
- **Connection Management**: Implements connection pooling with pre-ping functionality and connection recycling for reliability
- **Schema Management**: Uses SQLAlchemy's `db.create_all()` for table creation with plans to migrate to Flask-Migrate for better schema management

### Authentication and Authorization
Currently implements basic security measures:

- **Session Security**: Configured with secure session cookies and HTTP-only flags
- **HTTPS Enforcement**: Forces HTTPS connections through the `PREFERRED_URL_SCHEME` configuration
- **CORS Configuration**: Allows cross-origin requests with proper credential handling
- **Proxy Headers**: Uses ProxyFix middleware to handle reverse proxy headers correctly

## External Dependencies

### Third-Party Services
- **Domain Management**: Uses Cloudflare for DNS management, DDoS protection, and SSL certificate handling for the custom domain treyharnden.com
- **Analytics**: Integrates Google Analytics (gtag.js) with tracking ID G-FT0YPCYY8N for visitor analytics
- **Content Delivery**: Uses Bootstrap CDN for CSS framework and Font Awesome CDN for social media icons

### Database and Infrastructure
- **Database**: PostgreSQL as the primary database system with psycopg2-binary as the database adapter
- **Deployment Platform**: Hosted on Replit with custom domain configuration and automatic HTTPS
- **Application Server**: Uses Gunicorn as the WSGI server for production deployment with multi-worker configuration

### Python Libraries
- **Web Framework**: Flask 3.1.0+ as the core web framework with Flask-CORS for cross-origin request handling
- **Database ORM**: SQLAlchemy 2.0.36+ with Flask-SQLAlchemy 3.1.1+ for database operations
- **Validation**: email-validator for input validation
- **Production Server**: Gunicorn for production WSGI serving with Werkzeug as the underlying WSGI toolkit

### Frontend Libraries
- **CSS Framework**: Bootstrap 5.3.0 for responsive design and UI components
- **Icons**: Font Awesome 6.4.0 for social media and UI icons
- **JavaScript**: Vanilla JavaScript with modern ES6+ features for dynamic functionality