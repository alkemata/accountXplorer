import pandas as pd
import logging
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc, html, dash_table
from FinanceX import functions as functions
import dash
from datetime import datetime, timedelta
import calendar
import plotly.graph_objs as go
import numpy as np 
from dash.dependencies import Input, Output
from datetime import datetime, timedelta
import plotly.express as px

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def create_dash_app(flask_server):
    appedit= dash.Dash(__name__,  server=flask_server,url_base_pathname='/edit/', external_stylesheets=[dbc.themes.BOOTSTRAP])
    df=functions.load_data('processed.csv')
    
    style_data_conditional = [
        {
            'if': {'filter_query': '{Betrag} > 0'},
            'backgroundColor': 'green',
            'color': 'white'
        },
        {
            'if': {'filter_query': '{Kategorie} = Umbuchung'},
            'backgroundColor': 'blue',
            'color': 'white'
        }
    ]

    layout_list_global= html.Div(
        children=[
            html.H1("Yearly view"),
            dcc.Input(id='filter-input', type='text', placeholder='Enter Notiz for the selection'),
            html.Button('ADD', id='filter-button', n_clicks=0),

                       
                dash_table.DataTable(
                    id=f'table-global',
                    columns=[{"name": i, "id": i} for i in df.columns],
                    data=df.to_dict('records'),
                    style_data_conditional=style_data_conditional,
                    style_table={'height': '400px', 'overflowY': 'auto'},  # Make the table scrollable
                style_cell={'minWidth': '150px', 'width': '150px', 'maxWidth': '150px','overflow': 'hidden','textOverflow': 'ellipsis'},  # Set column widths
                fixed_rows={'headers': True},
                filter_action='native',
                ),
                html.Button('SAVE', id='save-global-button', n_clicks=0),
                ])

    def layout_main():
        layout=html.Div(
        style={'display': 'flex', 'flex-direction': 'column', 'padding': '10px'},  # Makes layout responsive
        children=[layout_list_global])
        return layout

    appedit.layout=layout_main()
    return appedit