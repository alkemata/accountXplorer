import dash
import dash_html_components as html
import dash_core_components as dcc
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State

def create_dash_app(server):
    app = dash.Dash(__name__, server=server, url_base_pathname='/app1/')

    app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Button('Upload CSV'),
        multiple=False
    ),
    dcc.DatePickerRange(
        id='date-picker-range',
        start_date=None,
        end_date=None
    ),
    html.Button('Filter', id='filter-button'),
    dash_table.DataTable(
        id='table',
        columns=[],
        data=[],
        style_data_conditional=[],
        style_table={'overflowX': 'auto'}
    )
    ])

    

    # Callback to parse the uploaded CSV
    @app.callback(
        Output('table', 'data'),
        Output('table', 'columns'),
        Output('date-picker-range', 'start_date'),
        Output('date-picker-range', 'end_date'),
        Input('upload-data', 'contents'),
        State('upload-data', 'filename')
    )

    def load_data(contents, filename):
        if contents is None:
            return [], [], None, None

        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

        columns = [{'name': col, 'id': col} for col in df.columns]
        data = df.to_dict('records')
        start_date = df['date'].min()
        end_date = df['date'].max()

        return data, columns, start_date, end_date

    # Callback to filter the data based on date range
    @app.callback(
        Output('table', 'data'),
        Output('table', 'style_data_conditional'),
        Input('filter-button', 'n_clicks'),
        State('date-picker-range', 'start_date'),
        State('date-picker-range', 'end_date'),
        State('upload-data', 'contents')
    )
    def update_table(n_clicks, start_date, end_date, contents):
        if contents is None:
            return [], []

        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

        if start_date and end_date:
            df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

        data = df.to_dict('records')
        style_data_conditional = [
            {
                'if': {'filter_query': '{betrag} > 0', 'column_id': 'betrag'},
                'backgroundColor': 'green',
                'color': 'white'
            }
        ]

        return data, style_data_conditional


    return app
 
