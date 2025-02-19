# Smart-Home-API

First push: Created a simple HTTP server using python's built-in http.server module. it handles GET and POST requests for a /users endpoint, allowing me to add a user (POST request) and retrieve all users (GET request).

# I added a requirements.txt file that has the dependencies

when you git clone this project type:
pip install -r requirements.txt
do this inside your virtual environment and all tests should pass.

# test_server.py

What the tests cover:

1. User API

- Creating a user with valid data.
- Creating a user with an invalid email.
- Creating a user with a short password.
- Creating a user with missing fields.

2. House API

- Creating a house with valid data.
- Creating a house with missing fields.

3. Room API

- Creating a room with valid data.
- Creating a room with missing fields.
- Creating a room with an invalid houseId.

4. Device API

- Creating a device with valid data.
- Creating a device with missing fields.
- Creating a device with an invalid roomId.

5. GET Endpoints

- Retrieving lists of users, houses, rooms, and devices.

(changing readme file to see whether actions is working)
