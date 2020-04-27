import tweepy
import datetime
from textblob import TextBlob
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
    
    alltweets = api.user_timeline(screen_name = screenname)

    # getting tweets from the CDC
    screen_name = "CDC"

    #grabbing tweets between december 2019 and april 2020
    for tweet in alltweets:
        if tweet.created_at < endDate and tweet.created_at > startDate:
            tweets.append(tweet)

    # keep grabbing tweets until there are no tweets left to grab
    while (alltweets[-1].created_at > startDate):
        print("Last Tweet @", alltweets[-1].created_at, " - fetching some more")
        alltweets = api.user_timeline(screen_name = screenname, max_id = alltweets[-1].id)
        for tweet in alltweets:
            if tweet.created_at < endDate and tweet.created_at > startDate:
                tweets.append(tweet)

    #organizing the data and calling tweet_analysis to get the sentiment 
    all_tweets = [[str(tweet.id_str), str(tweet.created_at.date()), str(tweet_analysis(str(tweet.text.encode("utf-8")))), str(tweet.text.encode("utf-8"))] for tweet in tweets]
    return all_tweets


# calling get_all_tweets to get all of the data to insert into tables
all_tweets = get_all_tweets(screenname)


#-------------------------------------------- EXPORTING DATA TO SQLITE DATABASE --------------------------------------------

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
        if count % 20 == 0:
            print('Pausing for a bit...')
            time.sleep(1)

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
    if count % 20 == 0:
        print('Pausing for a bit...')
        time.sleep(1)
'''


# -------------------------------------------- PULLING DATA / CREATING MATPLOTLIB GRAPHS-------------------------------------




#  --- Visualization 1 --- Number of Tweets the CDC has Released containing the word 'COVID' or 'Coronavirus' since Deceber 1, 2019 Visualization (total_covid_tweets)

''' TotalTweets Table Calculation: using the TweetTotal data to calculate average number of tweets
released by the CDC each week and organizing the data into seperate lists. 
For the graph, I am using the corona_tweet_count data straight from the table to visualize how many times a
day the CDC Posted about COVID or Corona every day since December 1, 2019'''

# pulling the date and corona_tweet_count from the TotalTweets data
def covid_tweet_count(cur = cur, conn = conn):
     cur.execute('SELECT date, corona_tweet_count FROM TotalTweets')
     data = cur.fetchall()
     return data

# calling the function and organizing the data
covid_tweet_count = covid_tweet_count(cur = cur, conn = conn)
total_dates = []
tweet_count = []
for tweet in covid_tweet_count:
    total_dates.append(tweet[0])
    tweet_count.append(tweet[1])

# to reverse the dates
def reverse(lst): 
    rev = lst[::-1] 
    return rev

dates_tweets = list(zip(reverse(total_dates), tweet_count))

#dividing the list of dates into groups of 7 (equivalent to one week) startign with December 1, which is a Sunday
def creating_weeks(lst, group): 
    for i in range(0, len(lst), group):  
        yield dates_tweets[i:i + group] 
days = 7
weeks_list = list(creating_weeks(dates_tweets, days)) 

#creating a dictionary of all of the weeks and their average number of covid-related tweets that week
def tweets_per_week(lst):
    week_count = {}
    count = 0
    n = 1
    for week in lst:
        for tup in week:
             count += tup[1]
        week_count["Week " + str(n)] = count / 7  # divided by 7 to get the average number of tweets for the week
        n+=1
    return week_count
week_tweet_averages = tweets_per_week(weeks_list)


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



#  --- Visualization 2 --- Sentiment Analysis of Every Tweet Containing the word 'COVID' or 'Coronavirus' released by the CDC since December 1, 2019 (tweet_sentiment_analysis)

'''TweetSentiment Table Calculation: using the TweetSentiment data to calculate the number of 
Positive, Negative, and Neutral Tweets the CDC Tweets on each day
organizing the counts into seperate lists for easy insertion into 
Tweet_Sentiment_Analysis graph as the depenent variable. The table will visualize how many times a
day the CDC posted a positive, negative, or Nnutral tweet about COVID or Corona every day since December 1, 2019'''

# pulling the dates and sentiments from the TweetSentiment table 
def tweet_sentiment(cur = cur, conn = conn):
    cur.execute('SELECT date, sentiment FROM TweetSentiment')
    data = cur.fetchall()
    return data

# calculating the number of pos, neg, and neutral tweets per each day and putting it into dictionaries
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

# to remove duplicates from dates
def remove_duplicates(dates_lst):
    return list(dict.fromkeys(dates_lst))

#organizing the data into lists to insert into table
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

final_dates = remove_duplicates(reverse(dates))
# writing all of the calculations into a txt file 
with open("CDC_Twitter_Calculations.txt", "w") as output:
    output.write("The Average Number of Coronavirus-Related Tweets Posted by the CDC Each Week Starting with the Week of 12/1/2019 - 12/7/2019.\n")
    output.write("----------------------------------------------------------------------------------------------------------------------------\n")    
    for week in week_tweet_averages:
        count = week_tweet_averages[week]
        text = "During {}, the CDC released an average of {} coronavirus-related tweets.".format(week,count)
        output.write(str(text) + "\n")
    output.write("--------\n")
    output.write("The Sentiment Analysis -- Positive, Negative, and Neutral -- of Coronavirus-Related Tweets Posted by the CDC per Day.\n")
    output.write("----------------------------------------------------------------------------------------------------------------------------\n")
    for date in final_dates:
        try:
            pos = str(pos_tweet_count[date])
        except KeyError:
            pos = str(0)
        try:
            neg = str(neg_tweet_count[date])
        except KeyError:
            neg = str(0)
        try:
            neut = str(neutral_tweet_count[date])
        except KeyError:
            neut = str(0)
        text2 = "{} : {} positive tweets | {} negative tweets | {} neutral tweets.".format(date, pos, neg, neut)
        output.write(str(text2) + "\n")
    output.write("--------")
output.close()

#creating a graph of the sentiment analysis of the covid related tweets per day from the TweetSentiment table using matplotlib
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




# --- Visualization 3 --- Joint Visualization between CDC Tweets about COVID19 and Nasdaq Stock Prices in Since December 1, 2019 
'''Pulling data from the Nasdaq and TotalTweets tables to show the correlation between the 
Nasdaq prices and number of tweets released by the CDC regarding COVID or coronavirus 
everyday since December 1, 2019'''

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
