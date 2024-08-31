import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, dash_table, no_update
from dash.dependencies import Input, Output, State
from dash import html
from dash import dcc, html, dash_table

def layout_files():

    layout= html.Div([
        html.H1("Account data editor"),
        # Input fields for file names
        html.Div([
            html.Div([
                html.Div([html.Label('Transfer file:'),dcc.Input(id='file1', type='text', value='transfer.csv', style={'margin-right': '10px'})]),
                html.Div([html.Label('Account file:'),dcc.Input(id='file2', type='text', value='processed.csv', style={'margin-right': '10px'})]),
                html.Div([html.Label('Accounts config:'),dcc.Input(id='file3', type='text', value='config.txt', style={'margin-right': '10px'})]),
                html.Div([html.Label('Categories config:'),dcc.Input(id='file4', type='text', value='categories.txt', style={'margin-right': '10px'})]),
            ], style={'display': 'flex', 'margin-bottom': '20px'})
        ]),
        
        # Button to trigger the update
        html.Button('Update Files', id='update-button'),
        
        # Logging area
        html.Div([
            dcc.Textarea(id='log', style={'width': '100%', 'height': 200}),
        ], style={'margin-top': '20px'}),
        html.Div(id='part-list-global'),
        html.Div(id='part-pivottable'),
        html.Div(id='part-saldo'),
        html.Div(id='part-planning')
    ])
    return layout

def layout_list_global(dataframe):
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
    layout= html.Div(
        children=[
            html.H1("DataFrame global"),
            dcc.Input(id='filter-input', type='text', placeholder='Enter filter like column1:value'),
            html.Button('Filter', id='filter-button', n_clicks=0),

                       
                dash_table.DataTable(
                    id=f'table-global',
                    columns=[{"name": i, "id": i} for i in dataframe.columns],
                    data=dataframe.to_dict('records'),
                    style_data_conditional=style_data_conditional,
                    style_table={'height': '400px', 'overflowY': 'auto'},  # Make the table scrollable
                style_cell={'minWidth': '150px', 'width': '150px', 'maxWidth': '150px'},  # Set column widths
                fixed_rows={'headers': True},
                )])
    return layout

def layout_categories(pivot_table, df, category_order):
    layout = html.Div([
            dbc.Row([
                dbc.Col(html.H2('Spending by category'), width=12),
                dbc.Col(
                    dash_table.DataTable(
                        id='pivot-table',
                        columns=[{"name": str(i), "id": str(i)} for i in pivot_table.reset_index().columns],
                        data=pivot_table.reset_index().to_dict('records'),
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
            html.Div([
            dcc.Textarea(id='log2', style={'width': '100%', 'height': 50}),
        ]),

            dbc.Row([
                html.Hr(style={'border': '1px solid black'}),
                dbc.Col(html.H2('Detail for a category'), width=12),
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


            dbc.Row([
                dbc.Col(html.H2('Change category'), width=12)
            ], className="mb-2"),

            dbc.Row([
                dbc.Col([
                    html.Button('Change', id='update-button-2', n_clicks=0, className="btn btn-primary mb-2"),
                    html.Button('Save', id='save-button', n_clicks=0, className="btn btn-secondary")
                ], width=2),
                dbc.Col(
                    dcc.Dropdown(
                        id='category-dropdown',
                        options=[{'label': cat, 'value': cat} for cat in category_order],
                        multi=False
                    ), width=10
                )
            ])])
    return layout

def layout_saldo(unique_accounts):
    layout=html.Div([
    dash_table.DataTable(
        id='saldo-input-table',
        columns=[
            {'name': 'Account', 'id': 'Account', 'editable': False},
            {'name': 'Date', 'id': 'Date', 'editable': True},
            {'name': 'Saldo', 'id': 'Saldo', 'editable': True}
        ],
        data=[{'Account': account, 'Date': '', 'Saldo': 0} for account in unique_accounts],
        style_table={'width': '50%'}
    ),    
    # Button to trigger saldo calculation
    html.Button('Calculate Saldos', id='calculate-button', n_clicks=0)    
    ])
    return layout

    def layer_planning(data):
        layout = html.Div([
        html.H1('Budget Management'),

        # Dash DataTable for input
        dash_table.DataTable(
            id='input-table',
            columns=[
                {'name': 'Type', 'id': 'type', 'type': 'numeric'},
                {'name': 'DateType', 'id': 'datetype', 'type': 'datetime'},
                {'name': 'Description', 'id': 'description', 'type': 'text'},
                {'name': 'Amount', 'id': 'amount', 'type': 'numeric'},
                {'name': 'Account', 'id': 'account', 'type': 'text'},
            ],
            data=df.to_dict('records'),
            editable=True,
            row_deletable=True
        ),
        html.Button('Add Row', id='add-row-button', n_clicks=0),

        html.Button('Update Occurrences', id='update-button', n_clicks=0),

        # Display calculated occurrences
        dash_table.DataTable(
            id='output-table',
            columns=[
                {'name': 'Date', 'id': 'date', 'type': 'datetime'},
                {'name': 'Amount', 'id': 'amount', 'type': 'numeric'},
                {'name': 'Description', 'id': 'description', 'type': 'text'},
                {'name': 'Account', 'id': 'account', 'type': 'text'},
            ],
            data=data
        ),
        
        html.Button('Save Data', id='save-button', n_clicks=0)
        ])
        return layout
        