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
    endDate =   datetime.datetime(2020, 4, 1, 0, 0, 0)
    #initializing a list to hold all the tweepy Tweets
    alltweets = []  

    # make the initial request for most recent tweets (200 is the maximum allowed count)
    
    new_tweets = api.user_timeline(screen_name = screenname)

    # getting tweets from the CDC
    screen_name = "CDC"

    #save most recent tweets
    alltweets.extend(new_tweets)

    #save the id of the second oldest tweet
    # oldest = alltweets[-1].id - 1

    for tweet in new_tweets:
        if tweet.created_at < endDate and tweet.created_at > startDate:
            alltweets.append(tweet)
    # keep grabbing tweets until there are no tweets left to grab
    # while len(new_tweets) > 0:
    while (new_tweets[-1].created_at > startDate):
        print("getting tweets before {}".format(new_tweets[-1].created_at))
        new_tweets = api.user_timeline(screen_name = screenname, max_id = new_tweets[-1].id - 1)
        for tweet in new_tweets:
            if tweet.created_at < endDate and tweet.created_at > startDate:
                alltweets.append(tweet)
        # using the max_id param to prevent duplicates
        # new_tweets = api.user_timeline(screen_name = screenname,count=1000,max_id=oldest)

        # #saving the most recent tweets
        # alltweets.extend(new_tweets)

        # #update the id of the second oldest tweet
        # oldest = alltweets[-1].id - 1

        # print("...{} tweets downloaded so far".format(len(alltweets)))

    #organizing the data and calling tweet_analysis to get the sentiment 

    outtweets = [[str(tweet_analysis(str(tweet.text.encode("utf-8")))), str(tweet.created_at.date()), str(tweet.id_str), str(tweet.text.encode("utf-8"))] for tweet in alltweets if "#COVID" or "#coronavirus" in tweet[3]]
    #outtweets = [[str(tweet_analysis(str(tweet.text.encode("utf-8")))), str(tweet.created_at.date()), str(tweet.id_str), str(tweet.text.encode("utf-8"))] for tweet in alltweets]
    return outtweets




#setting up database
path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path + '/' + "finalprojectdatabase.db")
cur = conn.cursor()

#creating Twitter table
all_tweets = get_all_tweets(screenname)
count = 0
cur.execute("DROP TABLE IF EXISTS Tweets")
cur.execute("CREATE TABLE IF NOT EXISTS Tweets(sentiment TEXT PRIMARY KEY, date TEXT, id TEXT , tweet TEXT)")
conn.commit()
for tweet in all_tweets:
    count += 1
    cur.execute("INSERT OR IGNORE INTO Tweets VALUES (?, ?, ?, ?)", (tweet[0], tweet[1], tweet[2],tweet[3]))
    conn.commit()
    if count % 10 == 0:
        print('Pausing for a bit...')
        time.sleep(5)

#creating a dictionary of every tweet about coronavirus published by the CDC per day
corona_tweet_count = {}
for tweet in all_tweets:
    if tweet[1] not in corona_tweet_count:
        corona_tweet_count[tweet[1]] = 1
    corona_tweet_count[tweet[1]] += 1

#creating dictionaries for number of positive, negative, and neutral tweets about coronavirus published by the CDC per day
pos_tweet_count = {}
neg_tweet_count = {}
neutral_tweet_count = {}
for tweet in all_tweets:
    date = tweet[1]
    sentiment = tweet[0]
    if sentiment == "Positive":
        if tweet[1] not in pos_tweet_count:
            pos_tweet_count[tweet[1]] = 1
        pos_tweet_count[tweet[1]] += 1
    if sentiment == "Negative":
        if tweet[1] not in neg_tweet_count:
            neg_tweet_count[tweet[1]] = 1
        neg_tweet_count[tweet[1]] += 1
    if sentiment == "Neutral":
        if tweet[1] not in neutral_tweet_count:
            neutral_tweet_count[tweet[1]] = 1
        neutral_tweet_count[tweet[1]] += 1

#seperating the dates and tweets into lists from the dictionaries
total_dates = []
total_tweets = []
for key in corona_tweet_count:
    total_dates.append(key)
    total_tweets.append(corona_tweet_count[key])

pos_dates = []
pos_tweets = []
for key in pos_tweet_count:
    pos_dates.append(key)
    pos_tweets.append(pos_tweet_count[key])

neg_dates = []
neg_tweets = []
for key in neg_tweet_count:
    neg_dates.append(key)
    neg_tweets.append(neg_tweet_count[key])

neutral_dates = []
neutral_tweets = []
for key in neutral_tweet_count:
    neutral_dates.append(key)
    neutral_tweets.append(neutral_tweet_count[key])

# to reverse the dates on the x axis
def reverse(lst): 
    new_lst = lst[::-1] 
    return new_lst


# creating total Number of Tweets per day from the CDC containing #COVID or #coronavirus graph

fig = plt.figure(figsize = (10,5))
ax = fig.add_subplot(111)
ax.plot(reverse(total_dates), total_tweets, color = "green")
plt.xticks(fontsize = 5, rotation = 90)
ax.xaxis.set_major_locator(ticker.LinearLocator(10))
ax.set_xlabel("Dates")
ax.set_ylabel("Number of Tweets")
ax.set_title("Number of Tweets per day from the CDC containing #COVID or #coronavirus since December 1, 2019")
ax.grid()
fig.savefig("total_tweets.png")
plt.show()

# creating sentiment Analysis of tweets per day from the CDC containing #COVID or #coronavirus graph

fig = plt.figure(figsize = (10,5))
ax = fig.add_subplot(111)
ax.plot(reverse(pos_dates), pos_tweets, color = "green", label = "positive")
ax.plot(neg_tweets, color = "red", label = "negative")
ax.plot(neutral_tweets, color = "blue", label = "neutral")
plt.xticks(fontsize = 5, rotation = 90)
ax.xaxis.set_major_locator(ticker.LinearLocator(10))
ax.set_xlabel("Dates")
ax.set_ylabel("Number of Tweets")
ax.set_title("Sentiment Analysis of tweets per day from the CDC containing #COVID or #coronavirus since December 1, 2019")
ax.grid()
ax.legend()
fig.savefig("setiment_analysis.png")
plt.show()
