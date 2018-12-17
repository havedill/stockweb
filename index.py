import dash_core_components as dcc
import dash_html_components as html
import yaml
import dash
from app import app
from apps import livetable, historical, profits

with open("config.yaml", 'r') as configfile:
    cfg = yaml.load(configfile)
symbols = []
csvfile = 'historical.csv'
for k,v in cfg['positions'].items():
    symbols.append(k)

def get_options():
    options = []
    for symbol in symbols:
        options.append({'label': symbol, 'value': symbol})
    return options


app.layout = html.Div([   
    dcc.Location(id='url', refresh=True),
    html.Div(id='page-content'),
        dcc.Interval(
        id='live-interval',
        interval=5000, # in milliseconds
        n_intervals=0
    ),
    dcc.Interval(
        id='interval-component',
        interval=10000, # in milliseconds
        n_intervals=0
    ),
])

@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    #log.info(f'Page {pathname} requested')
    if pathname == '/historical':
        return historical.layout
    elif pathname == '/profits':
        return profits.layout
    else:
        return livetable.layout

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
