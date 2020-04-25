import tweepy
from textblob import TextBlob
import csv


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
    outtweets = [[tweet.id_str, tweet.created_at, tweet.text.encode("utf-8"), tweet_analysis(str(tweet.text.encode("utf-8")))] for tweet in alltweets if "#COVID" in str(tweet.text.encode("utf-8"))]

    #write the csv  
    with open('CDC_tweets.csv' , 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["id","created_at","text", "sentiment"])
        writer.writerows(outtweets)

    pass

if __name__ == '__main__':
    #pass in the username of the account you want to download
    get_all_tweets(screenname)

