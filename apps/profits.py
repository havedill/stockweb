import dash
import dash_core_components as dcc
from datetime import datetime, timedelta
import dash_table_experiments as dt
import dash_html_components as html
import yaml
import pandas as pd
import arrow
import plotly.graph_objs as go
from iexfinance import Stock, get_historical_data
from app import app

layout = html.Div([
    dcc.Slider(
        id='week-slider',
        min=0,
        max=10,
        step=None,
        marks={0: 'Today',
               1: '2 days',
               2: '3 days',
               3: '4 days',
               4: '5 days',
               5: '6 days',
               6: '14 days',
               7: '30 days',
               8: '3 months',
               9: '6 months',
               10: '1 year'
        },
        value=0,
    ),
    html.P(),
    dcc.Graph(id='profit-graph')
], style = {'marginLeft': 15, 'marginRight': 15})


@app.callback(
    dash.dependencies.Output('profit-graph', 'figure'),
    [dash.dependencies.Input('interval-component', 'n_intervals'),
    dash.dependencies.Input('week-slider', 'value')]
    )
def profit_graph(unused, index):
    csvfile = 'historical.csv'
    slidersensitivity = [0, 1, 2, 3, 4, 5, 14, 30, 60, 180, 360]
    now = arrow.now()
    daysback = now.shift(days=-1).replace(hour=15, minute=00, second=00)
    days = slidersensitivity[index]
    if days != 0:
        daysback = now.shift(days=(days*-1)).replace(hour=8, minute=15, second=00)
    print(f'Filtering profit chart limited to {daysback}')
    df = pd.read_csv(csvfile)
    data = []
    filtereddata = df[(df.Date > daysback.format('YYYY-MM-DD HH:mm:ss'))]
    linecolor = 'rgb(255,0,0)'
    #print(list(filtereddata.TodaysProfit)[-1])
    if list(filtereddata.TodaysProfit)[-1] > 0:
        linecolor = 'rgb(34,139,34)'
    totalprofitline = go.Line(x=list(filtereddata.Date),
                        y=list(filtereddata.Profit),
                        text=filtereddata.Profit,
                        name="Total Profits")
                        
    if days > 30:
        graphtype = "date"
    else:
        graphtype = "category"
                            
    if days == 0:
        todaysprofitline = go.Line(x=list(filtereddata.Date),
                            y=list(filtereddata.TodaysProfit),
                            name="Todays Profits",
                            yaxis="y2",
                            line=dict(
                                color = (linecolor)
                            )
                            )
        data = [totalprofitline, todaysprofitline] 
        output = {
        'data': data,
        'layout' : go.Layout(
            yaxis={'title': 'Profits'},
            yaxis2={'title': 'Todays Profits',
                    'side': 'right',
                    'overlaying':'y'},
            xaxis={'type':graphtype,
                'tickangle': 45}
        )}
    else:
        data = [totalprofitline] 
        output = {
        'data': data,
        'layout' : go.Layout(
            yaxis={'title': 'Profits'},
            xaxis={'type':graphtype,
                'tickangle': 45}
        )}
  
    return output
