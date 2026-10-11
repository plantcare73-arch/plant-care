"""Tests for Admin Dashboard, User Management, and Auditing."""
from bson.objectid import ObjectId


def test_admin_dashboard_unauthenticated(client):
    """Test anonymous access to admin dashboard redirects to login."""
    res = client.get('/admin/')
    assert res.status_code == 302
    assert '/auth/login' in res.headers['Location']


def test_admin_dashboard_farmer_forbidden(auth_client):
    """Test regular farmer cannot access admin dashboard."""
    res = auth_client.get('/admin/', follow_redirects=True)
    assert res.status_code == 200
    assert b"Administrator access required" in res.data or b"admin" not in res.data.lower()


def test_admin_dashboard_admin_success(admin_client):
    """Test admin user successfully accesses admin dashboard."""
    res = admin_client.get('/admin/')
    assert res.status_code == 200
    assert b"Admin" in res.data
    assert b"User Management" in res.data or b"Total Users" in res.data


def test_admin_suspend_user_toggle(admin_client, test_db, registered_user):
    """Test admin can suspend and unsuspend a user."""
    user_id = str(registered_user['_id'])
    
    # Toggle to suspended
    res = admin_client.post(f'/admin/suspend/{user_id}')
    assert res.status_code == 200
    user = test_db.users.find_one({'_id': ObjectId(user_id)})
    assert user.get('suspended') is True

    # Check audit log was recorded
    audit_log = test_db.audit_logs.find_one({'action': 'toggle_suspend_user'})
    assert audit_log is not None
    assert audit_log['target_id'] == user_id

    # Toggle back to unsuspended
    res2 = admin_client.post(f'/admin/suspend/{user_id}')
    assert res2.status_code == 200
    user = test_db.users.find_one({'_id': ObjectId(user_id)})
    assert user.get('suspended') is False


def test_admin_diseases_management(admin_client, test_db):
    """Test admin can view and update diseases & treatments."""
    res_get = admin_client.get('/admin/diseases')
    assert res_get.status_code == 200

    # Update disease
    res_post = admin_client.post('/admin/diseases/update', data={
        'class_name': 'Tomato___Early_blight',
        'name': 'Early Blight of Tomato',
        'crop': 'Tomato',
        'description': 'Fungal pathogen Alternaria solani',
        'symptoms': 'Concentric rings on leaves\nYellowing halo',
        'prevention': 'Rotate crops\nKeep foliage dry',
        'chemical_control': 'Copper fungicide',
        'biological_control': 'Trichoderma harzianum'
    }, follow_redirects=True)
    assert res_post.status_code == 200

    # Verify update in diseases collection
    disease = test_db.diseases.find_one({'class_name': 'Tomato___Early_blight'})
    assert disease is not None
    assert disease['name'] == 'Early Blight of Tomato'

    # Verify treatment update
    treatment = test_db.treatments.find_one({'disease_class': 'Tomato___Early_blight'})
    assert treatment is not None
    assert 'Copper fungicide' in treatment['chemical_control']


def test_admin_risk_rules_crud(admin_client, test_db):
    """Test admin can configure, update, and delete risk rules."""
    res_get = admin_client.get('/admin/risk_rules')
    assert res_get.status_code == 200

    # Add rule
    res_add = admin_client.post('/admin/risk_rules/update', data={
        'disease_class': 'Potato___Late_blight',
        'crop': 'Potato',
        'min_temp': 12,
        'max_temp': 24,
        'min_humidity': 80,
        'max_humidity': 100,
        'condition': 'Rain'
    }, follow_redirects=True)
    assert res_add.status_code == 200

    rule = test_db.risk_rules.find_one({'disease_class': 'Potato___Late_blight', 'crop': 'Potato'})
    assert rule is not None
    assert rule['min_humidity'] == 80.0

    # Delete rule
    res_del = admin_client.post('/admin/risk_rules/delete', data={
        'disease_class': 'Potato___Late_blight',
        'crop': 'Potato'
    }, follow_redirects=True)
    assert res_del.status_code == 200

    rule_after = test_db.risk_rules.find_one({'disease_class': 'Potato___Late_blight', 'crop': 'Potato'})
    assert rule_after is None
