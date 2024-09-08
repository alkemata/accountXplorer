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
ressources_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'resources')


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



# ============= display categories

pivot_table=pd.read_csv(os.path.join(ressources_dir,'pivot.csv'))

categories_layout= html.Div([
            dbc.Row([
                dbc.Col(html.H2('Spending by category'), width=12),
                dbc.Col(
                    dash_table.DataTable(
                        id='pivot-table',
                        columns=[{"name": str(i), "id": str(i)} for i in pivot_table.reset_index().columns],
                        data=pivot_table.to_dict('records'),
                        style_table={'overflowX': 'auto', 'height': '300px', 'overflowY': 'auto'},
                        style_data_conditional=[
                            {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}
                        ],
                        style_cell={
                            'textAlign': 'left',
                            'padding': '2px',
                            'fontSize': '12px',
                            'height': 'auto',
                            'whiteSpace': 'normal'
                        },
                        style_header={
                            'backgroundColor': 'lightgrey',
                            'fontWeight': 'bold',
                            'fontSize': '12px',
                            'padding': '2px'
                        },
                        style_data={
                            'padding': '2px',
                            'fontSize': '12px',
                            'height': 'auto',
                            'whiteSpace': 'normal'
                        },
                        cell_selectable=True
                    ), width=12
                )
            ], className="mb-4"),
             dbc.Row([
                html.Hr(style={'border': '1px solid black'}),
                dbc.Col(html.H2('List of transactions for a category'), width=12),
                dbc.Col(
                    dash_table.DataTable(
                        id='detail-table',
                  #      columns=[{"name": col, "id": col} for col in df.drop(columns=['Month']).columns],
                        style_table={'overflowX': 'auto', 'height': '300px', 'overflowY': 'auto'},
                        style_cell={
                            'textAlign': 'left',
                            'padding': '2px',
                            'fontSize': '12px',
                            'height': 'auto',
                            'whiteSpace': 'normal'
                        },
                        style_header={
                            'backgroundColor': 'lightgrey',
                            'fontWeight': 'bold',
                            'fontSize': '12px',
                            'padding': '2px'
                        },
                        style_data={
                            'padding': '2px',
                            'fontSize': '12px',
                            'height': 'auto',
                            'whiteSpace': 'normal'
                        },
                        row_selectable='multi'
                    ), width=12
                )
            ], className="mb-4"),

            ])

    @app.callback(
        Output('detail-table', 'data'),
        [Input('pivot-table', 'active_cell'),
        Input('pivot-table','data')
        ]
    )
    def display_details(active_cell,pivot):
        if active_cell:
            row = active_cell['row']
            col = active_cell['column_id']
            pivot_table=pd.DataFrame(pivot).reset_index()
            category = pivot_table.iloc[row]['Kategorie']
            month=col
            #month = pd.Period(col, freq='M')  # Convert string back to Period
            # Filter the dataframe based on the selected category and month
            filtered_df = df[(df['Kategorie'] == category) & (df['Month'] == int(month))]
            filtered_df = filtered_df.drop(columns=['Month'])
             #filtered_df['Buchungsdatum'] = filtered_df['Buchungsdatum'].astype(str)
            return filtered_df.to_dict('records')
        return no_update

    def layout_main():
        layout=html.Div(
        style={'display': 'flex', 'flex-direction': 'column', 'padding': '10px'},  # Makes layout responsive
        children=[spending_layout,categories_layout])
        return layout

    appyear.layout=layout_main()
    return appyear





