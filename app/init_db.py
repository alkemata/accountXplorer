
from appmanager import create_app
from appmanager.models import db, User, App
import os
from appmanager import create_app
from pathlib import Path


app=create_app()

def create_user(user1, email, password,is_admin=False):
    with app.app_context():
        user1 = User(username=user1, email=email,is_admin=is_admin)
        user1.set_password(password)

        # Commit to the database
        db.session.add(user1)
        db.session.commit()

# List all users and their authorized apps
def list_users():
    with app.app_context():
        users = User.query.all()
        for user in users:
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Admin: {user.is_admin}")
            print("Authorized Apps:")
            for app1 in user.authorized_apps:
                print(f"- {app1.name} ({app1.path})")
            print("\n")

def make_admin(username):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user:
            user.is_admin = True
            db.session.commit()
            print(f"{username} is now an admin.")
        else:
            print(f"User {username} not found.")

def modify_user(username, app_name):
    with app.app_context():
        # Fetch user and app
        user = User.query.filter_by(username=username).first()
        app1 = App.query.filter_by(name=app_name).first()

        # Add app to user
        user.authorized_apps.append(app1)
        db.session.commit()

        print(f"Added {app.name} to {user.username}")


def list_apps():
    with app.app_context():
        apps = App.query.all()

        if not apps:
            print("No apps found in the database.")
        else:
            print("Listing all apps in the database:")
            for app1 in apps:
                print("App Name: {}".format(app1.name))
                print("App Path: {}".format(app1.path))
                print("-" * 30)

APPS_DIRECTORY = './apps'

def sync_apps_directory():
    with app.app_context():
        current_apps = {}

        # Walk through all subdirectories of APPS_DIRECTORY
        current_apps = [f.name for f in Path('apps').iterdir() if f.is_dir()]

        # Fetch all apps from the database
        db_apps = {app.name: app1 for app1 in App.query.all()}

        # Add new apps to the database
        for app_name in current_apps.items():
            if app_name not in db_apps:
                new_app = App(name=app_name)
                db.session.add(new_app)
                print(f"Added new app to database: {app_name}")

        # Remove apps from the database that are no longer in the directory
        for app_name, app1 in db_apps.items():
            if app1.name not in current_apps:
                db.session.delete(app1)
                print(f"Removed app from database: {app_name}")

        # Commit the changes to the database
        db.session.commit()

if __name__ == '__main__':
    sync_apps_directory()

def create_db():
    with app.app_context():
       db.create_all()

