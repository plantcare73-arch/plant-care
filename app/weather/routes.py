"""
Weather routes.
"""
from flask import request, redirect, url_for, session, flash
from . import weather_bp
from ..extensions import get_db
from ..utils.decorators import login_required

@weather_bp.route('/set-location', methods=['POST'])
@login_required
def set_location():
    city = request.form.get('city', '').strip()
    if city:
        db = get_db()
        from bson.objectid import ObjectId
        db['users'].update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$set': {'farm_location': city}}
        )
        flash(f'Weather location updated to {city}.', 'success')
    else:
        flash('Please enter a valid city.', 'error')
        
    return redirect(url_for('main.dashboard'))
