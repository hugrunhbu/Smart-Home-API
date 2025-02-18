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

# Test cases for House API
def test_create_house():
    # Test creating a house with valid data
    house_data = {'name': 'My House', 'address': '123 Main St'}
    response = send_request('POST', '/houses', data=house_data)
    assert response.status_code == 201
    assert response.json() == {
        'id': 1,
        'name': 'My House',
        'address': '123 Main St'
    }

def test_create_house_missing_fields():
    # Test creating a house with missing fields
    house_data = {'name': 'My House'}
    response = send_request('POST', '/houses', data=house_data)
    assert response.status_code == 400
    assert response.json() == {'error': 'Missing required fields'}

# Test cases for Room API
def test_create_room():
    # Test creating a room with valid data
    room_data = {'name': 'Living Room', 'houseId': 1}
    response = send_request('POST', '/rooms', data=room_data)
    assert response.status_code == 201
    assert response.json() == {
        'id': 1,
        'name': 'Living Room',
        'houseId': 1
    }

def test_create_room_missing_fields():
    # Test creating a room with missing fields
    room_data = {'name': 'Living Room'}
    response = send_request('POST', '/rooms', data=room_data)
    assert response.status_code == 400
    assert response.json() == {'error': 'Missing required fields'}

def test_create_room_invalid_house():
    # Test creating a room with an invalid houseId
    room_data = {'name': 'Living Room', 'houseId': 999}  # Non-existent houseId
    response = send_request('POST', '/rooms', data=room_data)
    assert response.status_code == 404
    assert response.json() == {'error': 'House not found'}

# Test cases for Device API
def test_create_device():
    # Test creating a device with valid data
    device_data = {'name': 'Smart Light', 'type': 'light', 'roomId': 1}
    response = send_request('POST', '/devices', data=device_data)
    assert response.status_code == 201
    assert response.json() == {
        'id': 1,
        'name': 'Smart Light',
        'type': 'light',
        'roomId': 1
    }

def test_create_device_missing_fields():
    # Test creating a device with missing fields
    device_data = {'name': 'Smart Light', 'type': 'light'}
    response = send_request('POST', '/devices', data=device_data)
    assert response.status_code == 400
    assert response.json() == {'error': 'Missing required fields'}

def test_create_device_invalid_room():
    # Test creating a device with an invalid roomId
    device_data = {'name': 'Smart Light', 'type': 'light', 'roomId': 999}  # Non-existent roomId
    response = send_request('POST', '/devices', data=device_data)
    assert response.status_code == 404
    assert response.json() == {'error': 'Room not found'}

# Test cases for GET endpoints
def test_get_users():
    # Test retrieving the list of users
    response = send_request('GET', '/users')
    assert response.status_code == 200
    assert response.json() == [{
        'id': 1,
        'name': 'John Doe',
        'email': 'john@example.com',
        'password': 'password123'
    }]

def test_get_houses():
    # Test retrieving the list of houses
    response = send_request('GET', '/houses')
    assert response.status_code == 200
    assert response.json() == [{
        'id': 1,
        'name': 'My House',
        'address': '123 Main St'
    }]

def test_get_rooms():
    # Test retrieving the list of rooms
    response = send_request('GET', '/rooms')
    assert response.status_code == 200
    assert response.json() == [{
        'id': 1,
        'name': 'Living Room',
        'houseId': 1
    }]

def test_get_devices():
    # Test retrieving the list of devices
    response = send_request('GET', '/devices')
    assert response.status_code == 200
    assert response.json() == [{
        'id': 1,
        'name': 'Smart Light',
        'type': 'light',
        'roomId': 1
    }]