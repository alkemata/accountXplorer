import dash
import pandas as pd
from dash import html
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import csv

def load_account_data(filename):
    account_data = {}
    with open(filename, mode='r') as file:
        reader = csv.reader(file,delimiter=';')
        #next(reader)  # Skip the header row if there is one
        for row in reader:
            account_code = row[0]
            account_name = row[1]
            account_value = float(row[2])  # Assuming the value column contains numeric data
            account_data[account_code] = {'name': account_name, 'value': account_value}
    return account_data

def calculate_differences(initial_value, df, column_name='Betrag'):
    # Initialize the new column with the first value being the difference between the initial value and the first element in column a
    df['Saldo'] = 0
        # Ensure the column exists in the DataFrame
    if column_name not in df.columns:
        raise KeyError(f"Column '{column_name}' not found in DataFrame")
     # Get the index of the first row
    first_index = df.index[0]

    # Calculate the first difference
    df.at[first_index, 'difference'] = initial_value - df.at[first_index, column_name]

    # Calculate the differences for the rest of the rows
    for i in range(1, len(df)):
        current_index = df.index[i]
        previous_index = df.index[i-1]
        df.at[current_index, 'difference'] = df.at[previous_index, 'difference'] - df.at[current_index, column_name]

    return df

def create_dash_app(server):
    app = dash.Dash(__name__, server=server, url_base_pathname='/app1/')
    df = pd.read_csv('./ressources/dataliste.csv',sep=';')
    df['Betrag'] = pd.to_numeric(df['Betrag'].replace(',','.',regex=True), errors='coerce')
    df = df.drop(columns=['Wertstellungsdatum', 'BIC', 'Notiz','Schlagworte','SteuerKategorie','ParentKategorie','Splitbuchung','AbweichenderEmpfaenger'])
    accounts=df['Konto'].unique()
    dfs = {k: v for k, v in df.groupby('Konto')}

    filename = 'config.txt'  # Replace with your CSV file path
    account_data = load_account_data(filename)

    for k,v in dfs.items():
            initial_value = account_data[k[0:3]]['value']
            dfs[k] = calculate_differences(initial_value, v)

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
 
