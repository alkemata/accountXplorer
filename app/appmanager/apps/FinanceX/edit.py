import pandas as pd
import logging
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from FinanceX.callbacks import edit_callbacks
from FinanceX.ui import edit_ui
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc, html, dash_table
from FinanceX import functions as functions
import dash

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
appedit= None

def create_dash_app(flask_server):
    global appedit
    appedit = dash.Dash(__name__,  server=flask_server,url_base_pathname='/edit/', external_stylesheets=[dbc.themes.BOOTSTRAP])
    logger.info('logger 2 activated')
    apeditp.layout=html.Div([dcc.Store(id='shared-dataframe'), edit_ui.layout_files()])
    appedit.run_server(debug=True)

    #recurrent_expenses = df.groupby('Verwendungszweck').filter(lambda x: len(x) > 1).drop(columns=['Month', 'IBAN', 'Umbuchung', 'Buchungstext'])
    #recurrent_expenses = recurrent_expenses.sort_values(by='Verwendungszweck')
    #recurrent_expenses_table = dbc.Table.from_dataframe(recurrent_expenses, striped=True, bordered=True, hover=True)