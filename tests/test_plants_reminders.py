"""Tests for Plants and Reminders."""
from datetime import datetime, timezone
from bson.objectid import ObjectId


def test_plants_index_empty(auth_client):
    """Test plants page loads with empty list."""
    res = auth_client.get('/plants/')
    assert res.status_code == 200


def test_add_plant(auth_client, test_db, registered_user):
    """Test creating a new plant profile."""
    res = auth_client.post('/plants/add', data={
        'name': 'North Field Tomato',
        'crop_type': 'Tomato',
        'location': 'Zone A'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"added successfully" in res.data or b"North Field Tomato" in res.data

    plant = test_db.plants.find_one({'user_id': str(registered_user['_id'])})
    assert plant is not None
    assert plant['name'] == 'North Field Tomato'
    assert plant['crop_type'] == 'Tomato'


def test_add_plant_care_activity(auth_client, test_db, registered_user):
    """Test logging a care activity on a plant."""
    user_id = str(registered_user['_id'])
    plant_id = test_db.plants.insert_one({
        'user_id': user_id,
        'name': 'Apple Orchard 1',
        'crop_type': 'Apple',
        'status': 'Healthy',
        'created_at': datetime.now(timezone.utc)
    }).inserted_id

    res = auth_client.post(f'/plants/{str(plant_id)}/care', data={
        'title': 'Applied Organic Neem Spray',
        'description': 'Preventative measure before monsoon'
    }, follow_redirects=True)
    assert res.status_code == 200

    care_case = test_db.care_cases.find_one({'plant_id': str(plant_id)})
    assert care_case is not None
    assert care_case['title'] == 'Applied Organic Neem Spray'


def test_reminders_schedule_and_complete(auth_client, test_db, registered_user):
    """Test scheduling and marking a reminder as completed."""
    user_id = str(registered_user['_id'])
    plant_id = str(test_db.plants.insert_one({
        'user_id': user_id,
        'name': 'Grape Vineyard',
        'crop_type': 'Grape'
    }).inserted_id)

    # Schedule reminder
    res_add = auth_client.post('/reminders/add', data={
        'plant_id': plant_id,
        'title': 'Check for Powdery Mildew',
        'due_date': '2026-10-25'
    }, follow_redirects=True)
    assert res_add.status_code == 200

    reminder = test_db.reminders.find_one({'user_id': user_id, 'title': 'Check for Powdery Mildew'})
    assert reminder is not None
    assert reminder['status'] == 'pending'

    # Complete reminder
    reminder_id = str(reminder['_id'])
    res_comp = auth_client.post(f'/reminders/{reminder_id}/complete', follow_redirects=True)
    assert res_comp.status_code == 200

    updated = test_db.reminders.find_one({'_id': ObjectId(reminder_id)})
    assert updated['status'] == 'completed'
