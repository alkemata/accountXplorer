# app/routes.py
from flask import Blueprint, render_template, session, redirect
from flask_login import login_required
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


main_blueprint = Blueprint('main', __name__)

@main_blueprint.route('/')
@login_required
def index():
    return render_template('home.html')

@main_blueprint.route('/users')
@admin_required
def list_users():
    users = User.query.all()
    return render_template('list_users.html', users=users)

@main_blueprint.route('/user/new', methods=['GET', 'POST'])
@admin_required
def create_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        app_ids = request.form.getlist('apps')
        apps = App.query.filter(App.id.in_(app_ids)).all()

        new_user = User(name=name, email=email, password=password, authorized_apps=apps)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('list_users'))

    apps = App.query.all()
    return render_template('create_user.html', apps=apps)

@main_blueprint.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.password = request.form['password']
        app_ids = request.form.getlist('apps')
        user.authorized_apps = App.query.filter(App.id.in_(app_ids)).all()

        db.session.commit()
        return redirect(url_for('list_users'))

    apps = App.query.all()
    return render_template('edit_user.html', user=user, apps=apps)

@main_blueprint.route('/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('list_users'))

@main_blueprint.route('/management')
@admin_required
def management_dashboard():
    return render_template('management_dashboard.html')  