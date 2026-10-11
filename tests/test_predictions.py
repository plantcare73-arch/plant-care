"""Tests for Prediction, Detection, and History workflows."""
from datetime import datetime, timezone
from bson.objectid import ObjectId


def test_detect_unauthenticated_redirects(client):
    """Test unauthenticated users cannot access detect page."""
    res = client.get('/predictions/detect')
    assert res.status_code == 302
    assert '/auth/login' in res.headers['Location']


def test_detect_page_loads_for_authenticated_user(auth_client):
    """Test authenticated users can load detection page."""
    res = auth_client.get('/predictions/detect')
    assert res.status_code == 200
    assert b"detect" in res.data.lower() or b"upload" in res.data.lower()


def test_upload_invalid_file_extension(auth_client, sample_invalid_file):
    """Test non-image file uploads are rejected with validation error."""
    file_bytes, filename = sample_invalid_file
    data = {
        'leaf_image': (file_bytes, filename)
    }
    res = auth_client.post('/predictions/detect', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert res.status_code == 200
    assert b"Invalid file type" in res.data or b"error" in res.data.lower()


def test_upload_valid_image_success(auth_client, test_db, sample_image):
    """Test valid image file is processed and creates prediction record."""
    file_bytes, filename = sample_image
    data = {
        'leaf_image': (file_bytes, filename)
    }
    res = auth_client.post('/predictions/detect', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert res.status_code == 200
    assert b"confidence" in res.data.lower() or b"treatment" in res.data.lower()

    # Verify prediction record created in database
    predictions = list(test_db.predictions.find())
    assert len(predictions) == 1
    assert 'predicted_class' in predictions[0]
    assert 'confidence' in predictions[0]


def test_prediction_result_view(auth_client, test_db, registered_user):
    """Test accessing result page for existing prediction."""
    pred_doc = {
        'user_id': str(registered_user['_id']),
        'image_filename': 'sample.jpg',
        'predicted_class': 'Tomato___Early_blight',
        'display_name': 'Tomato Early Blight',
        'confidence': 0.94,
        'all_predictions': {'Tomato___Early_blight': 0.94},
        'disease_info': {'disease_name': 'Tomato Early Blight', 'crop': 'Tomato'},
        'created_at': datetime.now(timezone.utc),
    }
    pred_id = str(test_db.predictions.insert_one(pred_doc).inserted_id)

    res = auth_client.get(f'/predictions/result/{pred_id}')
    assert res.status_code == 200
    assert b"Tomato Early Blight" in res.data


def test_prediction_history(auth_client, test_db, registered_user):
    """Test prediction history list returns user records."""
    pred_doc = {
        'user_id': str(registered_user['_id']),
        'image_filename': 'sample.jpg',
        'predicted_class': 'Tomato___Early_blight',
        'display_name': 'Tomato Early Blight',
        'confidence': 0.94,
        'created_at': datetime.now(timezone.utc),
        'disease_info': {'disease': 'Early blight', 'crop': 'Tomato'},
    }
    test_db.predictions.insert_one(pred_doc)

    res = auth_client.get('/predictions/history')
    assert res.status_code == 200
    assert b"Tomato" in res.data
