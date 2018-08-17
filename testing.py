import yaml
from iexfinance import Stock, get_historical_data
import arrow
import csv
import json
from datetime import datetime, timedelta

with open("config.yaml", 'r') as configfile:
    cfg = yaml.load(configfile)
symbols = []
for k,v in cfg['positions'].items():
    symbols.append(k)

def get_price(sym):
    symbol = Stock(sym)
    price = symbol.get_price()
    return price

#print(get_price('CARA'))


def fill_historicalvalues(symbols, months=1):
    end = datetime.now() 
    start = datetime.now() - timedelta(days=(months*30))
    data = {}
    mytable = {}
    for symbol in symbols:
        try:
            data[symbol] = get_historical_data(symbol, start=start, end=end, output_format='json')
        except:
            pass
    
    for k, v in data.items():
        for date, values in v[k].items():
                profit = 0
                pull = cfg['positions'].get(k, None)
                if pull:
                    shares = pull['shares']
                    basis = pull['basis']
                    dayvalue = shares * values['close']
                    costvalue = shares * basis
                    profit = dayvalue - costvalue
                    print(f'Date={date} Sym={k} Profit={profit}')
                    if str(date) in mytable:
                        mytable[str(date)] += profit
                    else:
                        mytable[str(date)] = profit

    for k, v in mytable.items():
        row = [k, v]
        with open('backfill.csv', 'a', newline='') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(row)
        csvFile.close()


#fill_historicalvalues(symbols, months=1)