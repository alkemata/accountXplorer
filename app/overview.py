import dash
import dash_html_components as html
import dash_core_components as dcc
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State

def create_dash_app(server):
    app = dash.Dash(__name__, server=server, url_base_pathname='/app1/')
    df = pd.read_csv('./ressources/dataliste.csv')

    app.layout = html.Div([

    dash_table.DataTable(
        id='table',
        columns=[{'name': col, 'id': col} for col in df.columns],
        data=[df.to_dict('records')],
        style_data_conditional=[],
        style_table={'overflowX': 'auto'}
    )
    ])

   
    return app
 
