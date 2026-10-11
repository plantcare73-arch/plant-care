import io
import pytest
from PIL import Image
import bcrypt
from app import create_app
from app.config import TestingConfig
from app.extensions import get_db


@pytest.fixture(scope='session')
def app():
    """Create and configure application for testing."""
    application = create_app(TestingConfig)
    application.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key-fixture',
        'DATABASE_NAME': 'plant_disease_test_db',
    })
    yield application


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture(autouse=True)
def clean_db(app):
    """Clean test database collections before each test."""
    with app.app_context():
        database = get_db()
        if database is not None:
            for collection_name in [
                'users', 'predictions', 'plants', 'reminders', 
                'risk_rules', 'risk_alerts', 'audit_logs', 'diseases', 
                'treatments', 'care_cases', 'reviews'
            ]:
                database[collection_name].delete_many({})
    yield


@pytest.fixture
def test_db(app):
    """Provide the test database."""
    with app.app_context():
        return get_db()


@pytest.fixture
def registered_user(app, test_db):
    """Create a regular test user."""
    salt = bcrypt.gensalt()
    pw_hash = bcrypt.hashpw(b"SecretPass123!", salt)
    user_doc = {
        'name': 'Test Farmer',
        'email': 'farmer@example.com',
        'password': pw_hash,
        'role': 'farmer',
        'is_active': True,
        'preferred_language': 'en'
    }
    result = test_db.users.insert_one(user_doc)
    user_doc['_id'] = result.inserted_id
    return user_doc


@pytest.fixture
def admin_user(app, test_db):
    """Create an administrator test user."""
    salt = bcrypt.gensalt()
    pw_hash = bcrypt.hashpw(b"AdminSecret123!", salt)
    user_doc = {
        'name': 'Admin User',
        'email': 'admin@example.com',
        'password': pw_hash,
        'role': 'admin',
        'is_active': True,
        'preferred_language': 'en'
    }
    result = test_db.users.insert_one(user_doc)
    user_doc['_id'] = result.inserted_id
    return user_doc


@pytest.fixture
def auth_client(client, registered_user):
    """Client authenticated as standard farmer."""
    with client.session_transaction() as sess:
        sess['user_id'] = str(registered_user['_id'])
        sess['user_name'] = registered_user['name']
        sess['user_email'] = registered_user['email']
        sess['user_role'] = registered_user['role']
    return client


@pytest.fixture
def admin_client(client, admin_user):
    """Client authenticated as administrator."""
    with client.session_transaction() as sess:
        sess['user_id'] = str(admin_user['_id'])
        sess['user_name'] = admin_user['name']
        sess['user_email'] = admin_user['email']
        sess['user_role'] = admin_user['role']
    return client


@pytest.fixture
def sample_image():
    """Generate in-memory valid JPEG image bytes."""
    img = Image.new('RGB', (224, 224), color=(73, 109, 137))
    byte_arr = io.BytesIO()
    img.save(byte_arr, format='JPEG')
    byte_arr.seek(0)
    return (byte_arr, 'test_leaf.jpg')


@pytest.fixture
def sample_invalid_file():
    """Generate in-memory invalid non-image file."""
    byte_arr = io.BytesIO(b"This is not an image file.")
    byte_arr.seek(0)
    return (byte_arr, 'notes.txt')
