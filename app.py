from http.server import BaseHTTPRequestHandler, HTTPServer
import json

# In-memory data storage
users = []

class SimpleAPIHandler(BaseHTTPRequestHandler):
    # helper method to send responses
    def _send_response(self, status_code, data=None):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        if data:
            self.wfile.write(json.dumps(data).encode('utf-8'))
    
    #handle GET requests
    def do_GET(self):
        if self.path == '/users':
            self._send_response(200, users)
        else:
            self._send_response(404, {'error': 'Not Found'})
    
    # handle POST requests
    def do_POST(self):
        if self.path == '/users':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                # validate input
                if not all(key in data for key in ['name', 'email', 'password']):
                    self._send_response(400, {'error': 'missing required fields'})
                    return
                # simulate adding a user
                user = {
                    'id': len(users) + 1,
                    'name': data['name'],
                    'email': data['email'],
                    'password': data['password']
                }
                users.append(user)
                self._send_response(201, user)
            except json.JSONDecodeError:
                self._send_response(400, {'error': 'Invalid JSON'})
            else:
                self._send_response(404, {'error': 'Not Found'})

# run the server
def run(server_class=HTTPServer, handler_class=SimpleAPIHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()