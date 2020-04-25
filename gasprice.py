import json
import unittest
import os
import requests
import re
import http.client
import sqlite3
import time
import matplotlib
import matplotlib.pyplot as plt

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
cur.execute("DROP TABLE IF EXISTS GulfCoastPricing")
cur.execute("CREATE TABLE IF NOT EXISTS GulfCoastPricing (Date VARCHAR(9) PRIMARY KEY, GulfCoastPrice BOOL)")

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

#create Midwest Table
cur.execute("DROP TABLE IF EXISTS MidwestPricing")
cur.execute("CREATE TABLE IF NOT EXISTS MidwestPricing (Date VARCHAR(9) PRIMARY KEY, MidwestPrice BOOL)")

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

#create Rocky Mountain table
cur.execute("DROP TABLE IF EXISTS RockyMountainPricing")
cur.execute("CREATE TABLE IF NOT EXISTS RockyMountainPricing (Date VARCHAR(9) PRIMARY KEY, RockyMountainPrice BOOL)")

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

#create West Coast table
cur.execute("DROP TABLE IF EXISTS WestCoastPricing")
cur.execute("CREATE TABLE IF NOT EXISTS WestCoastPricing (Date VARCHAR(9) PRIMARY KEY, WestCoastPrice BOOL)")

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
#=============================================================================================================================================================================================================================================================================================================================================================
#find averages of each week from Pricing table and returns list of tuples

#cur.execute("SELECT AVG(WEEK_1), AVG(WEEK_2), AVG(WEEK_3), AVG(WEEK_4), AVG(WEEK_5), AVG(WEEK_6), AVG (WEEK_7), AVG(WEEK_8), AVG(WEEK_9), AVG(WEEK_10), AVG(WEEK_11), AVG(WEEK_12), AVG(WEEK_13), AVG(WEEK_14), AVG(WEEK_15), AVG(WEEK_16), AVG(WEEK_17), AVG(WEEK_18), AVG(WEEK_19) AS Average FROM Pricing")
r = cur.fetchall()
result = []
week_count = 1
for i in r:
	for x in i:
		time = "Week " + str(week_count)	
		#print(time)
		money = "$" + str(x)
		tup = (time, money)	
		result.append(tup)
		week_count += 1
	print(result)

#=============================================================================================================================================================================================================================================================================================================================================================
# more calculations

#takes in a list of averages per week and returns length
def length_of_avg(lst_avg):
	l = len(lst_avg)
	return l

#testing method
lst_a = [('Week 1', '$4791.2'), ('Week 2', '$4495.4'), ('Week 3', '$4296.0'), ('Week 4', '$4246.4'), ('Week 5', '$4003.8'), ('Week 6', '$4737.8'), ('Week 7', '$5037.2'), ('Week 8', '$5180.6'), ('Week 9', '$5332.2'), ('Week 10', '$5372.4'), ('Week 11', '$5433.2'), ('Week 12', '$5544.0'), ('Week 13', '$5484.8'), ('Week 14', '$5725.6'), ('Week 15', '$5462.6'), ('Week 16', '$5285.0'), ('Week 17', '$5229.2'), ('Week 18', '$4943.2'), ('Week 19', '$4709.0')]
length_of_avg(lst_a)

#find specific price based on area and week
# def find_price(area, week, price):
# 	cur.execute("SELECT ? FROM Pricing WHERE ?",(area, week, price))
# 	cur.fetchall()

# find_price("Gulf Coast (PADD 3) Ending Stocks of Conventional Motor Gasoline, Weekly", "WEEK_2", "7239")
# find_price("West Coast (PADD 5) Ending Stocks of Conventional Motor Gasoline, Weekly", "WEEK_14", "2337")

#find max value within a column
# def max_value(week):
# 	maxx = cur.execute(f"SELECT MAX({week}) FROM Pricing")
# 	return maxx

# max_value("WEEK_6")
# =============================================================================================================
#create visualization

#cur.execute("SELECT Area FROM Pricing")
l = cur.fetchall()
a_list = []
for i in l:
	for x in i:
		a_list.append(x)
b_list = []
for y in a_list:
	find = re.findall("^.*?(?=\s\()", y)
	b_list.append(find)

finalarea_list = [item for sublist in b_list for item in sublist]
print(finalarea_list)



