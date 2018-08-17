import dash
import dash_core_components as dcc
from datetime import datetime, timedelta
import dash_html_components as html
import yaml
import pandas as pd

import plotly.graph_objs as go
from iexfinance import Stock, get_historical_data
from app import app

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

layout = html.Div([
    html.Label('Symbols'),
    dcc.Checklist(
        id='symbols',
        options=get_options(),
        #default values to select are below
        values=['SPY']
        ),
     dcc.Graph(id='history-graph')
     
])

def get_history(sym="SPY", days=10):
    end = datetime.now()
    start = datetime.now() - timedelta(days=days)
    data = get_historical_data(sym, start=start, end=end, output_format='pandas')
    return data

@app.callback(
    dash.dependencies.Output('history-graph', 'figure'),
    [dash.dependencies.Input('symbols', 'values')]
    )
def update_graph(selected_options):
    data = []
    for symbol in selected_options:
        history = get_history(symbol, 180)
        #log.debug(type(history))
        data.append(go.Line(x=history.index,
        y=history['close'],
        text=symbol
        ))
   
#    log.debug(history)

    return {
        'data': data,
        'layout' : go.Layout(
            yaxis={'title': 'Close Price'}
        )
    }