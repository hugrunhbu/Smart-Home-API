import json
import sys
print(sys.executable)
print(sys.path)
import pytest
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from server import SimpleAPIHandler, users  # Import your server code

# Helper function to start the server in a separate thread
def start_server():
    server = HTTPServer(('localhost', 8000), SimpleAPIHandler)
    thread = Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    return server, thread

# Helper function to send HTTP requests
def send_request(method, path, data=None):
    import requests
    url = f'http://localhost:8000{path}'
    headers = {'Content-Type': 'application/json'}
    if method == 'GET':
        response = requests.get(url, headers=headers)
    elif method == 'POST':
        response = requests.post(url, headers=headers, json=data)
    return response

# Fixture to start and stop the server for each test
@pytest.fixture(scope="module")
def server():
    server, thread = start_server()
    yield server
    server.shutdown()
    thread.join()

# Test cases
def test_get_users_empty(server):
    # Test GET /users with an empty list
    response = send_request('GET', '/users')
    assert response.status_code == 200
    assert response.json() == []

def test_create_user(server):
    # Test POST /users to create a user
    user_data = {'name': 'John Doe', 'email': 'john@example.com', 'password': 'password123'}
    response = send_request('POST', '/users', data=user_data)
    assert response.status_code == 201
    assert response.json() == {'id': 1, **user_data}

def test_get_users_with_data(server):
    # Test GET /users after creating a user
    response = send_request('GET', '/users')
    assert response.status_code == 200
    assert response.json() == [{'id': 1, 'name': 'John Doe', 'email': 'john@example.com', 'password': 'password123'}]

def test_create_user_missing_fields(server):
    # Test POST /users with missing fields
    user_data = {'name': 'John Doe', 'email': 'john@example.com'}
    response = send_request('POST', '/users', data=user_data)
    assert response.status_code == 400
    assert response.json() == {'error': 'Missing required fields'}

def test_create_user_invalid_email(server):
    # Test POST /users with an invalid email
    user_data = {'name': 'John Doe', 'email': 'invalid-email', 'password': 'password123'}
    response = send_request('POST', '/users', data=user_data)
    assert response.status_code == 400
    assert response.json() == {'error': 'Invalid email format'}

def test_create_user_short_password(server):
    # Test POST /users with a short password
    user_data = {'name': 'John Doe', 'email': 'john@example.com', 'password': '123'}
    response = send_request('POST', '/users', data=user_data)
    assert response.status_code == 400
    assert response.json() == {'error': 'Password must be at least 8 characters long'}