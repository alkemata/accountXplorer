import pandas as pd
import logging
import os
import callbacks
import ui
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc, html, dash_table
tate
from FinanceX import functions as functions

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

app = Dash(__name__, server=server, url_base_pathname='/edit/', external_stylesheets=[dbc.themes.BOOTSTRAP])
logger.info('logger 2 activated')
app.layout=html.Div([dcc.Store(id='shared-dataframe'), ui.layout_files()])
 

    #recurrent_expenses = df.groupby('Verwendungszweck').filter(lambda x: len(x) > 1).drop(columns=['Month', 'IBAN', 'Umbuchung', 'Buchungstext'])
    #recurrent_expenses = recurrent_expenses.sort_values(by='Verwendungszweck')
    #recurrent_expenses_table = dbc.Table.from_dataframe(recurrent_expenses, striped=True, bordered=True, hover=True)