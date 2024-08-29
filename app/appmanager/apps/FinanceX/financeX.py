from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required
from .edit import create_dash_app

# Define the blueprint
FinanceX = Blueprint('FinanceX', __name__, template_folder='templates')
appedit=create_dash_app(FinanceX)

# Route for the first page
@FinanceX.route('/financeX/overview')
@login_required
def overview():
    return render_template('financeX/page1.html')

# Route for the second page
@FinanceX.route('/financeX//edit')
@login_required
def page2():
    
    return appedit.index()

# Route for the second page
@FinanceX.route('/financeX/')
@login_required
def home():
    return render_template('financeX/page1.html')

