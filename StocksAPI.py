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



def getCompanyInfo(symbols):
    stock_batch = Stock(symbols,
                        token='pk_0b97f59343db4ac18746910e73a44945')
    company_info = stock_batch.get_company()
    return company_info


def getHistoricalPrices(stock, start, end):
    return get_historical_data(stock, start, end, close_only = True, token="pk_0b97f59343db4ac18746910e73a44945")

#Date Range
start = datetime(2019, 11, 15)
end = datetime(2020, 4, 17)

#Connecting to Database
path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path + '/' + "finalprojectdatabase.db")
cur = conn.cursor()

'''
#Collecting Information for Nasdaq Stock
count = 0
historicalPrices = getHistoricalPrices('NDAQ', start, end)
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
#Retrieve NASDAQ stock price by a certain day
def Ndate(year = 2020, month = 4, day = 1):
    if len(str(month)) == 1:
        month = "0" + str(month)
    if len(str(day)) ==1:
        day = '0' + str(day) 
    year = str(year)
    day = str(day)
    month = str(month)
    d = str(year + '-' + month + '-' + day)
    cur.execute('SELECT Date, ClosingPrice FROM Nasdaq WHERE Date = ?', (d,))
    stock = cur.fetchall()
    return stock

#Retrieve Nasdaq stock prices
def nasdaq(cur = cur, conn = conn):
    cur.execute('SELECT Date, ClosingPrice FROM Nasdaq')
    data = cur.fetchall()
    return data

n = nasdaq()
d, p = zip(*n)

#Calculating NASDAQ Average Stock Monthly Price
nov = []
dec = []
jan = []
feb = []
march = []
april = []

total = nasdaq()

for date in total:
    if '2019-11' in date[0]:
        nov.append(date)
    elif '2019-12' in date[0]:
        dec.append(date)
    elif '2020-01' in date[0]:
        jan.append(date)
    elif '2020-02' in date[0]:
        feb.append(date)
    elif '2020-03' in date[0]:
        march.append(date)
    elif '2020-04' in date[0]:
        april.append(date)
    else:
        print('error with: ')
        print(date)

def monthlyNstock(month_list):
    total = 0
    date, price = zip(*month_list)
    for p in price:
        total += int(p)
    avg = total/(len(price))
    return avg

#Writes monthly average out to text file
with open ("NASDAQ_Monthly_Avg.txt", 'w') as output:
    output.write("Monthly Average" + "\n")
    np = monthlyNstock(nov)
    nd = monthlyNstock(dec)
    nj = monthlyNstock(jan)
    nf = monthlyNstock(feb)
    nm = monthlyNstock(march)
    na = monthlyNstock(april)
    st1 = f"The monthly average stock price for November was ${np}."
    st2 = f"The monthly average stock price for December was ${nd}."
    st3 = f"The monthly average stock price for January was ${nj}."
    st4 = f"The monthly average stock price for February was ${nf}."
    st5 = f"The monthly average stock price for March was ${nm}."
    st6 = f"The monthly average stock price for April was ${na}."
    sts = []
    sts.append(st1)
    sts.append(st2)
    sts.append(st3)
    sts.append(st4)
    sts.append(st5)
    sts.append(st6)
    for st in sts:
        output.write(str(st) + "\n")





#Visualization for Nasdaq Stock Prices
fig = plt.figure(figsize=(10,5))
ax = fig.add_subplot(111)
ax.plot(d, p, color = 'deepskyblue')
plt.xticks(fontsize = 7, rotation = 45)
ax.xaxis.set_major_locator(ticker.LinearLocator(10))
ax.set_xlabel('Date')
ax.set_ylabel('NASDAQ Closing Stock Price')
ax.set_title('NASDAQ Closing Stock Price by Date')
fig.savefig('NASDAQClosingPrice.png')

plt.show()


#Collecting NASDAQ prices for 2020 only
nasdaq_2020 = []
for date in n:
    if '2020' in date[0]:
        nasdaq_2020.append(date)

nasdate_2020, nasprice_2020 = zip(*nasdaq_2020)

#_______________________________________________________________________________________________________________________________________________________________________

#Collecting Gasprice Data from Database
cur.execute(
	'''
	SELECT EastCoastPricing.Date, EastCoastPricing.EastCoastPrice, GulfCoastPricing.GulfCoastPrice, MidwestPricing.MidwestPrice, RockyMountainPricing.RockyMountainPrice, WestCoastPricing.WestCoastPrice
	FROM ((((EastCoastPricing
	INNER JOIN  GulfCoastPricing ON EastCoastPricing.Date=GulfCoastPricing.Date)
	INNER JOIN MidwestPricing ON EastCoastPricing.Date=MidwestPricing.Date)
	INNER JOIN RockyMountainPricing ON EastCoastPricing.Date=RockyMountainPricing.Date)
	INNER JOIN WestCoastPricing ON EastCoastPricing.Date=WestCoastPricing.Date);
	'''
)

# =================================================================================================================================================================================================================

r = cur.fetchall()

#get list of each price from each area per week
ec_list = []
gc_list = []
m_list = []
rm_list = []
wc_list = []
for y in r:
	ec = y[1]
	gc = y[2]
	m = y[3]
	rm = y[4]
	wc = y[5]
	ec_list.append(ec)
	gc_list.append(gc)
	m_list.append(m)
	rm_list.append(rm)
	wc_list.append(wc)
eastcoast_list = ec_list[::-1]
gulfcoast_list = gc_list[::-1]
midwest_list = m_list[::-1]
rockymountain_list = rm_list[::-1]
westcoast_list = wc_list[::-1]

#Finding Gas Price Averages of Each Week from Joined
d_list = []
average_list = []
for x in r:
	avg = (x[1] + x[2] + x[3] + x[4] + x[5])/5
	d_list.append(x[0])
	average_list.append(avg)

#Reversing order of lists
date_list = (d_list[::-1])
avg_list = (average_list[::-1])

#Zipping both lists together
combined_list = list(zip(date_list, avg_list))

#Collecting Gas Prices for 2020 Only
gasdate_2020 = []
gasprice_2020 = []
for date, price in combined_list:
    if '2020' in date:
        gasdate_2020.append(date)
        gasprice_2020.append(price)


#Joint Visualization between Gas Stock Prices and Nasdaq Stock Prices in 2020
plt.figure(1)
ax1 = plt.subplot(1, 2, 1)
ax1.plot(nasdate_2020, nasprice_2020, color = 'deepskyblue')
plt.suptitle('2020 Gas vs NASDAQ Closing Stock Prices in Dollars', fontsize = 14)
plt.ylabel('NASDAQ Closing Stock Price', fontsize = 10)
plt.xlabel('Date')
plt.xticks(fontsize = 7, rotation = 45)
ax1.xaxis.set_major_locator(ticker.LinearLocator(10))


ax2 = plt.subplot(1, 2, 2)
plt.plot(gasdate_2020, gasprice_2020, color = 'mediumpurple')
plt.xlabel('Date')
plt.xticks(fontsize = 7, rotation = 45)
ax2.xaxis.set_major_locator(ticker.LinearLocator(10))
plt.ylabel('Average Closing Stock of Conventional Motor Gasoline', fontsize = 10)

plt.tight_layout()

fig.savefig('2020GasvsNASDAQStockPrices.png')
plt.show()

