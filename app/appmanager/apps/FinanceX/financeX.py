from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required

# Define the blueprint
FinanceX = Blueprint('FinanceX', __name__, template_folder='templates')

# Route for the first page
@FinanceX.route('/overview')
@login_required
def overview():
    return render_template('financeX/page1.html')

# Route for the second page
@FinanceX.route('/edit')
@login_required
def page2():
    return render_template('financeX/page2.html')

# Route for the second page
@FinanceX.route('/')
@login_required
def home():
    return render_template('financeX/home.html')
