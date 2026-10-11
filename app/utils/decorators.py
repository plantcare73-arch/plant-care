"""
Authentication and authorization decorators.
"""

from functools import wraps
from flask import session, flash, redirect, url_for, request, jsonify


def login_required(f):
    """Require an authenticated session."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            if request.accept_mimetypes.best == 'application/json' or request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'error': {'code': 'AUTHENTICATION_REQUIRED', 'message': 'Please log in.'}
                }), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Require an authenticated admin session."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'error': {'code': 'AUTHENTICATION_REQUIRED', 'message': 'Please log in.'}
                }), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('user_role') != 'admin':
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'error': {'code': 'FORBIDDEN', 'message': 'Admin access required.'}
                }), 403
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated
