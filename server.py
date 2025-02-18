from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import re

# In-memory data storage
users = []

class SimpleAPIHandler(BaseHTTPRequestHandler):
    # helper method to validate password
    def _validate_password(self, password):
        return len(password) >= 8

    # helper method to validate email
    def _validate_email(self, email):
        regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(regex, email) is not None
    
    # Helper method to send responses
    def _send_response(self, status_code, data=None, content_type='application/json'):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()
        if data is not None:  # Explicitly check for None
            if not isinstance(data, str):
                data = json.dumps(data)  # Convert list/dict to JSON string
            self.wfile.write(data.encode('utf-8'))

    # Handle GET requests
    def do_GET(self):
        path = self.path.rstrip('/')  # Normalize path
        if path == '/users':
            self._send_response(200, users)  # Send the users list (even if empty)
        else:
            self._send_response(404, {'error': 'Not Found'})

    # Handle POST requests
    def do_POST(self):
        print(f"POST request received for path: {self.path}")  # Debug print
        if self.path == '/users':
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
        else:
            self._send_response(404, {'error': 'Not Found'})

# Run the server
def run(server_class=HTTPServer, handler_class=SimpleAPIHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()