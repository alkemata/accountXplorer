from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import Config
from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from FinanceX import financeX

app = Flask(__name__)
app.config.from_object(Config)



login_manager = LoginManager(app)
bcrypt = Bcrypt(app)

login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

app.register_blueprint(financeX)


from models import User, App
from init_db import sync_apps_directory



if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,debug=True)
