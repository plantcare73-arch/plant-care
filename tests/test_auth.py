"""Tests for Authentication workflows (register, login, logout, security)."""
from flask import session


def test_register_success(client, test_db):
    """Test standard registration with valid inputs."""
    res = client.post('/auth/register', data={
        'name': 'New Farmer',
        'email': 'newfarmer@example.com',
        'password': 'StrongPassword123!'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Registration successful" in res.data or b"log in" in res.data.lower()

    # Verify user exists in database
    user = test_db.users.find_one({'email': 'newfarmer@example.com'})
    assert user is not None
    assert user['name'] == 'New Farmer'
    assert user['role'] == 'farmer'


def test_register_duplicate_email(client, registered_user):
    """Test registration with already registered email fails."""
    res = client.post('/auth/register', data={
        'name': 'Duplicate User',
        'email': registered_user['email'],
        'password': 'AnotherPassword123!'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Email already registered" in res.data


def test_register_invalid_email(client):
    """Test registration with invalid email format."""
    res = client.post('/auth/register', data={
        'name': 'Invalid Email User',
        'email': 'not-an-email',
        'password': 'Password123!'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Invalid email" in res.data


def test_register_weak_password(client):
    """Test registration with short/weak password fails."""
    res = client.post('/auth/register', data={
        'name': 'Weak User',
        'email': 'weak@example.com',
        'password': '123'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Password must be at least" in res.data or b"error" in res.data.lower()


def test_login_success(client, registered_user):
    """Test logging in with valid credentials sets session."""
    res = client.post('/auth/login', data={
        'email': registered_user['email'],
        'password': 'SecretPass123!'
    }, follow_redirects=True)
    assert res.status_code == 200
    with client.session_transaction() as sess:
        assert sess['user_email'] == registered_user['email']
        assert sess['user_role'] == 'farmer'


def test_login_wrong_password(client, registered_user):
    """Test logging in with invalid password fails."""
    res = client.post('/auth/login', data={
        'email': registered_user['email'],
        'password': 'WrongPassword123!'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Invalid email or password" in res.data
    with client.session_transaction() as sess:
        assert 'user_id' not in sess


def test_login_suspended_account(client, test_db, registered_user):
    """Test that suspended accounts cannot log in."""
    test_db.users.update_one(
        {'_id': registered_user['_id']},
        {'$set': {'suspended': True}}
    )
    res = client.post('/auth/login', data={
        'email': registered_user['email'],
        'password': 'SecretPass123!'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"suspended" in res.data.lower()
    with client.session_transaction() as sess:
        assert 'user_id' not in sess


def test_logout(auth_client):
    """Test logout clears session."""
    res = auth_client.get('/auth/logout', follow_redirects=True)
    assert res.status_code == 200
    with auth_client.session_transaction() as sess:
        assert 'user_id' not in sess


def test_forgot_password_generic_response(client):
    """Test forgot password gives generic response preventing email enumeration."""
    res = client.post('/auth/forgot-password', data={
        'email': 'nonexistent@example.com'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"password reset link" in res.data.lower()
