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
from dash.dependencies import Input, Output, State
from datetime import datetime, timedelta
import plotly.express as px

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


def create_dash_app(flask_server):
    global displayed_month
    appyear = dash.Dash(__name__,  server=flask_server,url_base_pathname='/year/', external_stylesheets=[dbc.themes.BOOTSTRAP])
    df=functions.load_data('processed.csv')
    last_update=df['Buchungsdatum'].max()
    year=df['Buchungsdatum'].dt.year.max()
    current_year=year
    current_month=df['Month'].max()
    displayed_month=current_month
    print(displayed_month)


    # Step 1: Group by 'Month number' and sum the 'Betrag' for each month
    monthly_spending = df[df['Betrag']>=0].groupby('Month')['Betrag'].sum().reset_index()

    # Step 2: Calculate the cumulative spending
    monthly_spending['Cumulative Spending'] = monthly_spending['Betrag'].cumsum()
    monthly_spending['Cumulative Spending']=-monthly_spending['Cumulative Spending']

    # Step 3: Create a bar chart with plotly
    fig = go.Figure(data=[
        go.Bar(x=monthly_spending['Month'], y=monthly_spending['Cumulative Spending'], marker_color='blue')
    ])

    # Add titles and labels
    fig.update_layout(
        title='Cumulative Monthly Spending',
        xaxis_title='Month Number',
        yaxis_title='Cumulative Spending'
    )

    spending_layout = html.Div(children=[
    html.H1(children='Monthly Spendings'),
    
    dcc.Graph(
        id='cumulative-spending-bar-chart',
        figure=fig
    )
    ])





    def layout_main():
        layout=html.Div(
        style={'display': 'flex', 'flex-direction': 'column', 'padding': '10px'},  # Makes layout responsive
        children=[spending_layout])
        return layout

    appyear.layout=layout_main()
    return appyear





