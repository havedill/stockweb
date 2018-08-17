import csv
import re
import time

import requests
import urllib3
import yaml
from bs4 import BeautifulSoup as BS
from colorama import Back, Fore, Style, init

import arrow
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import plotly.plotly as py
from app import app
from iexfinance import Stock, get_historical_data

http = urllib3.PoolManager()
init(autoreset=True)

requests.packages.urllib3.disable_warnings() 

csvfile = 'historical.csv'
#load the figure as a global variable so after hours we can keep it up

fig = {}
generateclose = 0
closedic = {}

with open("config.yaml", 'r') as configfile:
    cfg = yaml.load(configfile)
symbols = []
for k,v in cfg['positions'].items():
    symbols.append(k)

layout = html.Div([
     dcc.Graph(id='live-table')
    ])

def get_price(sym):
    start = time.time()
    pattern = re.compile(r'^\$([0-9]+\.[0-9]+)', re.MULTILINE)
    try:
        symbol = Stock(sym)
        price = symbol.get_price()
    except:
        soup = pull_website(sym)
        text = soup.find('p', {'class':f'last_price'})
        if not hasattr(text, 'text'):
            text = soup.find('div', {'class':f'last_price_mf'})
            #print(text.text)
        price = re.search(pattern, text.text).group(1)
    end = time.time()
    #print(f'{sym} price generation took {end-start} seconds')
    return float(price)

def get_close(sym):
    start = time.time()
    try:
        symbol = Stock(sym)
        symclose = symbol.get_close()

    except:
        symclose = alternative_close(sym)
    
    end = time.time()
    #print(f'{sym} close generation took {end-start} seconds')
    return symclose

def pull_website(sym):
    url = f"https://www.zacks.com/stock/quote/{sym}?q={sym}"
    response = http.request('GET', url)
    soup = BS(response.data)
    return soup

def alternative_close(sym):
    soup = pull_website(sym)
    currentprice = get_price(sym)
    text = soup.find('p', {'id':'net_change'})
    if not hasattr(text, 'text'):
         text = soup.find('div', {'class':f'change'})
    pattern = re.compile(r'([\+|\-])', re.MULTILINE)
    direction = re.search(pattern, text.text).group(1)
    change = re.search(r'[\+|\-]([0-9]+\.[0-9]+)', text.text).group(1)
    if "+" in direction:
        altclose = currentprice - float(change)
    else:
        altclose = currentprice + float(change)
    return altclose

def calculate_profit(symbol, currentprice, closeprice):
    profit = 0
    pull = cfg['positions'].get(symbol, None)
    if pull:
        shares = pull['shares']
        basis = pull['basis']
        currentvalue = shares * currentprice
        costvalue = shares * basis
        profit = currentvalue - costvalue
        today = currentvalue - (closeprice * shares)
    #print(f'{symbol}: Close={closeprice} CurrentVal={currentvalue} Profit={profit} Today={today}')
    return profit, today

def calculate_todaysgain(symbol, currentprice, closeprice):
    percentage = (currentprice/closeprice)-1
    percentage = round(percentage *100, 3)
    return percentage


@app.callback(
    dash.dependencies.Output('live-table', 'figure'),
    [dash.dependencies.Input('live-interval', 'n_intervals')]
    )
def generate_table(whatever):
    pricedic = []
    profitdic = []
    percentdic = []
    gaindic = []
    total = 0
    global fig
    global generateclose

    now = arrow.now()
    marketopen = now.replace(hour=8, minute=25, second=00)
    marketclose = now.replace(hour=15, minute=5, second=00)
    if now < marketclose and now > marketopen and now.weekday() != 5 and now.weekday() !=6:
        if  generateclose == 0:
            global closedic
            closedic = {}
            generateclose = 1
            for symbol in symbols:
                closeprice = get_close(symbol)
                closedic[symbol] = closeprice
                
        start = time.time()
        for symbol in symbols:
            price = round(get_price(symbol), 2)
            pricedic.append(price)
            profit, gain = calculate_profit(symbol, price, closedic[symbol])
            profit =  round(profit, 2)
            profitdic.append(profit)
            percent = calculate_todaysgain(symbol, price, closedic[symbol])
            percentdic.append(percent)
            gaindic.append(gain)

            pricecolor='LIGHTRED_EX'
            perccolor='LIGHTRED_EX'
            gaincolor='LIGHTRED_EX'
            if price > 0.0:
                pricecolor = 'GREEN'
            if percent > 0.0:
                perccolor = 'GREEN'
            if gain  > 0.0:
                gaincolor = 'GREEN'
            pricemeth = getattr(Fore, pricecolor)
            percmeth = getattr(Fore, perccolor)
            profitmeth = getattr(Fore, gaincolor)
            print(Fore.WHITE + str(symbol) + ' Price=' + pricemeth + str(price)  + Style.RESET_ALL + ' PercentToday=' + percmeth + str(percent) + Style.RESET_ALL + ' TodaysProfit=' + profitmeth + str(gain))
            total += profit
        end = time.time()
        #print(f'Total calculations took {end-start} seconds')
    #append the TOTALS Row
        start = time.time()
        symlist = []
        symlist = symbols[:]
        symlist.append('TOTAL')
        pricedic.append('')
        profitdic.append(total)
        percentdic.append(sum(p for p in percentdic))
        gaindic.append(sum(g for g in gaindic))
        table_trace=dict(type = 'table',
            columnwidth= [5]+[5],
            columnorder=[0, 1, 2, 3, 4],
            header = dict(height = 40,
                values = [['<b>Symbol</b>'], ['<b>Price</b>'], ['<b>Todays Gain</b>'], ['<b>Todays Profit</b>'], ['<b>Total Profit</b>']],
                line = dict(color='rgb(50,50,50)'),
                align = ['left']*2,
                font = dict(color=['rgb(45,45,45)']*2, size=12),
                fill = dict( color = 'rgb(235,235,235)' )
                ),
            cells = dict(values = [symlist, pricedic, percentdic, gaindic, profitdic],
                line = dict(color='#506784'),
                align = ['left']*5,
                font = dict(color=['rgb(40,40,40)']*2, size=10),
                format = [None, ",.2f"],
                prefix = ['','$','','$','$'],
                suffix = ['','','%', '', ''],
                height = 20,
                fill = dict(color=['rgb(245,245,245)',#unique color for the first column
                                ['rgba(0,250,0, 0.8)' if val>=0 else 'rgba(250,0,0, 0.8)' for val in gaindic] ]
                #the cells in the second column colored with green or red, according to their values
                            )
                    )
                )
        stored_data = [arrow.now().format('YYYY-MM-DD HH:mm:ss'), total]

        with open('historical.csv', 'a', newline='') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(stored_data)
        csvFile.close()
        
        layout = dict(width=900, height=500, autosize=False) 
        fig = dict(data=[table_trace], layout=layout)
        end = time.time()
        #print(f'Table generation took {end-start} seconds')
    else:
        print(f'Markets are sleeping. So we are too :)')
        generateclose = 0
    return fig
