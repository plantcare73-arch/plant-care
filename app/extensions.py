"""
Application extensions initialization.

Manages MongoDB connection and shared utilities.
"""

from pymongo import MongoClient
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel

# Module-level references
mongo_client = None
db = None
csrf = CSRFProtect()

def get_locale():
    from flask import session, request
    # Use language from session if set, else check Accept-Language header
    return session.get('lang', request.accept_languages.best_match(['en', 'hi', 'kn'])) or 'en'

babel = Babel()


def init_extensions(app):
    """Initialize all application extensions."""
    global mongo_client, db
    import os
    
    csrf.init_app(app)
    babel.init_app(app, locale_selector=get_locale)

    # MongoDB
    uri = app.config['MONGODB_URI']
    mongo_kwargs = {
        'serverSelectionTimeoutMS': 4000,
        'connectTimeoutMS': 4000,
    }
    if 'mongodb+srv' in uri or 'tls=true' in uri.lower() or 'ssl=true' in uri.lower():
        try:
            import certifi
            mongo_kwargs['tlsCAFile'] = certifi.where()
        except ImportError:
            pass
        mongo_kwargs['tlsAllowInvalidCertificates'] = True

    mongo_client = MongoClient(uri, **mongo_kwargs)
    db = mongo_client[app.config['DATABASE_NAME']]

    # Create upload directory
    os.makedirs(app.config['UPLOAD_DIR'], exist_ok=True)
    os.makedirs(os.path.dirname(app.config['MODEL_PATH']) or 'models', exist_ok=True)

    # Setup database indexes gracefully
    try:
        _ensure_indexes(db)
    except Exception as e:
        app.logger.warning("Could not ensure indexes on startup (will retry on operations): %s", e)

    # Store db reference on app for easy access
    app.db = db

    app.logger.info(
        "Extensions initialized. DB: %s", app.config['DATABASE_NAME']
    )


def _ensure_indexes(database):
    """Create required MongoDB indexes."""
    # Users: unique email
    database['users'].create_index('email', unique=True)

    # Predictions: user_id + created_at for history queries
    database['predictions'].create_index([
        ('user_id', 1),
        ('created_at', -1),
    ])
    database['predictions'].create_index('predicted_class')

    # Reviews: created_at for listing
    database['reviews'].create_index('created_at')

    # Diseases: unique identifier
    database['diseases'].create_index('class_name', unique=True)
    database['diseases'].create_index('crop')

    # Treatments: disease reference
    database['treatments'].create_index('disease_class')
    database['treatments'].create_index('crop')

    # Plants: user_id
    database['plants'].create_index('user_id')

    # Care cases: user_id + status
    database['care_cases'].create_index([('user_id', 1), ('status', 1)])

    # Reminders: user_id + due_date
    database['reminders'].create_index([('user_id', 1), ('due_date', 1)])
    database['reminders'].create_index('status')

    # Notifications: user_id + read status
    database['notifications'].create_index([('user_id', 1), ('read', 1)])
    database['notifications'].create_index(
        'expires_at', expireAfterSeconds=0
    )

    # Weather cache: location + expiry
    database['weather_cache'].create_index(
        'expires_at', expireAfterSeconds=0
    )
    database['weather_cache'].create_index('location_key', unique=True)

    # Risk rules
    database['risk_rules'].create_index([('crop', 1), ('disease_class', 1)])

    # Risk alerts
    database['risk_alerts'].create_index([('user_id', 1), ('created_at', -1)])

    # Experts
    database['experts'].create_index([('location.coordinates', '2dsphere')])
    database['experts'].create_index('category')

    # Agricultural stores
    database['agricultural_stores'].create_index(
        [('location.coordinates', '2dsphere')]
    )

    # Model versions
    database['model_versions'].create_index('version', unique=True)

    # Audit logs
    database['audit_logs'].create_index([('user_id', 1), ('created_at', -1)])
    database['audit_logs'].create_index('action')


def get_db():
    """Get the database instance."""
    return db
