Just updat the config.yaml with your stock holdings/cost basis. Stocks not available from iEXFinance have alternative get methods by parsing a webpage. Historical info / close prices for those will not be as accurate.

Run python ./index.py to start the webapp running on localhost:8050/

Available URLS are /, /historical, /profits


Must always be on the / page to get updated values / write values to the csv for historical profit data.

testing.py contains a script to backfill profits vs dates