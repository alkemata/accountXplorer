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
                        html.P(f"Present Date: {datetime.now().strftime('%d-%m-%Y')}", className="card-text"),
                        html.P(f"Last Date in DataFrame: {last_update.strftime('%d-%m-%Y')}", className="card-text")
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
        prinnt(last_month_df)
        
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
            autosize=True
        )     
        return fig

    daily_sum, month_year = get_last_month_data(df)
    bar_chart_figure = create_bar_chart(daily_sum, month_year)
    last_month_data = get_last_month_data(df)[0]
    monthly_total = last_month_data['total_amount'].sum()


    current_spend_layout= html.Div(
            id='div2',
            children=[
                    dbc.Card(
                    dbc.CardBody([
                        html.H2(f"Total Amount Today: {monthly_total:.2f}", className="card-title", style={'font-size': '2em', 'text-align': 'center'}),
                    ]),
                    style={'margin-bottom': '10px', 'padding': '10px', 'border': '1px solid #ddd'}
                ),
                dcc.Graph(
                    id='bar-chart',
                    figure=bar_chart_figure
                ),
            html.Div(
            id='div3',
            children=[
                html.H3('List of Amounts for Selected Day'),
                dbc.Table(id='amounts-table', children=[], bordered=True, dark=True, hover=True, responsive=True, striped=True)
            ],
            style={'flex': '1', 'margin-bottom': '10px', 'padding': '10px', 'border': '1px solid #ddd'}
        )
            ],
            style={'flex': '1', 'margin-bottom': '10px', 'padding': '10px', 'border': '1px solid #ddd'}
        )   

    # Define callback to update the table based on the selected bar
    @appdash.callback(
        Output('amounts-table', 'children'),
        Input('bar-chart', 'clickData')
    )
    def update_table(clickData):
        if clickData is None:
            return []

        # Get the selected date from the bar chart
        selected_date = clickData['points'][0]['x']
        
        # Filter the DataFrame for the selected date
        print(df['Buchungsdatum'].dt.strftime('%Y-%m-%d'))
        selected_data = df[df['Buchungsdatum'].dt.strftime('%Y-%m-%d') == selected_date]
        

        table_body = [
            html.Tbody([
                html.Tr([html.Td(index), html.Td(amount)]) for index, amount in enumerate(selected_data['amount'], 1)
            ])
        ]
    
        return table_body

    def layout_main():
        layout=html.Div(
        style={'display': 'flex', 'flex-direction': 'column', 'padding': '10px'},  # Makes layout responsive
        children=[param_layout,current_spend_layout])
        return layout

    appdash.layout=layout_main()
    return appdash