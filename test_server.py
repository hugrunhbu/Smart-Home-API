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
    elif method == 'DELETE':
        response = requests.delete(url, headers=headers)
    elif method == 'PUT':
        response = requests.put(url, headers=headers, json=data)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")
    
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

    # Test DELETE user
def test_delete_user(server):
    response = send_request('DELETE', '/users/1')
    assert response.status_code == 204  # No Content

    # Verify the user is deleted
    response = send_request('GET', '/users')
    assert response.status_code == 200
    assert response.json() == []

# Test DELETE house
def test_delete_house(server):
    response = send_request('DELETE', '/houses/1')
    assert response.status_code == 204  # No Content

    # Verify the house is deleted
    response = send_request('GET', '/houses')
    assert response.status_code == 200
    assert response.json() == []

# # Test DELETE room
# def test_delete_room(server):
#     # Ensure a house exists first
#     house_data = {'name': 'My House', 'address': '123 Main St'}
#     send_request('POST', '/houses', data=house_data)

#     # Create a room
#     room_data = {'name': 'Living Room', 'houseId': 1}
#     send_request('POST', '/rooms', data=room_data)

#     # Fetch all rooms to verify the assigned ID
#     response = send_request('GET', '/rooms')
#     assert response.status_code == 200
#     rooms = response.json()
#     assert len(rooms) > 0  # Ensure a room was created

#     room_id = rooms[0]['id']  # Get the actual ID assigned

#     # Now delete the room
#     response = send_request('DELETE', f'/rooms/{room_id}')
#     assert response.status_code == 204  # No Content

#     # Verify the room is deleted
#     response = send_request('GET', '/rooms')
#     assert response.status_code == 200
#     assert response.json() == []


# Test PUT (UPDATE) user
def test_update_user(server):
    # Create a user first
    user_data = {'name': 'John Doe', 'email': 'john@example.com', 'password': 'password123'}
    send_request('POST', '/users', data=user_data)

    # Update the user
    updated_data = {'name': 'John Updated', 'email': 'john.updated@example.com', 'password': 'newpassword123'}
    response = send_request('PUT', '/users/1', data=updated_data)

    assert response.status_code == 200
    assert response.json() == {'id': 1, **updated_data}

# Test PUT (UPDATE) house
def test_update_house(server):
    # Create a house first
    house_data = {'name': 'My House', 'address': '123 Main St'}
    send_request('POST', '/houses', data=house_data)

    # Update the house
    updated_data = {'name': 'Updated House', 'address': '456 New St'}
    response = send_request('PUT', '/houses/1', data=updated_data)

    assert response.status_code == 200
    assert response.json() == {'id': 1, **updated_data}

# # Test PUT (UPDATE) room
# def test_update_room(server):
#     # Ensure a house exists first
#     house_data = {'name': 'My House', 'address': '123 Main St'}
#     send_request('POST', '/houses', data=house_data)

#     # Create a room before trying to update it
#     room_data = {'name': 'Living Room', 'houseId': 1}
#     send_request('POST', '/rooms', data=room_data)

#     # Update the room
#     updated_data = {'name': 'Updated Room'}
#     response = send_request('PUT', '/rooms/1', data=updated_data)
    
#     assert response.status_code == 200
#     assert response.json() == {'id': 1, 'houseId': 1, **updated_data}

# # test to delete device
# def test_delete_device(server):
#     # Ensure a house and room exist first
#     house_data = {'name': 'My House', 'address': '123 Main St'}
#     send_request('POST', '/houses', data=house_data)

#     room_data = {'name': 'Living Room', 'houseId': 1}
#     send_request('POST', '/rooms', data=room_data)

#     # Create a device before trying to delete it
#     device_data = {'name': 'Smart Light', 'type': 'light', 'roomId': 1}
#     send_request('POST', '/devices', data=device_data)

#     # Now delete the device
#     response = send_request('DELETE', '/devices/1')
#     assert response.status_code == 204  # No Content

#     # Verify the device is deleted
#     response = send_request('GET', '/devices')
#     assert response.status_code == 200
#     assert response.json() == []

# # test to update device
# def test_update_device(server):
#     # Ensure a house and room exist first
#     house_data = {'name': 'My House', 'address': '123 Main St'}
#     send_request('POST', '/houses', data=house_data)

#     room_data = {'name': 'Living Room', 'houseId': 1}
#     send_request('POST', '/rooms', data=room_data)

#     # Create a device before trying to update it
#     device_data = {'name': 'Smart Light', 'type': 'light', 'roomId': 1}
#     send_request('POST', '/devices', data=device_data)

#     # Update the device
#     updated_data = {'name': 'Updated Light', 'type': 'LED'}
#     response = send_request('PUT', '/devices/1', data=updated_data)

#     assert response.status_code == 200
#     assert response.json() == {'id': 1, 'roomId': 1, **updated_data}
