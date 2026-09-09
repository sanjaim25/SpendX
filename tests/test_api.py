import pytest
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app import create_app, db


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test_secret'
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    client.post('/api/register', json={
        'name': 'Test User', 'email': 'test@test.com', 'password': 'password123'
    })
    response = client.post('/api/login', json={
        'email': 'test@test.com', 'password': 'password123'
    })
    token = json.loads(response.data)['access_token']
    return {'Authorization': f'Bearer {token}'}


def test_health_check(client):
    response = client.get('/api/health')
    assert response.status_code == 200


def test_register(client):
    response = client.post('/api/register', json={
        'name': 'Sanjai', 'email': 'sanjai@test.com', 'password': 'secure123'
    })
    assert response.status_code == 201


def test_login(client):
    client.post('/api/register', json={
        'name': 'User', 'email': 'user@test.com', 'password': 'pass123'
    })
    response = client.post('/api/login', json={
        'email': 'user@test.com', 'password': 'pass123'
    })
    assert response.status_code == 200
    assert 'access_token' in json.loads(response.data)


def test_add_expense(client, auth_headers):
    response = client.post('/api/expenses', json={
        'description': 'Swiggy order', 'amount': 350, 'date': '2024-03-01'
    }, headers=auth_headers)
    assert response.status_code == 201


def test_get_expenses(client, auth_headers):
    response = client.get('/api/expenses', headers=auth_headers)
    assert response.status_code == 200
    assert 'expenses' in json.loads(response.data)
