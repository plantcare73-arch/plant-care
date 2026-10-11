"""
Main pages routes.
"""
from flask import render_template, session, redirect, request, url_for
from . import main_bp
from ..utils.decorators import login_required
from ..extensions import get_db

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/sw.js')
def service_worker():
    from flask import send_from_directory
    import os
    from flask import current_app
    return send_from_directory(os.path.join(current_app.root_path, 'static'), 'sw.js', mimetype='application/javascript')

@main_bp.route('/manifest.json')
def manifest():
    from flask import send_from_directory
    import os
    from flask import current_app
    return send_from_directory(os.path.join(current_app.root_path, 'static'), 'manifest.json', mimetype='application/json')

@main_bp.route('/lang/<lang>')
def set_language(lang):
    if lang in ['en', 'hi', 'kn']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('main.index'))




@main_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    db = get_db()
    predictions_col = db['predictions']
    
    recent_predictions = list(
        predictions_col.find({'user_id': user_id})
        .sort('created_at', -1)
        .limit(5)
    )
    total_predictions = predictions_col.count_documents({'user_id': user_id})
    from bson.objectid import ObjectId
    user = db['users'].find_one({'_id': ObjectId(user_id)})
    city = user.get('farm_location', 'San Francisco') if user else 'San Francisco'
    
    # Weather & Advice
    from ..weather.services import WeatherService, get_irrigation_advice
    weather_svc = WeatherService()
    weather_data = weather_svc.get_weather(city)
    
    # We will pick a default crop from their plants or fallback
    first_plant = db['plants'].find_one({'user_id': user_id})
    primary_crop = first_plant['crop_type'] if first_plant else "General Crops"
    irrigation_advice = get_irrigation_advice(weather_data, primary_crop)
    
    # Risk Engine Evaluation
    from ..risk_engine.evaluator import evaluate_user_risks
    evaluate_user_risks(user_id, weather_data)
    
    # Fetch active risk alerts
    active_alerts = list(db['risk_alerts'].find({'user_id': user_id, 'is_read': False}).sort('created_at', -1))
    
    return render_template(
        'dashboard.html',
        predictions=recent_predictions,
        total_predictions=total_predictions,
        weather=weather_data,
        city=city,
        irrigation_advice=irrigation_advice,
        active_alerts=active_alerts
    )
