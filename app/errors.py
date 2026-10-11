"""
Centralized error handling.

Provides consistent error responses for both HTML and JSON API requests.
External service failures must not crash the entire application.
"""

from flask import render_template, request, jsonify, current_app


class AppError(Exception):
    """Base application error."""

    def __init__(self, message, code='INTERNAL_ERROR', status_code=500, details=None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class ValidationError(AppError):
    def __init__(self, message, details=None):
        super().__init__(message, code='VALIDATION_ERROR', status_code=400, details=details)


class AuthenticationError(AppError):
    def __init__(self, message='Authentication required.'):
        super().__init__(message, code='AUTHENTICATION_REQUIRED', status_code=401)


class AuthorizationError(AppError):
    def __init__(self, message='You do not have permission to access this resource.'):
        super().__init__(message, code='FORBIDDEN', status_code=403)


class NotFoundError(AppError):
    def __init__(self, message='Resource not found.'):
        super().__init__(message, code='NOT_FOUND', status_code=404)


class InvalidImageError(ValidationError):
    def __init__(self, message='The uploaded file is not a valid plant image.'):
        super().__init__(message)
        self.code = 'INVALID_IMAGE'


class ModelUnavailableError(AppError):
    def __init__(self, message='The prediction model is currently unavailable.'):
        super().__init__(message, code='MODEL_UNAVAILABLE', status_code=503)


class ExternalServiceError(AppError):
    def __init__(self, service_name, message=None):
        msg = message or f'{service_name} is temporarily unavailable.'
        super().__init__(msg, code='EXTERNAL_SERVICE_ERROR', status_code=503)
        self.service_name = service_name


class RateLimitError(AppError):
    def __init__(self, message='Too many requests. Please try again later.'):
        super().__init__(message, code='RATE_LIMIT_EXCEEDED', status_code=429)


def _wants_json():
    """Check if the client prefers JSON responses."""
    return (
        request.accept_mimetypes.best == 'application/json'
        or request.path.startswith('/api/')
        or request.is_json
    )


def _error_response(error_code, message, status_code, details=None):
    """Create a consistent error response."""
    if _wants_json():
        body = {
            'success': False,
            'error': {
                'code': error_code,
                'message': message,
            }
        }
        if details:
            body['error']['details'] = details
        return jsonify(body), status_code

    # HTML response
    template = f'{status_code}.html'
    try:
        return render_template(template, error_message=message), status_code
    except Exception:
        return render_template('500.html', error_message=message), status_code


def register_error_handlers(app):
    """Register all error handlers on the Flask app."""

    @app.errorhandler(AppError)
    def handle_app_error(error):
        current_app.logger.warning(
            "AppError [%s]: %s", error.code, error.message
        )
        return _error_response(error.code, error.message, error.status_code, error.details)

    @app.errorhandler(400)
    def handle_bad_request(error):
        return _error_response('BAD_REQUEST', 'Bad request.', 400)

    @app.errorhandler(401)
    def handle_unauthorized(error):
        return _error_response('UNAUTHORIZED', 'Authentication required.', 401)

    @app.errorhandler(403)
    def handle_forbidden(error):
        return _error_response('FORBIDDEN', 'Access denied.', 403)

    @app.errorhandler(404)
    def handle_not_found(error):
        return _error_response('NOT_FOUND', 'Page not found.', 404)

    @app.errorhandler(413)
    def handle_too_large(error):
        return _error_response(
            'FILE_TOO_LARGE',
            'File is too large. Maximum size is 10MB.',
            413
        )

    @app.errorhandler(429)
    def handle_rate_limit(error):
        return _error_response(
            'RATE_LIMIT_EXCEEDED',
            'Too many requests. Please try again later.',
            429
        )

    @app.errorhandler(500)
    def handle_server_error(error):
        current_app.logger.error("Internal server error: %s", error, exc_info=True)
        return _error_response(
            'INTERNAL_ERROR',
            'An unexpected error occurred. Please try again later.',
            500
        )
