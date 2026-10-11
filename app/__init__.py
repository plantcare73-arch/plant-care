"""
AI Plant Care — Application Package

Intelligent Plant Disease Detection and Agricultural Assistance Platform.
"""

from flask import Flask
from .config import Config
from .extensions import init_extensions
from .logging_config import setup_logging


def create_app(config_class=Config):
    """Application factory pattern."""
    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='../static',
    )
    app.config.from_object(config_class)

    # Setup structured logging
    setup_logging(app)

    # Initialize extensions (DB, CSRF, etc.)
    init_extensions(app)

    # Initialize ML Model Manager
    from .ml import model_manager
    import os
    model_path = os.path.join(app.root_path, '..', 'models', 'model_weights.h5')
    model_manager.load_model(model_path)

    # Register blueprints
    _register_blueprints(app)

    # Register error handlers
    _register_error_handlers(app)

    # Register health checks
    _register_health_routes(app)

    app.logger.info("AI Plant Care application initialized.")
    return app


def _register_blueprints(app):
    """Register all application blueprints."""
    from .auth.routes import auth_bp
    from .predictions.routes import predictions_bp
    from .main.routes import main_bp
    from .reviews.routes import reviews_bp
    from .admin.routes import admin_bp
    from .plants.routes import plants_bp
    from .reminders.routes import reminders_bp
    from .weather.routes import weather_bp
    from .risk_engine.routes import risk_bp
    from .location.routes import bp as location_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(predictions_bp, url_prefix='/predictions')
    app.register_blueprint(reviews_bp, url_prefix='/reviews')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(plants_bp, url_prefix='/plants')
    app.register_blueprint(reminders_bp, url_prefix='/reminders')
    app.register_blueprint(weather_bp, url_prefix='/weather')
    app.register_blueprint(risk_bp, url_prefix='/risk')
    app.register_blueprint(location_bp, url_prefix='/location')


def _register_error_handlers(app):
    """Register centralized error handlers."""
    from .errors import register_error_handlers
    register_error_handlers(app)


def _register_health_routes(app):
    """Register health check endpoints."""
    from .health import register_health_routes
    register_health_routes(app)
