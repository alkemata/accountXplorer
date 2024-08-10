from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required

# Define the blueprint
financeX = Blueprint('financeX', __name__, template_folder='templates')

# Route for the first page
@financeX.route('/overview')
@login_required
def page1():
    return render_template('financeX/page1.html')

# Route for the second page
@financeX.route('/edit')
@login_required
def page2():
    return render_template('financeX/page2.html')

# Route for the second page
@financeX.route('/')
@login_required
def home():
    return render_template('financeX/home.html')
