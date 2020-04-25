import pandas as pd
from pandas import DataFrame
from iexfinance.stocks import Stock
from datetime import datetime
import matplotlib.pyplot as plt
from iexfinance.stocks import get_historical_data
import json
import sqlite3
import os
import time

baseURL = "https://cloud.iexapis.com/"

def getCompanyInfo(symbols):
    stock_batch = Stock(symbols,
                        token='pk_0b97f59343db4ac18746910e73a44945')
    company_info = stock_batch.get_company()
    return company_info


def getHistoricalPrices(stock):
    return get_historical_data(stock, start, end, close_only = True, token="pk_0b97f59343db4ac18746910e73a44945")

#Date Range
start = datetime(2019, 12, 1)
end = datetime(2020, 4, 23)

path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path + '/' + "finalprojectdatabase.db")
cur = conn.cursor()



#Collecting Information for Nasdaq Stock
count = 0
historicalPrices = getHistoricalPrices('NDAQ')
columns = ['close', 'volume']
cur.execute("DROP TABLE IF EXISTS Nasdaq")
cur.execute("CREATE TABLE IF NOT EXISTS Nasdaq(Date PRIMARY KEY, ClosingPrice)")
conn.commit()
for d in historicalPrices:
    count += 1
    cur.execute("INSERT INTO Nasdaq VALUES (?, ?)", (d, historicalPrices[d]['close']))
    conn.commit()
    if count % 10 == 0:
        print('Pausing for a bit...')
        time.sleep(5)

