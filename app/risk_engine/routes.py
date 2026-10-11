"""
Routes for Risk Engine (managing alerts).
"""
from flask import request, redirect, url_for, session, flash
from bson.objectid import ObjectId
from . import risk_bp
from ..extensions import get_db
from ..utils.decorators import login_required

@risk_bp.route('/dismiss/<alert_id>', methods=['POST'])
@login_required
def dismiss_alert(alert_id):
    db = get_db()
    db['risk_alerts'].update_one(
        {'_id': ObjectId(alert_id), 'user_id': session['user_id']},
        {'$set': {'is_read': True}}
    )
    return redirect(request.referrer or url_for('main.dashboard'))
