from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from ./config import Config
from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required


app = Flask(__name__)
app.config.from_object(Config)



login_manager = LoginManager(app)
bcrypt = Bcrypt(app)

login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


from models import User, App
from init_db import sync_apps_directory



if __name__ == '__main__':
    app.run(debug=True)
