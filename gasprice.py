import json
import unittest
import os
import requests
import http.client
import sqlite3
import time

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

area_id = ['PET.WG4ST_R10_1.W', 'PET.WG4ST_R30_1.W', 'PET.WG4ST_R20_1.W', 'PET.WG4ST_R40_1.W ', 'PET.WG4ST_R50_1.W']


for area in area_id:
	base_url = get_url(area)
	area_info = get_info(base_url)

oil_prices = read_cache("cache_oilweekly.json")

# ==============================================================================
# setup database

path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path + '/' + "oil.db")
cur = conn.cursor()


cur.execute("DROP TABLE IF EXISTS Pricing")
cur.execute("CREATE TABLE IF NOT EXISTS Pricing (Area TEXT PRIMARY KEY, WEEK_1 VARCHAR(10), WEEK_2 VARCHAR(10),  WEEK_3 VARCHAR(10), WEEK_4 VARCHAR(10), WEEK_5 VARCHAR(10), WEEK_6 VARCHAR(10), WEEK_7 VARCHAR(10), WEEK_8 VARCHAR(10), WEEK_9 VARCHAR(10), WEEK_10 VARCHAR(10), WEEK_11 VARCHAR(10), WEEK_12 VARCHAR(10), WEEK_13 VARCHAR(10), WEEK_14 VARCHAR(10), WEEK_15 VARCHAR(10), WEEK_16 VARCHAR(10), WEEK_17 VARCHAR(10), WEEK_18 VARCHAR(10), WEEK_19 VARCHAR(10))")


for area in area_id:
	count = 1
	lst = []
	base_url = get_url(area)
	area_info = get_info(base_url)
	name = area_info['series'][0]['name']
	for i in area_info['series'][0]['data'][0:19]:
		p = i[1]
		lst.append(p)
		count += 1
		if count == 20:
			print("Pausing")
			time.sleep(1)
			print("Ok")
			cur.execute("INSERT INTO Pricing (Area, WEEK_1, WEEK_2, WEEK_3, WEEK_4, WEEK_5, WEEK_6, WEEK_7, WEEK_8, WEEK_9, WEEK_10, WEEK_11, WEEK_12, WEEK_13, WEEK_14, WEEK_15, WEEK_16, WEEK_17,WEEK_18, WEEK_19) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (name, lst[0], lst[1], lst[2], lst[3], lst[4], lst[5], lst[6], lst[7], lst[8], lst[9], lst[10], lst[11], lst[12], lst[13], lst[14], lst[15], lst[16], lst[17], lst[18]))
			conn.commit()
print("Finished adding data to database")
			
#=============================================================================================================================================================================================================================================================================================================================================================
#find averages of each week from Pricing table

cur.execute("SELECT AVG(WEEK_1), AVG(WEEK_2), AVG(WEEK_3), AVG(WEEK_4), AVG(WEEK_5), AVG(WEEK_6), AVG (WEEK_7), AVG(WEEK_8), AVG(WEEK_9), AVG(WEEK_10), AVG(WEEK_11), AVG(WEEK_12), AVG(WEEK_13), AVG(WEEK_14), AVG(WEEK_15), AVG(WEEK_16), AVG(WEEK_17), AVG(WEEK_18), AVG(WEEK_19) AS Average FROM Pricing")
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
def max_value(week):
	maxx = cur.execute(f"SELECT MAX({week}) FROM Pricing")
	return maxx

max_value("WEEK_6")
# =============================================================================================================
#test calculation methods



