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

    # Step 1: Group by 'Month number' and sum the 'Betrag' for each month
    df2=df[df['Konto']!='4907********4225']
    monthly_spending = df2[(df2['Betrag']<0)].groupby('Month')['Betrag'].sum().reset_index() #remove visa - different approach
    monthly_earning = df2[(df2['Betrag']>0)].groupby('Month')['Betrag'].sum().reset_index()

    # Step 2: Calculate the cumulative spending
    #monthly_spending['Cumulative Spending'] = monthly_spending['Betrag'].cumsum()
    monthly_spending['Spending']=-monthly_spending['Betrag']
    monthly_earning['Earning']=(monthly_earning['Betrag']+monthly_spending['Betrag'])

    # Step 3: Create a bar chart with plotly
    fig = go.Figure(data=[
        go.Bar(x=monthly_spending['Month'], y=monthly_spending['Spending'], marker_color='red')
    ])
    fig2 = go.Figure(data=[
        go.Bar(x=monthly_earning['Month'], y=monthly_earning['Earning'], marker_color='green')
    ])


    # Add titles and labels
    fig.update_layout(
        title='Monthly Spending',
        xaxis_title='Month Number',
        yaxis_title='Spending'
    )
        # Add titles and labels
    fig2.update_layout(
        title='Monthly Excedent',
        xaxis_title='Month Number',
        yaxis_title='Excedent'
    )

    spending_layout = html.Div(children=[
    html.H1(children='Year overview'),
    
    dcc.Graph(
        id='cumulative-spending-bar-chart',
        figure=fig
    ),
        dcc.Graph(
        id='cumulative-earning-bar-chart',
        figure=fig2
    ),
    ])





    def layout_main():
        layout=html.Div(
        style={'display': 'flex', 'flex-direction': 'column', 'padding': '10px'},  # Makes layout responsive
        children=[spending_layout])
        return layout

    appyear.layout=layout_main()
    return appyear





