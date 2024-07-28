import dash
import pandas as pd
from dash import html
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State

def create_dash_app(server):
    app = dash.Dash(__name__, server=server, url_base_pathname='/app1/')
    df = df.drop(columns=['Wertstellungsdatum', 'BIC', 'Notiz','Schlagworte','Steuerkategorie','Parentkategorie','Splitbuchung','Abweichenderempfaenger'])
    accounts=ddf['Konto'].unique()

    style_data_conditional = [
        {
            'if': {'filter_query': '{Betrag} > 0'},
            'backgroundColor': 'green',
            'color': 'white'
        }
    ]

    app.layout = html.Div([

    dash_table.DataTable(
        id='table',
        columns=[{'name': col, 'id': col} for col in df.columns],
        data=df.to_dict('records'),
        style_data_conditional=style_data_conditional,
        style_table={'height': '400px', 'overflowY': 'auto'},  # Make the table scrollable
        style_cell={'minWidth': '150px', 'width': '150px', 'maxWidth': '150px'},  # Set column widths
        fixed_rows={'headers': True},
    ),
    html.Div(id='output-box', children=', '.join(map(str, distinct_values)), style={'border': '1px solid black', 'padding': '10px', 'margin-top': '10px'})

    ])

   
    return app
 
