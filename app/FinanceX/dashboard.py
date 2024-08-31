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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def create_dash_app(flask_server):
    appdash = dash.Dash(__name__,  server=flask_server,url_base_pathname='/home/', external_stylesheets=[dbc.themes.BOOTSTRAP])
    df=functions.load_data('processed.csv')
    last_update=df['Buchungsdatum'].max()


    param_layout=html.Div(
            id='div1',
            children=[
                dbc.Card(
                    dbc.CardBody([
                        html.H4("Date Information", className="card-title"),
                        html.P(f"Present Date: {datetime.now().strftime('%Y-%m-%d')}", className="card-text"),
                        html.P(f"Last Date in DataFrame: {last_update.strftime('%Y-%m-%d')}", className="card-text")
                    ]),
                style={'margin-bottom': '10px', 'padding': '10px', 'border': '1px solid #ddd'}
                )
            ]
        )

    def get_last_month_data(df):
        today = datetime.today()
        first_day_current_month = today.replace(day=1)
        last_day_last_month = first_day_current_month - timedelta(days=1)
        first_day_last_month = last_day_last_month.replace(day=1)
        
        # Filter DataFrame for last month
        mask = (df['Buchungsdatum'] >= first_day_last_month) & (df['Buchungsdatum'] <= last_day_last_month)
        last_month_df = df.loc[mask]
        
        # Group by day and sum amounts
        daily_sum = last_month_df.groupby(last_month_df['Buchungsdatum'].dt.day)['Betrag'].sum().reset_index()
        daily_sum.rename(columns={'Buchungsdatum': 'day', 'Betrag': 'total_amount'}, inplace=True)
        
        # To ensure all days are represented (even with zero amounts)
        days_in_last_month = calendar.monthrange(last_day_last_month.year, last_day_last_month.month)[1]
        all_days = pd.DataFrame({'day': range(1, days_in_last_month + 1)})
        daily_sum = pd.merge(all_days, daily_sum, on='day', how='left').fillna(0)
        
        return daily_sum, last_day_last_month.strftime('%B %Y')

    def create_bar_chart(daily_sum, month_year):
        fig = go.Figure(data=[
            go.Bar(
                x=daily_sum['day'],
                y=daily_sum['total_amount'],
                marker_color='indianred'
            )
        ])
        
        fig.update_layout(
            title=f'Sum of Amounts per Day for {month_year}',
            xaxis_title='Day of Month',
            yaxis_title='Total Amount',
            bargap=0.2,
            bargroupgap=0.1,
            responsive=True
        )     
        return fig

    daily_sum, month_year = get_last_month_data(df)
    bar_chart_figure = create_bar_chart(daily_sum, month_year)

    current_spend_layout= html.Div(
            id='div2',
            children=[
                dcc.Graph(
                    id='bar-chart',
                    figure=bar_chart_figure
                )
            ],
            style={'flex': '1', 'margin-bottom': '10px', 'padding': '10px', 'border': '1px solid #ddd'}
        )   

    def layout_main():
        layout=html.Div(
        style={'display': 'flex', 'flex-direction': 'column', 'padding': '10px'},  # Makes layout responsive
        children=[param_layout,current_spend_layout])
        return layout

    appdash.layout=layout_main()
    return appedit