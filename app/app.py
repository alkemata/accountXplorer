from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
import config
import dash
#import dash_html_components as html
#import dash_core_components as dcc

app=dash.Dash(__name__, server=server, suppress_callback_exceptions=True)
#app = Flask(__name__)
app.config.from_object(config.Config)

""" from overview import create_dash_app
overview = create_dash_app(app)
from edit import create_dash_app
edit = create_dash_app(app) """

db.init_app(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

@app.route('/')
@login_required
def home():
    return f'Hello, {current_user.username}!'


""" @app.route('/overview')
@login_required
def render_app1():
    return overview.index()

@app.route('/edit')
@login_required
def render_app2():
    return edit.index() """

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Dynamic routing for apps
@app.server.route('/<app_name>')
@login_required
def render_app(app_name):
    if app_name in current_user.permissions:
        app_module = __import__(f'apps.{app_name}.app', fromlist=['app'])
        return app_module.app.index()
    return 'Unauthorized', 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)
