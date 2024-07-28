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
                            dcc.Input(
                id=f'input-{k[0:3]}',
                type='text',
                placeholder='column: content',
                debounce=True
                ),
            
                dash_table.DataTable(
                    id=f'table-{k[0:3]}',
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

    # Callback for each table
    for k in dfs.keys():
        @app.callback(
            Output(f'table-{k[0:3]}', 'data'),
            [Input(f'input-{k[0:3]}', 'value')],
            [State(f'table-{k[0:3]}', 'data')]
        )
        def update_table(input_value, rows, k=k):
            if input_value:
                try:
                    column, content = input_value.split(':')
                    column = column.strip()
                    content = content.strip()
                    filtered_df = dfs[k][dfs[k][column].astype(str).str.contains(content, case=False, na=False)]
                except Exception as e:
                    filtered_df = dfs[k]  # If there's an error in input, show the unfiltered table
            else:
                filtered_df = dfs[k]

            return filtered_df.to_dict('records')
    
    return app
 
