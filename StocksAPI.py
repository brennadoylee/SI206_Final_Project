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
import numpy as np 
import matplotlib.ticker as ticker

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

'''

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

'''
def Ndate(year = 2020, month = 4, day = 1):
    if len(str(month)) == 1:
        month = "0" + str(month)
    if len(str(day)) ==1:
        day = '0' + str(day) 
    year = str(year)
    day = str(day)
    month = str(month)
    d = str(year + '-' + month + '-' + day)
    cur.execute('SELECT close FROM Nasdaq WHERE timestamp = ?', (d,))
    stock = cur.fetchall()
    print(stock)
    return stock

#Retrieve Nasdaq stock prices
def nasdaq(cur = cur, conn = conn):
    cur.execute('SELECT Date, ClosingPrice FROM Nasdaq')
    data = cur.fetchall()
    return data

n = nasdaq()
d, p = zip(*n)

fig = plt.figure(figsize=(10,5))
ax = fig.add_subplot(111)
ax.plot(d, p, color = 'teal')
plt.xticks(fontsize = 8, rotation = 45)
ax.xaxis.set_major_locator(ticker.LinearLocator(10))
ax.set_xlabel('Date')
ax.set_ylabel('NASDAW Closing Stock Price')
ax.set_title('NASDAQ Closing Stock Price by Date')
fig.savefig('NASDAQClosingPrice.png')

plt.show()


dec = []
jan = []
feb = []
mar = []
apr = []
other = []
for date in n:
    if '2019-12' in date[0]:
        dec.append(date)
    elif '2020-01' in date[0]:
        jan.append(date)
    elif '2020-02' in date[0]:
        feb.append(date)
    elif '2020-03' in date[0]:
        mar.append(date)
    elif '2020-04' in date[0]:
        apr.append(date)
    else:
        print(date)

