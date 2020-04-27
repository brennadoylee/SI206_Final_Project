import json
import os
import requests
import http.client
import sqlite3
import time
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

path = os.path.dirname(os.path.realpath(__file__))
oil_cache = path + '/' + "cache_oilweekly.json"
api_key = "6094ff67aa668f81420be64ece1a9adb"


def read_cache(CACHE_FNAME):
	try:
		file = open(CACHE_FNAME, 'r')
		cache_dict = json.loads(file.read())
		file.close()
		return cache_dict
	except:
		cache_dict = {}
		return cache_dict


def write_cache(CACHE_FNAME, cache_dict):
	file_path = os.path.join(os.path.dirname(__file__), CACHE_FNAME)
	file = open(file_path, 'w')
	file.write(json.dumps(cache_dict))


#get proper url to call API
def get_url(area_id):
	url = f"https://api.eia.gov/series/?api_key={api_key}&series_id={area_id}"
	return url


#get data from calling API
def get_info(url, CACHE_FNAME = oil_cache):
	cache_dict = read_cache(CACHE_FNAME)

	if url in cache_dict:
		return cache_dict[url]
	else:
		request = requests.get(url)
		cache_dict[url] = json.loads(request.text)
		write_cache(CACHE_FNAME, cache_dict)
		return cache_dict[url]

area_id = ['PET.WG4ST_R10_1.W', 'PET.WG4ST_R30_1.W', 'PET.WG4ST_R20_1.W', 'PET.WG4ST_R40_1.W', 'PET.WG4ST_R50_1.W']


for area in area_id:
	base_url = get_url(area)
	area_info = get_info(base_url)

oil_prices = read_cache("cache_oilweekly.json")

# ==============================================================================
# setup database

path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path + '/' + "finalprojectdatabase.db")
cur = conn.cursor()

#create east coast table
def eastcoast_table():
	cur.execute("DROP TABLE IF EXISTS EastCoastPricing")
	cur.execute("CREATE TABLE IF NOT EXISTS EastCoastPricing (Date VARCHAR(9) PRIMARY KEY, EastCoastPrice BOOL)")

	count1 = 0
	base_url = get_url('PET.WG4ST_R10_1.W')
	area_info = get_info(base_url)
	for i in area_info['series'][0]['data'][0:100]:
		date = i[0]
		newdate = date[0:4] + "-" + date[4:6] + "-" + date[-2:]
		pr = i[1]
		count1 += 1
		if count1 % 20 == 0:
			print("Pausing")
			time.sleep(1)
			print("Ok")
		cur.execute("INSERT INTO EastCoastPricing (Date, EastCoastPrice) VALUES (?,?)", (newdate, pr))
		conn.commit()
	print("Finished adding East Coast data to database")

#create Gulf Coast Table
def gulfcoast_table():
	cur.execute("DROP TABLE IF EXISTS GulfCoastPricing")
	cur.execute("CREATE TABLE IF NOT EXISTS GulfCoastPricing (Date VARCHAR(9) PRIMARY KEY, GulfCoastPrice BOOL)")
	count1 = 0
	base_url2 = get_url('PET.WG4ST_R30_1.W')
	area_info2 = get_info(base_url2)
	for a in area_info2['series'][0]['data'][0:100]:
		date2 = a[0]
		newdate2 = date2[0:4] + "-" + date2[4:6] + "-" + date2[-2:]
		pr2 = a[1]
		count1 += 1
		if count1 % 20 == 0:
			print("Pausing")
			time.sleep(1)
			print("Ok")
		cur.execute("INSERT INTO GulfCoastPricing (Date, GulfCoastPrice) VALUES (?,?)", (newdate2, pr2))
		conn.commit()
	print("Finished adding Gulf Coast data to database")	
gulfcoast_table()

#create Midwest Table
def midwest_table():
	cur.execute("DROP TABLE IF EXISTS MidwestPricing")
	cur.execute("CREATE TABLE IF NOT EXISTS MidwestPricing (Date VARCHAR(9) PRIMARY KEY, MidwestPrice BOOL)")
	count1 = 0
	base_url3 = get_url('PET.WG4ST_R20_1.W')
	area_info3 = get_info(base_url3)
	for b in area_info3['series'][0]['data'][0:100]:
		date3 = b[0]
		newdate3 = date3[0:4] + "-" + date3[4:6] + "-" + date3[-2:]
		pr3 = b[1]
		count1 += 1
		if count1 % 20 == 0:
			print("Pausing")
			time.sleep(1)
			print("Ok")
		cur.execute("INSERT INTO MidwestPricing (Date, MidwestPrice) VALUES (?,?)", (newdate3, pr3))
		conn.commit()
	print("Finished adding Midwest data to database")
midwest_table()

#create Rocky Mountain table
def rockymountain_table():
	cur.execute("DROP TABLE IF EXISTS RockyMountainPricing")
	cur.execute("CREATE TABLE IF NOT EXISTS RockyMountainPricing (Date VARCHAR(9) PRIMARY KEY, RockyMountainPrice BOOL)")
	count1 = 0
	base_url4 = get_url('PET.WG4ST_R40_1.W')
	area_info4 = get_info(base_url4)
	for c in area_info4['series'][0]['data'][0:100]:
		date4 = c[0]
		newdate4 = date4[0:4] + "-" + date4[4:6] + "-" + date4[-2:]
		pr4 = c[1]
		count1 += 1
		if count1 % 20 == 0:
			print("Pausing")
			time.sleep(1)
			print("Ok")
		cur.execute("INSERT INTO RockyMountainPricing (Date, RockyMountainPrice) VALUES (?,?)", (newdate4, pr4))
		conn.commit()
	print("Finished adding Rocky Mountain data to database")
rockymountain_table()

#create West Coast table
def westcoast_table():
	cur.execute("DROP TABLE IF EXISTS WestCoastPricing")
	cur.execute("CREATE TABLE IF NOT EXISTS WestCoastPricing (Date VARCHAR(9) PRIMARY KEY, WestCoastPrice BOOL)")
	count1 = 0
	base_url5 = get_url("PET.WG4ST_R50_1.W")
	area_info5 = get_info(base_url5)
	for d in area_info5['series'][0]['data'][0:100]:
		date5 = d[0]
		newdate5 = date5[0:4] + "-" + date5[4:6] + "-" + date5[-2:]
		pr5 = d[1]
		count1 += 1
		if count1 % 20 == 0:
			print("Pausing")
			time.sleep(1)
			print("Ok")
		cur.execute("INSERT INTO WestCoastPricing (Date, WestCoastPrice) VALUES (?,?)", (newdate5, pr5))
		conn.commit()
	print("Finished adding West Coast data to database")
westcoast_table()

#=============================================================================================================================================================================================================================================================================================================================================================
def join_tables():
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
	conn.commit()
join_tables()
# =================================================================================================================================================================================================================
#get list of each price from each area per week
r = cur.fetchall()

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



#find averages of each week from joined 
d_list = []
average_list = []
tup_list = []
for x in r:
	avg = (x[1] + x[2] + x[3] + x[4] + x[5])/5
	d_list.append(x[0])
	average_list.append(avg)
	tup = (x[0], avg)
	tup_list.append(tup)
date_list = (d_list[::-1])
avg_list = (average_list[::-1])


#writes average from joined out to text file
with open("Oil_Averages.txt", "w") as output:
	output.write("Week, Average Conventional Motor Oil Stock Price in U.S.\n")
	for t in tup_list:
		d = str(t[0])
		p = str(t[1])
		st = f"The week of {d} the average conventional motor oil stock price was ${p}"
		output.write(str(st) + "\n")

#=============================================================================================================================================================================================================================================================================================================================================================

#create visualization of multiple line lineplot for each area
fig, ax = plt.subplots()
ax.plot(date_list, eastcoast_list, "-r", label = "East Coast")
ax.plot(date_list, gulfcoast_list, "-m", label = "Gulf Coast")
ax.plot(date_list, midwest_list, "-y", label = "Midwest")
ax.plot(date_list, rockymountain_list, "-b", label = "Rocky Mountains")
ax.plot(date_list, westcoast_list, "-g", label = "West Coast")
ax.legend(loc = "upper left")
plt.xticks(fontsize = 5, rotation = 45)
ax.xaxis.set_major_locator(ticker.LinearLocator(10))
ax.set_xlabel("Date")
ax.set_ylabel("Ending Stock of Conventional Motor Gasoline (Dollars) Per Week")
ax.set_title("Ending Stock of Conventional Motor Gasoline Per Week By Area in U.S.")
ax.grid

fig.savefig("AreaOilPriceWeekly.png")

plt.show()

# =======================================================================================================
#create visualization of average gas price line plot

fig, ax = plt.subplots()
ax.plot(date_list, avg_list)
plt.xticks(fontsize = 5, rotation = 45)
ax.xaxis.set_major_locator(ticker.LinearLocator(10))
ax.set_xlabel("Date")
ax.set_ylabel("Average Ending Stock of Conventional Motor Gasoline (Dollars)")
ax.set_title("Average Ending Stock of Conventional Motor Gasoline, Weekly")
ax.grid()

fig.savefig("AverageOilPriceWeekly.png")
plt.show()
# =======================================================================================================
#get tweet sentiment analysis
cur.execute("SELECT * FROM TotalTweets")
t = cur.fetchall()
info_list = [list(elem) for elem in t]
#print(info_list)
list_dates = []
tweets = []
for i in info_list:
	date = i[0]
	twe = i[1]
	list_dates.append(date)
	tweets.append(twe)
list_dates = list_dates[::-1]
tweets = tweets[::-1]
# print(len(list_dates))
# print(len(tweets))

avg_list = avg_list[-21:]
date_list = date_list[-21:]

#tweet count vs oil stock visualization
plt.figure(1)
tweet_ax = plt.subplot(1,2,1)
tweet_ax.plot(list_dates, tweets, color = "cyan")
plt.suptitle("CDC Tweet Count vs Average Ending Stock of Conventional Motor Gasoline")
plt.ylabel("Tweet Counts CDC Has Released Containing Word COVID or Coronavirus")
plt.xlabel("Date")
plt.xticks(fontsize = 5, rotation = 45)
tweet_ax.xaxis.set_major_locator(ticker.LinearLocator(10))

oil_ax = plt.subplot(1, 2, 2)
plt.plot(date_list, avg_list, color = "magenta")
plt.xlabel('Date')
plt.ylabel('Average Ending Stock of Conventional Motor Gasoline (Dollars)')
plt.xticks(fontsize = 5, rotation = 45)
oil_ax.xaxis.set_major_locator(ticker.LinearLocator(10))

fig.savefig("TweetCountvsOilStocks")
plt.show()