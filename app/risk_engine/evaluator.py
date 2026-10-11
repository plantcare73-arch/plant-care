"""
Risk Evaluator logic.
"""
from datetime import datetime, timezone
from ..extensions import get_db

def evaluate_user_risks(user_id, weather_data):
    """
    Evaluates risk rules for all plants belonging to a user and generates alerts.
    """
    db = get_db()
    plants = list(db['plants'].find({'user_id': user_id}))
    
    if not plants or not weather_data:
        return
        
    temp = weather_data.get('temp', 25)
    humidity = weather_data.get('humidity', 50)
    rain = weather_data.get('rain', False)
    
    for plant in plants:
        crop = plant.get('crop_type', '').lower()
        
        # Rule 1: High Humidity + Warm Temp for Tomatoes/Potatoes -> Blight Risk
        if humidity >= 80 and temp >= 20 and 'tomato' in crop:
            _create_alert(
                db, 
                user_id, 
                plant['_id'],
                "High Risk: Late Blight", 
                "High humidity and warm temperatures create ideal conditions for Late Blight. Monitor tomato plants closely and consider preventative fungicides.",
                "danger"
            )
            
        # Rule 2: Extreme Heat
        if temp >= 35:
            _create_alert(
                db,
                user_id,
                plant['_id'],
                "Warning: Heat Stress",
                f"Temperatures are exceedingly high ({temp}°C). Ensure {crop} is adequately watered. Consider providing shade if possible.",
                "warning"
            )
            
        # Rule 3: Rain and Fungal Risk
        if rain and humidity >= 85:
            _create_alert(
                db,
                user_id,
                plant['_id'],
                "Warning: Fungal Infection Risk",
                "Rain combined with high humidity increases the chance of fungal infections. Ensure good air circulation around your plants.",
                "warning"
            )


def _create_alert(db, user_id, plant_id, title, message, severity):
    """Creates a risk alert if an identical unread alert doesn't already exist."""
    # Check if a recent identical alert exists and is unread
    existing = db['risk_alerts'].find_one({
        'user_id': user_id,
        'plant_id': plant_id,
        'title': title,
        'is_read': False
    })
    
    if not existing:
        db['risk_alerts'].insert_one({
            'user_id': user_id,
            'plant_id': plant_id,
            'title': title,
            'message': message,
            'severity': severity,  # info, warning, danger
            'is_read': False,
            'created_at': datetime.now(timezone.utc)
        })
