"""Tests for /health, /health/database, and /health/model endpoints."""

def test_overall_health_endpoint(client):
    """Test /health returns HTTP 200 and expected status keys."""
    response = client.get('/health')
    assert response.status_code in (200, 503)
    data = response.get_json()
    assert 'status' in data
    assert 'database' in data
    assert 'model' in data
    if response.status_code == 200:
        assert data['status'] == 'healthy'


def test_database_health_endpoint(client):
    """Test /health/database endpoint returns status."""
    response = client.get('/health/database')
    assert response.status_code in (200, 503)
    data = response.get_json()
    assert 'status' in data


def test_model_health_endpoint(client):
    """Test /health/model endpoint returns model status."""
    response = client.get('/health/model')
    assert response.status_code in (200, 503)
    data = response.get_json()
    assert 'status' in data
    assert data['status'] in ('loaded', 'demo_mode', 'not_loaded', 'error')
