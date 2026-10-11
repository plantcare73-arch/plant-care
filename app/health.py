"""
Health check endpoints.

Exposes application health without leaking sensitive internal details.
"""

from flask import jsonify, current_app
from .extensions import get_db


def register_health_routes(app):
    """Register health check endpoints."""

    @app.route('/ping')
    def ping():
        """Ultra-fast keepalive endpoint for cron jobs (zero DB/ML overhead)."""
        return jsonify({'status': 'ok'}), 200

    @app.route('/health')
    def health():
        """Overall application health."""
        db_status = _check_database()
        model_status = _check_model()

        overall = 'healthy' if (
            db_status == 'healthy' and model_status in ('loaded', 'demo_mode')
        ) else 'degraded'

        return jsonify({
            'status': overall,
            'database': db_status,
            'model': model_status,
        }), 200 if overall == 'healthy' else 503

    @app.route('/health/database')
    def health_database():
        """Database health check."""
        status = _check_database()
        code = 200 if status == 'healthy' else 503
        return jsonify({'status': status}), code

    @app.route('/health/model')
    def health_model():
        """Model health check."""
        status = _check_model()
        code = 200 if status in ('loaded', 'demo_mode') else 503
        return jsonify({'status': status}), code


def _check_database():
    """Check MongoDB connectivity."""
    try:
        database = get_db()
        if database is None:
            return 'unavailable'
        database.command('ping')
        return 'healthy'
    except Exception as e:
        current_app.logger.error("Database health check failed: %s", e)
        return 'unavailable'


def _check_model():
    """Check ML model status."""
    try:
        from .ml.model_manager import model_manager
        if model_manager.is_loaded():
            return 'loaded'
        elif model_manager.is_demo_mode():
            return 'demo_mode'
        return 'not_loaded'
    except Exception as e:
        current_app.logger.error("Model health check failed: %s", e)
        return 'error'
