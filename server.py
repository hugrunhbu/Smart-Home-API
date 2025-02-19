from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import re

# In-memory data storage
users = []
houses = []
rooms = []
devices = []

class SimpleAPIHandler(BaseHTTPRequestHandler):
    # Helper method to send responses
    def _send_response(self, status_code, data=None, content_type='application/json'):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()
        if data is not None:  # Explicitly check for None
            if not isinstance(data, str):
                data = json.dumps(data)  # Convert list/dict to JSON string
            self.wfile.write(data.encode('utf-8'))

    # helper method to validate password
    def _validate_password(self, password):
        return len(password) >= 8

    # helper method to validate email
    def _validate_email(self, email):
        regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(regex, email) is not None

    # Handle GET requests (returns the lists of users/houses etc)
    def do_GET(self):
        path = self.path.rstrip('/')  # Normalize path
        if path == '/users':
            self._send_response(200, users)  # Send the users list (even if empty)
        elif path == '/houses':
            self._send_response(200, houses)
        elif path == '/rooms':
            self._send_response(200, rooms)
        elif path == '/devices':
            self._send_response(200, devices)
        else:
            self._send_response(404, {'error': 'Not Found'})

    # Handle POST requests
    def do_POST(self):
        print(f"POST request received for path: {self.path}")  # Debug print
        if self.path == '/users':
            self._handle_create_user()
        elif self.path == '/houses':
            self._handle_create_house()
        elif self.path == '/rooms':
            self._handle_create_room()
        elif self.path == '/devices':
            self._handle_create_device()
        else:
            self._send_response(404, {'error': 'Not Found'})
    
    # Handle DELETE requests
        # Handle DELETE requests
    def do_DELETE(self):
        path = self.path.rstrip('/')  # Normalize path
        
        if path.startswith('/users/'):
            user_id = int(path.split('/')[-1])
            user_to_delete = next((user for user in users if user['id'] == user_id), None)
            if user_to_delete:
                users.remove(user_to_delete)
                self._send_response(204)  # No Content
            else:
                self._send_response(404, {'error': 'User not found'})

        elif path.startswith('/houses/'):
            house_id = int(path.split('/')[-1])
            house_to_delete = next((house for house in houses if house['id'] == house_id), None)
            if house_to_delete:
                houses.remove(house_to_delete)
                self._send_response(204)  # No Content
            else:
                self._send_response(404, {'error': 'House not found'})

        elif path.startswith('/rooms/'):
            room_id = int(path.split('/')[-1])
            room_to_delete = next((room for room in rooms if room['id'] == room_id), None)
            if room_to_delete:
                rooms.remove(room_to_delete)
                self._send_response(204)  # No Content
            else:
                self._send_response(404, {'error': 'Room not found'})

        elif path.startswith('/devices/'):
            device_id = int(path.split('/')[-1])
            device_to_delete = next((device for device in devices if device['id'] == device_id), None)
            if device_to_delete:
                devices.remove(device_to_delete)
                self._send_response(204)  # No Content
            else:
                self._send_response(404, {'error': 'Device not found'})

        else:
            self._send_response(404, {'error': 'Not Found'})


       # Handle PUT requests (updates)
    def do_PUT(self):
        path = self.path.rstrip('/')  # Normalize path

        if path.startswith('/users/'):
            user_id = int(path.split('/')[-1])
            user_to_update = next((user for user in users if user['id'] == user_id), None)
            if user_to_update:
                content_length = int(self.headers['Content-Length'])
                put_data = self.rfile.read(content_length)
                try:
                    data = json.loads(put_data)
                    # Update user fields
                    if 'name' in data:
                        user_to_update['name'] = data['name']
                    if 'email' in data:
                        if not self._validate_email(data['email']):
                            self._send_response(400, {'error': 'Invalid email format'})
                            return
                        user_to_update['email'] = data['email']
                    if 'password' in data:
                        if not self._validate_password(data['password']):
                            self._send_response(400, {'error': 'Password must be at least 8 characters long'})
                            return
                        user_to_update['password'] = data['password']
                    self._send_response(200, user_to_update)
                except json.JSONDecodeError:
                    self._send_response(400, {'error': 'Invalid JSON'})
            else:
                self._send_response(404, {'error': 'User not found'})

        elif path.startswith('/houses/'):
            house_id = int(path.split('/')[-1])
            house_to_update = next((house for house in houses if house['id'] == house_id), None)
            if house_to_update:
                content_length = int(self.headers['Content-Length'])
                put_data = self.rfile.read(content_length)
                try:
                    data = json.loads(put_data)
                    # Update house fields
                    if 'name' in data:
                        house_to_update['name'] = data['name']
                    if 'address' in data:
                        house_to_update['address'] = data['address']
                    self._send_response(200, house_to_update)
                except json.JSONDecodeError:
                    self._send_response(400, {'error': 'Invalid JSON'})
            else:
                self._send_response(404, {'error': 'House not found'})

        elif path.startswith('/rooms/'):
            room_id = int(path.split('/')[-1])
            room_to_update = next((room for room in rooms if room['id'] == room_id), None)
            if room_to_update:
                content_length = int(self.headers['Content-Length'])
                put_data = self.rfile.read(content_length)
                try:
                    data = json.loads(put_data)
                    # Update room fields
                    if 'name' in data:
                        room_to_update['name'] = data['name']
                    if 'houseId' in data:
                        room_to_update['houseId'] = data['houseId']
                    self._send_response(200, room_to_update)
                except json.JSONDecodeError:
                    self._send_response(400, {'error': 'Invalid JSON'})
            else:
                self._send_response(404, {'error': 'Room not found'})

        elif path.startswith('/devices/'):
            device_id = int(path.split('/')[-1])
            device_to_update = next((device for device in devices if device['id'] == device_id), None)
            if device_to_update:
                content_length = int(self.headers['Content-Length'])
                put_data = self.rfile.read(content_length)
                try:
                    data = json.loads(put_data)
                    # Update device fields
                    if 'name' in data:
                        device_to_update['name'] = data['name']
                    if 'type' in data:
                        device_to_update['type'] = data['type']
                    if 'roomId' in data:
                        device_to_update['roomId'] = data['roomId']
                    self._send_response(200, device_to_update)
                except json.JSONDecodeError:
                    self._send_response(400, {'error': 'Invalid JSON'})
            else:
                self._send_response(404, {'error': 'Device not found'})

        else:
            self._send_response(404, {'error': 'Not Found'})


    def _handle_create_user(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print(f"Raw POST data: {post_data}")  # Debug print
        try:
            data = json.loads(post_data)
            print(f"Parsed JSON data: {data}")  # Debug print
            # Validate input
            if not all(key in data for key in ['name', 'email', 'password']):
                self._send_response(400, {'error': 'Missing required fields'})
                return
            # validate email format
            if not self._validate_email(data['email']):
                self._send_response(400, {'error': 'Invalid email format'})
                return
            # validate password length
            if not self._validate_password(data['password']):
                self._send_response(400, {'error': 'Password must be at least 8 characters long'})
                return
            # Simulate adding a user
            user = {
                'id': len(users) + 1,
                'name': data['name'],
                'email': data['email'],
                'password': data['password']
            }
            users.append(user)
            self._send_response(201, user)
        except json.JSONDecodeError:
            print("Invalid JSON received")  # Debug print
            self._send_response(400, {'error': 'Invalid JSON'})

    def _handle_create_house(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data)
            # Validate input
            if not all(key in data for key in ['name', 'address']):
                self._send_response(400, {'error': 'Missing required fields'})
                return
            # Simulate adding a house
            house = {
                'id': len(houses) + 1,
                'name': data['name'],
                'address': data['address']
            }
            houses.append(house)
            self._send_response(201, house)
        except json.JSONDecodeError:
            self._send_response(400, {'error': 'Invalid JSON'})

    def _handle_create_room(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data)
            # Validate input
            if not all(key in data for key in ['name', 'houseId']):
                self._send_response(400, {'error': 'Missing required fields'})
                return
            # Check if house exists
            if not any(house['id'] == data['houseId'] for house in houses):
                self._send_response(404, {'error': 'House not found'})
                return
            # Simulate adding a room
            room = {
                'id': len(rooms) + 1,
                'name': data['name'],
                'houseId': data['houseId']
            }
            rooms.append(room)
            self._send_response(201, room)
        except json.JSONDecodeError:
            self._send_response(400, {'error': 'Invalid JSON'})

    def _handle_create_device(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data)
            # Validate input
            if not all(key in data for key in ['name', 'type', 'roomId']):
                self._send_response(400, {'error': 'Missing required fields'})
                return
            # Check if room exists
            if not any(room['id'] == data['roomId'] for room in rooms):
                self._send_response(404, {'error': 'Room not found'})
                return
            # Simulate adding a device
            device = {
                'id': len(devices) + 1,
                'name': data['name'],
                'type': data['type'],
                'roomId': data['roomId']
            }
            devices.append(device)
            self._send_response(201, device)
        except json.JSONDecodeError:
            self._send_response(400, {'error': 'Invalid JSON'})

# Run the server
def run(server_class=HTTPServer, handler_class=SimpleAPIHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()