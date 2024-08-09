from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db
from models import User, App
from init_db import sync_apps_directory

print('routes loaded')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    # Sync the apps directory with the database before rendering
    sync_apps_directory()
    
    # Only show the apps that the user is authorized for and that still exist in the directory
    authorized_apps = [app for app in current_user.authorized_apps if os.path.exists(app.path)]
    
    return render_template('home.html', apps=authorized_apps)
