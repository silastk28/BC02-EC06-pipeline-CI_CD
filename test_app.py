import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_route(client):
    """Teste que la route principale renvoie un code 200 et du JSON"""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == "success"
    assert "TechCorp" in data['message']

def test_health_route_structure(client):
    """Teste que la route /health renvoie une structure correcte"""
    response = client.get('/health')
    # Le status code peut être 200 ou 500 selon si Mongo tourne pendant le test unitaire,
    # mais la structure du JSON retourné doit contenir 'status' et 'services'
    data = response.get_json()
    assert 'status' in data
    assert 'services' in data