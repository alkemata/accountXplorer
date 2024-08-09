from werkzeug.security import generate_password_hash
from app import app, db
from sqlalchemy.orm import Session
from models import User, Permission
from database import SessionLocal

#add_user("john_doe", "password123", permissions=["app1", "app2"])
#list_users()
#modify_user("john_doe", new_password="newpassword123", new_permissions=["app1", "app3"])
#delete_user("john_doe")

def init_db():
    with app.app_context():
        try: 
            db.create_all()  # Create tables
            # Check if the initial user exists
            if not User.query.filter_by(username=app.config['INITIAL_USERNAME']).first():
                # Add initial user
                hashed_password = generate_password_hash(app.config['INITIAL_PASSWORD'], method='sha256')
                new_user = User(username=app.config['INITIAL_USERNAME'], password=hashed_password)
                db.session.add(new_user)
                db.session.commit()
                print("Initialized the database and added the initial user.")
        except Exception as e:
            logger.error("Error initializing the database: %s", e)
            raise

def add_user(username, password, permissions=None):
    """Add a new user with the specified permissions."""
    session = SessionLocal()
    if session.query(User).filter(User.username == username).first():
        raise ValueError("User already exists.")
    hashed_password = generate_password_hash(password)
    user = User(username=username, password=hashed_password)
    session.add(user)
    session.commit()
    
    if permissions:
        for app_name in permissions:
            permission = Permission(user_id=user.id, app_name=app_name)
            session.add(permission)
    
    session.commit()
    session.close()
    print(f"User '{username}' added successfully.")

def list_users():
    """List all users with their associated permissions."""
    session = SessionLocal()
    users = session.query(User).all()
    for user in users:
        permissions = [perm.app_name for perm in user.permissions]
        print(f"User: {user.username}, Permissions: {permissions}")
    session.close()

def modify_user(username, new_password=None, new_permissions=None):
    """Modify the user's password and/or permissions."""
    session = SessionLocal()
    user = session.query(User).filter(User.username == username).first()
    if not user:
        raise ValueError("User not found.")
    
    if new_password:
        user.password = generate_password_hash(new_password)
    
    if new_permissions is not None:
        # Clear current permissions
        session.query(Permission).filter(Permission.user_id == user.id).delete()
        # Add new permissions
        for app_name in new_permissions:
            permission = Permission(user_id=user.id, app_name=app_name)
            session.add(permission)
    
    session.commit()
    session.close()
    print(f"User '{username}' modified successfully.")

def delete_user(username):
    """Delete a user and their associated permissions."""
    session = SessionLocal()
    user = session.query(User).filter(User.username == username).first()
    if not user:
        raise ValueError("User not found.")
    
    # Delete the user's permissions
    session.query(Permission).filter(Permission.user_id == user.id).delete()
    # Delete the user
    session.delete(user)
    session.commit()
    session.close()
    print(f"User '{username}' deleted successfully.")

if __name__ == '__main__':
    init_db()
