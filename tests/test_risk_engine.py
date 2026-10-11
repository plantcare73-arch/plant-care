"""Tests for Weather-Driven Risk Engine."""
from app.risk_engine.evaluator import evaluate_user_risks


def test_risk_evaluation_late_blight(test_db, registered_user):
    """Test high humidity and warm temp triggers late blight risk for tomato."""
    user_id = str(registered_user['_id'])
    plant_id = test_db.plants.insert_one({
        'user_id': user_id,
        'crop_type': 'Tomato',
        'variety': 'Roma'
    }).inserted_id

    # Weather: 85% humidity, 24°C
    weather = {'temp': 24, 'humidity': 85, 'rain': False}
    evaluate_user_risks(user_id, weather)

    alerts = list(test_db.risk_alerts.find({'user_id': user_id}))
    assert len(alerts) >= 1
    assert any("Late Blight" in a['title'] for a in alerts)
    assert any(a['severity'] == 'danger' for a in alerts)


def test_risk_evaluation_heat_stress(test_db, registered_user):
    """Test extreme heat (>35C) triggers heat stress warning."""
    user_id = str(registered_user['_id'])
    test_db.plants.insert_one({
        'user_id': user_id,
        'crop_type': 'Corn',
        'variety': 'Sweet Corn'
    })

    weather = {'temp': 38, 'humidity': 30, 'rain': False}
    evaluate_user_risks(user_id, weather)

    alerts = list(test_db.risk_alerts.find({'user_id': user_id}))
    assert len(alerts) >= 1
    assert any("Heat Stress" in a['title'] for a in alerts)


def test_risk_evaluation_no_duplicate_unread(test_db, registered_user):
    """Test identical unread alerts are not duplicated on re-evaluation."""
    user_id = str(registered_user['_id'])
    test_db.plants.insert_one({
        'user_id': user_id,
        'crop_type': 'Tomato',
        'variety': 'Roma'
    })

    weather = {'temp': 24, 'humidity': 85, 'rain': False}
    evaluate_user_risks(user_id, weather)
    evaluate_user_risks(user_id, weather)

    # Should only create 1 alert
    alerts = list(test_db.risk_alerts.find({'user_id': user_id}))
    assert len(alerts) == 1


def test_risk_evaluation_mild_weather_safe(test_db, registered_user):
    """Test mild weather triggers no alerts."""
    user_id = str(registered_user['_id'])
    test_db.plants.insert_one({
        'user_id': user_id,
        'crop_type': 'Tomato',
        'variety': 'Roma'
    })

    weather = {'temp': 22, 'humidity': 50, 'rain': False}
    evaluate_user_risks(user_id, weather)

    alerts = list(test_db.risk_alerts.find({'user_id': user_id}))
    assert len(alerts) == 0
