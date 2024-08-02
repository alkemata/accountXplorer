import dash
import pandas as pd
from dash import html
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import csv
import plotly.graph_objs as go
from plotly.subplots import make_subplots

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
    first_index = df.index[-1]

    # Calculate the first difference
    df.at[first_index, 'Saldo'] = initial_value + df.at[first_index, column_name]

    # Calculate the differences for the rest of the rows
    for i in range(len(df) - 2, -1, -1):
        current_index = df.index[i]
        previous_index = df.index[i+1]
        df.at[current_index, 'Saldo'] = df.at[previous_index, 'Saldo'] + df.at[current_index, column_name]

    return df

def detect_transfers(row):
    if row['Konto']=='DE39360100430206819439':
        if row['Kategorie']=='PayPal':
            row['Kategorie']='Umbuchung'
        if row['Umbuchung']=='0-Euro-Konto':
            row['Kategorie']='Umbuchung'
        if row['Buchungstext']=='LASTSCHRIFT':      
            row['Kategorie']='Umbuchung' 
    if row['Konto']=='DE47700400480857576300':
        if row['Umbuchung']=='Postbank Giro extra plus':
            row['Kategorie']='Umbuchung'
    if row['Konto']=='PayPal (albanatita@gmail.com)':
        if row['Kategorie']=='Sonstige Einnahmen':
            row['Kategorie']='Umbuchung'
    return row['Kategorie']


def load_data():
    if os.path.exists('saved_dataframe.csv'):
        df = pd.read_csv('saved_dataframe.csv',sep=';') #TO>DO put file in ressources directory. See in edit as well
    else:   
        df = pd.read_csv('./ressources/dataliste.csv',sep=';')
    df['Betrag'] = pd.to_numeric(df['Betrag'].replace(',','.',regex=True), errors='coerce')
    df = df.drop(columns=['Wertstellungsdatum', 'BIC', 'Notiz','Schlagworte','SteuerKategorie','ParentKategorie','Splitbuchung','AbweichenderEmpfaenger'])
    df['Kategorie'] = df.apply(detect_transfers, axis=1)  
    return df


def save_df(dataframe): 
        dataframe.to_csv('saved_dataframe.csv', index=False)

def create_dash_app(server):
    app = dash.Dash(__name__, server=server, url_base_pathname='/overview/')


    df=load_data()
    save_df(df)

    accounts=df['Konto'].unique()
    dfs = {k: v for k, v in df.groupby('Konto')}

    filename = 'config.txt'  # Replace with your CSV file path
    account_data = load_account_data(filename)

    for k,v in dfs.items():
            initial_value = account_data[k[0:3]]['value']
            dfs[k] = calculate_differences(initial_value, v)

    for k,v in dfs.items():
        v['BuchungsDatum'] = pd.to_datetime(v['Buchungsdatum'], format='%d.%m.%Y')


    
    style_data_conditional = [
        {
            'if': {'filter_query': '{Betrag} > 0'},
            'backgroundColor': 'green',
            'color': 'white'
        },
        {
            'if': {'filter_query': '{Kategorie} = Umbuchung'},
            'backgroundColor': 'blue',
            'color': 'white'
        }
    ]

    # Create subplots
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)

    # Add traces
    fig.add_trace(
        go.Scatter(x=dfs.sort_values(by='date')['DE39360100430206819439']['BuchungsDatum'], y=dfs.sort_values(by='date')['DE39360100430206819439']['Saldo'], mode='lines', name='DataFrame 1', fill='tozeroy'),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(x=dfs.sort_values(by='date')['DE47700400480857576300']['Buchungsdatum'], y=dfs.sort_values(by='date')['DE47700400480857576300']['Saldo'], mode='lines', name='DataFrame 2', fill='tozeroy'),
        row=2, col=1
    )

    # Update layout
    fig.update_layout(
        title='Saldo Over Time',
        xaxis_title='Date',
        yaxis_title='Saldo',
        height=600
    )

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
            ]) for k, v in dfs.items()],
            html.H1(children='Saldo Over Time'),

            dcc.Graph(
            id='area-plot',
            figure=fig
    )
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
 
