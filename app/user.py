# user.py
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# In-memory user store
users = {
    1: User(1, "testuser", "password")
}

def get_user_by_username(username):
    for user in users.values():
        if user.username == username:
            return user
    return None
