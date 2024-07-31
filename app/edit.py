import pandas as pd
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import dash

def load_categories(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    categories = {}
    current_category = None

    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue
        if line.startswith(' '):  # Assuming sub-categories are indented
            if current_category:
                categories[current_category].append(stripped_line)
        else:
            current_category = stripped_line
            categories[current_category] = []

    return categories


def create_dash_app(server):
    app = dash.Dash(__name__, server=server, url_base_pathname='/edit/')

    df = pd.read_csv('./ressources/dataliste.csv',sep=';')
    df['Betrag'] = pd.to_numeric(df['Betrag'].replace(',','.',regex=True), errors='coerce')
    df = df.drop(columns=['Wertstellungsdatum', 'BIC', 'Notiz','Schlagworte','SteuerKategorie','ParentKategorie','Splitbuchung','AbweichenderEmpfaenger'])

    # Convert Date to datetime
    df['Buchungsdatum'] = pd.to_datetime(df['Buchungsdatum'], format='%d.%m.%Y')
    # Create a month-year column
    df['Month'] = df['Buchungsdatum'].dt.to_period('M')

    # Predefined list of categories
    categories = load_categories('./categories.txt')
    category_order  = []
    for sublist in categories.values():
        category_order.extend(sublist)

    # Set the category order
    df['Kategorie'] = pd.Categorical(df['Kategorie'], categories=category_order, ordered=True)

    # Function to create pivot table
    def create_pivot_table(dataframe):
        pivot_table = dataframe.pivot_table(values='Betrag', index='Kategorie', columns='Month', aggfunc='sum', fill_value=0)  
        pivot_table.columns = pivot_table.columns.astype(str)  # Convert Period to str
        pivot_table = pivot_table.reindex(category_order)  # Reindex to enforce the order
        return pivot_table

    pivot_table = create_pivot_table(df)

    # Function to save DataFrame
    def save_df(dataframe):
        dataframe.to_csv('saved_dataframe.csv', index=False)


    app.layout = html.Div([
        html.H1('Pivot Table'),
        dash_table.DataTable(
            id='pivot-table',
            columns=[{"name": str(i), "id": str(i)} for i in pivot_table.reset_index().columns],
            data=pivot_table.reset_index().to_dict('records'),
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left'},
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}
            ],
            row_selectable='single',
            cell_selectable=True
        ),
        html.H2('Detailed Data'),
        dash_table.DataTable(
            id='detail-table',
            columns=[{"name": col, "id": col} for col in df.columns],
            row_selectable='multi',
        ),
        html.H2('Select Category'),
        dcc.Dropdown(
            id='category-dropdown',
            options=[{'label': cat, 'value': cat} for cat in category_order],
            multi=False
        ),
        html.Button('Update Category', id='update-button', n_clicks=0),
        html.Button('Save DataFrame', id='save-button', n_clicks=0)
    ])

    @app.callback(
        Output('detail-table', 'data'),
        [Input('pivot-table', 'derived_virtual_selected_rows'),
        Input('pivot-table', 'active_cell')]
    )
    def display_details(selected_rows, active_cell):
        if active_cell:
            row = active_cell['row']
            col = active_cell['column_id']
            category = pivot_table.index[row]
            month = pd.Period(col, freq='M')  # Convert string back to Period
            print(category)
            print(month)
            # Filter the dataframe based on the selected category and month
            filtered_df = df[(df['Kategorie'] == category) & (df['Month'] == month)]
            return filtered_df.to_dict('records')
        return []

    @app.callback(
        [Output('pivot-table', 'data'),
        Output('detail-table', 'data')],
        [Input('update-button', 'n_clicks')],
        [State('detail-table', 'selected_rows'),
        State('detail-table', 'data'),
        State('category-dropdown', 'value')]
    )
    def update_category(n_clicks, selected_rows, detail_data, selected_category):
        if n_clicks > 0 and selected_rows and selected_category:
            detail_df = pd.DataFrame(detail_data)
            selected_indices = detail_df.iloc[selected_rows].index
            
            # Update the original dataframe
            for index in selected_indices:
                df.loc[index, 'Kategorie'] = selected_category
            
            # Recreate pivot table
            new_pivot_table = create_pivot_table(df)
            
            # Update data tables
            return new_pivot_table.reset_index().to_dict('records'), detail_df.to_dict('records')
        return dash.no_update, dash.no_update

    @app.callback(
        Output('save-button', 'n_clicks'),
        [Input('save-button', 'n_clicks')]
    )
    def save_dataframe(n_clicks):
        if n_clicks > 0:
            save_df(df)
        return 0

    return app
