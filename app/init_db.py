import db
from models import User, App
import os


def create_user(user1, email, password)
    user1 = User(username=user1, email=email)
    user1.set_password(password)

    # Commit to the database
    db.session.add(user1)
    db.session.commit()

# List all users and their authorized apps
def list_users():
    users = User.query.all()
    for user in users:
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print("Authorized Apps:")
        for app in user.authorized_apps:
            print(f"- {app.name} ({app.path})")
        print("\n")

def modify_user(username, app_name)
    # Fetch user and app
    user = User.query.filter_by(username=username).first()
    app = App.query.filter_by(name=app_name).first()

    # Add app to user
    user.authorized_apps.append(app)
    db.session.commit()

    print(f"Added {app.name} to {user.username}")


APPS_DIRECTORY = './apps'

def sync_apps_directory():
    # Get the list of apps in the directory
    current_apps = {filename for filename in os.listdir(APPS_DIRECTORY) if filename.endswith('.py')}

    # Fetch all apps from the database
    db_apps = {app.name: app for app in App.query.all()}

    # Add new apps to the database
    for app_filename in current_apps:
        if app_filename not in db_apps:
            new_app = App(name=app_filename, path=os.path.join(APPS_DIRECTORY, app_filename))
            db.session.add(new_app)
            print(f"Added new app to database: {app_filename}")

    # Remove apps from the database that are no longer in the directory
    for app_name, app in db_apps.items():
        if app_name not in current_apps:
            db.session.delete(app)
            print(f"Removed app from database: {app_name}")

    # Commit the changes to the database
    db.session.commit()

if __name__ == '__main__':
    sync_apps_directory()
