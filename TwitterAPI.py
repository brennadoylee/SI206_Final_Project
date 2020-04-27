import tweepy
import datetime
from textblob import TextBlob
import csv
import matplotlib.pyplot as plt
import json
import sqlite3
import os
import time
import numpy as np
import matplotlib.ticker as ticker


consumer_key='SVaUMV92pJosw7f95Fdif2Eqi'
consumer_secret='fTVKKnHpsA5WbCZanXFfyxbKh0QDDsjM7ZZpYv1jIhP0IzrhUE'
access_token='2249378049-VGOJPkBMvlaAb3m7xpySNoAIITwW274TucQq72x'
access_token_secret='KdedfOf5aruqkwPhCvYSPgjLgp6FKkezjpbiCbbxFMhZM'
screenname = "@CDCgov"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


def tweet_analysis(tweet): 
    analysis = TextBlob(tweet)        
    if analysis.sentiment[0]>0:       
        result = 'Positive'  
    elif analysis.sentiment[0]<0:       
        result = 'Negative'  
    else:       
        result = 'Neutral'
    return result

def get_all_tweets(screen_name):
    startDate = datetime.datetime(2019, 12, 1, 0, 0, 0)
    endDate =   datetime.datetime(2020, 4, 26, 0, 0, 0)
    #initializing a list to hold all the tweepy Tweets
    tweets = []  

    # make the initial request for most recent tweets (200 is the maximum allowed count)
    
    tmpTweets = api.user_timeline(screen_name = screenname)

    # getting tweets from the CDC
    screen_name = "CDC"

    #grabbing tweets between december 2019 and april 2020
    for tweet in tmpTweets:
        if tweet.created_at < endDate and tweet.created_at > startDate:
            tweets.append(tweet)

    # keep grabbing tweets until there are no tweets left to grab
    while (tmpTweets[-1].created_at > startDate):
        print("Last Tweet @", tmpTweets[-1].created_at, " - fetching some more")
        tmpTweets = api.user_timeline(screen_name = screenname, max_id = tmpTweets[-1].id)
        for tweet in tmpTweets:
            if tweet.created_at < endDate and tweet.created_at > startDate:
                tweets.append(tweet)

    #organizing the data and calling tweet_analysis to get the sentiment 
    all_tweets = [[str(tweet.id_str), str(tweet.created_at.date()), str(tweet_analysis(str(tweet.text.encode("utf-8")))), str(tweet.text.encode("utf-8"))] for tweet in tweets]
    return all_tweets

# to reverse the dates
def reverse(lst): 
    new_lst = lst[::-1] 
    return new_lst

# calling get_all_tweets to get all of the data to insert into tables
all_tweets = get_all_tweets(screenname)


#------------------------- EXPORTING DATA TO SQLITE DATABASE ----------------------

# setting up database
path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path + '/' + "finalprojectdatabase.db")
cur = conn.cursor()

#creating table for sentiment analysis of only covid tweets table
'''
count = 0
cur.execute("DROP TABLE IF EXISTS TweetSentiment")
cur.execute("CREATE TABLE IF NOT EXISTS TweetSentiment(id TEXT PRIMARY KEY, date TEXT, sentiment TEXT , tweet TEXT)")
conn.commit()
for tweet in all_tweets:
    if "COVID" or "coronavirus" in tweet[3]:
        count += 1
        cur.execute("INSERT OR IGNORE INTO TweetSentiment VALUES (?, ?, ?, ?)", (tweet[0], tweet[1], tweet[2],tweet[3]))
        conn.commit()
        if count % 10 == 0:
            print('Pausing for a bit...')
            time.sleep(5)

print("------")

#creating a table counting how many time the word covid was tweeted each day
count = 0
cur.execute("DROP TABLE IF EXISTS TotalTweets")
cur.execute("CREATE TABLE IF NOT EXISTS TotalTweets(date TEXT PRIMARY KEY, corona_tweet_count INTEGER)")
conn.commit()
corona_tweet_count = {}
all_tweet_count = {}
for tweet in all_tweets:
    date = tweet[1]
    text = tweet[3]
    if "COVID" or "coronavirus" in text:
        if date not in corona_tweet_count:
            corona_tweet_count[date] = 1
        else:
            corona_tweet_count[date] += 1

for key in corona_tweet_count:
    cur.execute("INSERT OR IGNORE INTO TotalTweets VALUES (?, ?)", (key, corona_tweet_count[key]))
    conn.commit()
    if count % 10 == 0:
        print('Pausing for a bit...')
        time.sleep(5)
'''

# -------------- PULLING DATA / CREATING MATPLOTLIB GRAPHS --------------------

# pulling the date and corona_tweet_count from the TotalTweets data
def covid_tweet_count(cur = cur, conn = conn):
     cur.execute('SELECT date, corona_tweet_count FROM TotalTweets')
     data = cur.fetchall()
     return data

# calling hte function and organizing the data
covid_tweet_count = covid_tweet_count(cur = cur, conn = conn)
total_dates = []
tweet_count = []
for tweet in covid_tweet_count:
    total_dates.append(tweet[0])
    tweet_count.append(tweet[1])
    

# creating a graph of the number of Covid related tweets per day from the TotalTweet Data
fig = plt.figure(figsize = (10,5))
ax = fig.add_subplot(111)
ax.plot(reverse(total_dates), tweet_count, color = "purple")
plt.xticks(fontsize = 8, rotation = 90)
ax.xaxis.set_major_locator(ticker.LinearLocator(10))
ax.set_xlabel("Dates")
ax.set_ylabel("Tweet Frequency")
ax.set_title("Number of Tweets the CDC has Released containing the word 'COVID' or 'Coronavirus' since Deceber 1, 2019")
ax.grid()
fig.savefig("total_tweets.png")
plt.show()

# pulling the dates and sentiments from the TweetSentiment table
def tweet_sentiment(cur = cur, conn = conn):
    cur.execute('SELECT date, sentiment FROM TweetSentiment')
    data = cur.fetchall()
    return data

# calling the function and getting the number of same sentiment analyisis of all covid related tweets
pos_tweet_count = {}
neg_tweet_count = {}
neutral_tweet_count = {}
tweet_sentiment = tweet_sentiment(cur,conn)
dates = []
for tweet in tweet_sentiment:
    date = tweet[0]
    dates.append(date)
    sentiment = tweet[1]
    if sentiment == "Positive":
        if date not in pos_tweet_count:
            pos_tweet_count[date] = 1
        pos_tweet_count[date] += 1
    if sentiment == "Negative":
        if date not in neg_tweet_count:
            neg_tweet_count[date] = 1
        neg_tweet_count[date] += 1
    if sentiment == "Neutral":
        if date not in neutral_tweet_count:
            neutral_tweet_count[date] = 1
        neutral_tweet_count[date] += 1

#organizing the counts into lists
pos_tweets = []
pos_dates = []

for key in pos_tweet_count:
    pos_tweets.append(pos_tweet_count[key])
    pos_dates.append(key)


neg_tweets = []
for key in neg_tweet_count:
    neg_tweets.append(neg_tweet_count[key])

neutral_tweets = []
for key in neutral_tweet_count:
    neutral_tweets.append(neutral_tweet_count[key])

#creating a graph of the sentiment analysis of the cvid related tweets per day from the TweetSentiment table
fig = plt.figure(figsize = (10,5))
ax = fig.add_subplot(111)
ax.plot(reverse(pos_dates), pos_tweets, color = "green", label = "positive")
ax.plot(neg_tweets, color = "red", label = "negative")
ax.plot(neutral_tweets, color = "blue", label = "neutral")
plt.xticks(fontsize = 8, rotation = 90)
ax.xaxis.set_major_locator(ticker.LinearLocator(10))
ax.set_xlabel("Dates")
ax.set_ylabel("Tweet Frequency")
ax.set_title("Sentiment Analysis of Every Tweet Containing the word 'COVID' or 'Coronavirus' released by the CDC since December 1, 2019")
ax.grid()
ax.legend()
fig.savefig("setiment_analysis.png")
plt.show()

# -------------------------- Joint Visualization between CDC Tweets about COVID19 and Nasdaq Stock Prices in Since December 1, 2019 --------------------

# pulling and organizing the data
def nasdaq_data(cur = cur, conn = conn):
    cur.execute('SELECT Date, ClosingPrice FROM Nasdaq')
    data = cur.fetchall()
    return data 

nasdaq_data = nasdaq_data(cur, conn)
nasdaq_dates = []
nasdaq_prices = []
for data in nasdaq_data:
    nasdaq_dates.append(data[0])
    nasdaq_prices.append(data[1])
nasdaq_dec_dates = nasdaq_dates[10:]
nasdaq_dec_prices =  nasdaq_prices[10:]

#creating the graph
fig = plt.figure(1)
tweet_ax = plt.subplot(1,2,1)
tweet_ax.plot(reverse(total_dates), tweet_count, color = "mediumturquoise")
plt.suptitle("CDC Coronavirus-related Tweet Count vs NASDAQ Closing Stock Prices in Dollars")
plt.ylabel("Number of Tweets the CDC Has Released Containing Word 'COVID' or 'Coronavirus' Since December 1, 2019")
plt.xlabel("Date")
plt.xticks(fontsize = 8, rotation = 90)
tweet_ax.xaxis.set_major_locator(ticker.LinearLocator(10))

nas_ax = plt.subplot(1, 2, 2)
plt.plot(nasdaq_dec_dates, nasdaq_dec_prices, color = "orchid")
plt.xlabel('Date')
plt.ylabel('NASDAQ Closing Stock Price ')
plt.xticks(fontsize = 8, rotation = 90)
nas_ax.xaxis.set_major_locator(ticker.LinearLocator(10))

fig.savefig("TweetCountvsNasdaq")
plt.show()
