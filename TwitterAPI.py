import tweepy
from textblob import TextBlob
import csv
import matplotlib.pyplot as plt
import json
import sqlite3
import os
import time


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

    #initializing a list to hold all the tweepy Tweets
    alltweets = []  

    # make the initial request for most recent tweets (200 is the maximum allowed count)
    
    new_tweets = api.user_timeline(screen_name = screenname ,count=200)

    # getting tweets from the CDC
    screen_name = "CDC"

    #save most recent tweets
    alltweets.extend(new_tweets)

    #save the id of the second oldest tweet
    oldest = alltweets[-1].id - 1

    # keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
        print("getting tweets before {}".format(oldest))

        # using the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name = screenname,count=200,max_id=oldest)

        #saving the most recent tweets
        alltweets.extend(new_tweets)

        #update the id of the second oldest tweet
        oldest = alltweets[-1].id - 1

        print("...{} tweets downloaded so far".format(len(alltweets)))

    #organizing the data and calling tweet_analysis to get the sentiment 

    outtweets = [[str(tweet_analysis(str(tweet.text.encode("utf-8")))), str(tweet.created_at.date()), str(tweet.id_str), str(tweet.text.encode("utf-8"))] for tweet in alltweets if "#COVID" in str(tweet.text.encode("utf-8"))]
    return outtweets



# #setting up database
# path = os.path.dirname(os.path.abspath(__file__))
# conn = sqlite3.connect(path + '/' + "finalprojectdatabase.db")
# cur = conn.cursor()

all_tweets = get_all_tweets(screenname)
# count = 0
# cur.execute("DROP TABLE IF EXISTS Twitter")
# cur.execute("CREATE TABLE IF NOT EXISTS Twitter(sentiment TEXT PRIMARY KEY, date TEXT, id TEXT , tweet TEXT)")
# conn.commit()
# for tweet in all_tweets:
#     count += 1
#     cur.execute("INSERT OR IGNORE INTO Twitter VALUES (?, ?, ?, ?)", (tweet[0], tweet[1], tweet[2],tweet[3]))
#     conn.commit()
#     if count % 10 == 0:
#         print('Pausing for a bit...')
#         time.sleep(5)


#february, march, and april 2020 sentiment counts
feb_pos_count = 0
feb_neg_count = 0
feb_neutral_count = 0
mar_pos_count = 0
mar_neg_count = 0
mar_neutral_count = 0
apr_pos_count = 0
apr_neg_count = 0
apr_neutral_count = 0
for tweet in all_tweets:
    date_vals = tweet[1].split("-")
    if date_vals[1] == "02":
        sentiment = tweet[0]
        if sentiment == "Positive":
            feb_pos_count += 1
        if sentiment == "Negative":
            feb_neg_count += 1
        if sentiment == "Neutral":
            feb_neutral_count += 1
    if date_vals[1] == "03":
        sentiment = tweet[0]
        if sentiment == "Positive":
            mar_pos_count += 1
        if sentiment == "Negative":
            mar_neg_count += 1
        if sentiment == "Neutral":
            mar_neutral_count += 1
    if date_vals[1] == "03":
        sentiment = tweet[0]
        if sentiment == "Positive":
            apr_pos_count += 1
        if sentiment == "Negative":
            apr_neg_count += 1
        if sentiment == "Neutral":
            apr_neutral_count += 1

#creating line graphs with matplot
pos_sentiment = [feb_pos_count, mar_pos_count, apr_pos_count]
neg_sentiment = [feb_neg_count, mar_neg_count, apr_neg_count]
neutral_sentiment = [feb_neutral_count, mar_neutral_count, apr_neutral_count]

#positive graph
date = ["February 2020", "March 2020", "April 2020"]
fig, ax = plt.subplots()
ax.plot(date, pos_sentiment)
ax.set_xlabel("Month")
ax.set_ylabel("Number of Tweets")
ax.set_title("Number of POSITIVE Tweets")
fig.savefig("positive_sentiment.png")
plt.show()

#negative graph
fig, ax = plt.subplots()
ax.plot(date, neg_sentiment)
ax.set_xlabel("Month")
ax.set_ylabel("Number of Tweets")
ax.set_title("Number of NEGATIVE Tweets")
fig.savefig("negative_sentiment.png")
plt.show()

#neutral graph
fig, ax = plt.subplots()
ax.plot(date, neutral_sentiment)
ax.set_xlabel("Month")
ax.set_ylabel("Number of Tweets")
ax.set_title("Number of Neutral Tweets")
fig.savefig("neutral_sentiment.png")
plt.show()