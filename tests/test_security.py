"""Tests for Security Hardening: CSRF, Path Traversal, and User Isolation."""
from datetime import datetime, timezone
from bson.objectid import ObjectId


def test_session_cookie_security_flags(client, registered_user):
    """Verify session cookie contains security attributes (HttpOnly)."""
    res = client.post('/auth/login', data={
        'email': registered_user['email'],
        'password': 'SecretPass123!'
    })
    # Check Set-Cookie header
    cookie_header = res.headers.get('Set-Cookie', '')
    assert 'HttpOnly' in cookie_header or 'httponly' in cookie_header.lower()


def test_user_data_isolation_prediction_view(client, test_db, registered_user):
    """Verify a farmer cannot view another farmer's prediction record."""
    # Create prediction belonging to user A
    user_a_pred_id = str(test_db.predictions.insert_one({
        'user_id': str(registered_user['_id']),
        'image_filename': 'secret_leaf.jpg',
        'predicted_class': 'Apple___healthy',
        'created_at': datetime.now(timezone.utc)
    }).inserted_id)

    # Log in as user B
    user_b_id = str(test_db.users.insert_one({
        'name': 'Farmer B',
        'email': 'farmerb@example.com',
        'password': 'hashed_password',
        'role': 'farmer',
        'is_active': True
    }).inserted_id)

    with client.session_transaction() as sess:
        sess['user_id'] = user_b_id
        sess['user_email'] = 'farmerb@example.com'
        sess['user_role'] = 'farmer'

    res = client.get(f'/predictions/result/{user_a_pred_id}', follow_redirects=True)
    # Should not display User A's data, should redirect to history with flash
    assert b"Prediction not found" in res.data or res.status_code in (302, 404, 200)
    assert b"secret_leaf.jpg" not in res.data


def test_path_traversal_prevention_uploads(auth_client):
    """Verify path traversal payloads in upload filenames are rejected or safe."""
    # Attempt path traversal
    res = auth_client.get('/predictions/uploads/..%2f..%2fapp%2fconfig.py')
    assert res.status_code in (404, 400)

    res2 = auth_client.get('/predictions/uploads/../../run.py')
    assert res2.status_code in (404, 400)


def test_csrf_protection_enabled(app):
    """Verify CSRF protection blocks requests when CSRF is enforced."""
    # Create test client with CSRF explicitly enabled
    app.config['WTF_CSRF_ENABLED'] = True
    test_client = app.test_client()

    # POST without CSRF token
    res = test_client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'Password123!'
    })
    # Should fail with 400 Bad Request due to missing CSRF token
    assert res.status_code == 400
    assert b"CSRF" in res.data or b"Bad Request" in res.data

    # Revert back
    app.config['WTF_CSRF_ENABLED'] = False
