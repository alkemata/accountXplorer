import dash
import dash_html_components as html
import dash_core_components as dcc

def create_dash_app(server):
    app = dash.Dash(__name__, server=server, url_base_pathname='/app1/')

    app.layout = html.Div([
        html.H1('Dash App 1'),
        dcc.Graph(
            id='example-graph',
            figure={
                'data': [
                    {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                    {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': 'NYC'},
                ],
                'layout': {
                    'title': 'Dash Data Visualization'
                }
            }
        )
    ])
    return app
