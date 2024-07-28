import dash
import pandas as pd
from dash import html
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State

def create_dash_app(server):
    app = dash.Dash(__name__, server=server, url_base_pathname='/app1/')
    df = pd.read_csv('./ressources/dataliste.csv',sep=';')
    df['Betrag'] = pd.to_numeric(df['Betrag'].replace(',','.',regex=True), errors='coerce')
    df = df.drop(columns=['Wertstellungsdatum', 'BIC', 'Notiz','Schlagworte','SteuerKategorie','ParentKategorie','Splitbuchung','AbweichenderEmpfaenger'])
    accounts=df['Konto'].unique()
    dfs = {k: v for k, v in df.groupby('Konto')}

    style_data_conditional = [
        {
            'if': {'filter_query': '{Betrag} > 0'},
            'backgroundColor': 'green',
            'color': 'white'
        }
    ]


    app.layout = html.Div(
        children=[
            html.H1("DataFrames by 'konto' Value"),
            *[html.Div([
                html.H2(f"DataFrame for konto = {k}"),
                dash_table.DataTable(
                    id=f'table-{k}',
                    columns=[{"name": i, "id": i} for i in v.columns],
                    data=v.to_dict('records'),
                    style_data_conditional=style_data_conditional,
                    style_table={'height': '400px', 'overflowY': 'auto'},  # Make the table scrollable
                style_cell={'minWidth': '150px', 'width': '150px', 'maxWidth': '150px'},  # Set column widths
                fixed_rows={'headers': True},
                )
            ]) for k, v in dfs.items()]
        ]
    )

  
    return app
 
