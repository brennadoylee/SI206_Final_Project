import twitter

# initialize api instance
twitter_api = twitter.Api(consumer_key='SVaUMV92pJosw7f95Fdif2Eqi',
                        consumer_secret='fTVKKnHpsA5WbCZanXFfyxbKh0QDDsjM7ZZpYv1jIhP0IzrhUE',
                        access_token_key='2249378049-VGOJPkBMvlaAb3m7xpySNoAIITwW274TucQq72x',
                        access_token_secret='KdedfOf5aruqkwPhCvYSPgjLgp6FKkezjpbiCbbxFMhZM')

def buildTestSet(searchword):
    #searching for 100 of the latest tweets with the search word in it
    try:
        tweets_fetched = twitter_api.GetSearch(searchword, count = 100)
        
        print("Fetched " + str(len(tweets_fetched)) + " tweets for the term " + searchword)
        
        return [{"text":status.text, "label":None} for status in tweets_fetched]
    except:
        print("Something went wrong...")
        return None

search_term = input("Enter a search keyword:")
testDataSet = buildTestSet(search_term)

#print(testDataSet[0:4])

def buidTrainingSet(corpusFile, tweetDataFile):
    import csv
    import time
    
    corpus = []
    #here i am reading Niek Sanders’ csv Corpus file of over 5000 hand-classified tweets that have a key word, lable, and tweet ID 
    with open(corpusFile,'r') as csvfile:
        lineReader = csv.reader(csvfile,delimiter=',', quotechar="\"")
        for row in lineReader:
            corpus.append({"tweet_id":row[2], "label":row[1], "topic":row[0]})
    #to speed up the process        
    rate_limit = 180
    sleep_time = 900/rate_limit
    
    newdata = []
    #here i am apending the data from the corpus csv to newdata to later write it into a new csv file (only doing this once to store the data and draw from later)
    for tweet in corpus:
        try:
            status = twitter_api.GetStatus(tweet["tweet_id"])
            print("Tweet fetched" + status.text)
            tweet["text"] = status.text
            newdata.append(tweet)
            time.sleep(sleep_time) 
        except: 
            continue

    # now we write them to the empty CSV file
    with open(tweetDataFile,'w') as csvfile:
        linewriter = csv.writer(csvfile,delimiter=',',quotechar="\"")
        for tweet in newdata:
            try:
                linewriter.writerow([tweet["tweet_id"], tweet["text"], tweet["label"], tweet["topic"]])
            except Exception as e:
                print(e)
    return newdata

corpusFile = "corpus.csv"
tweetDataFile = "tweetDataFile.csv"

trainingData = buidTrainingSet(corpusFile, tweetDataFile)

# Now I am processing the tweets by extracting only the relevant words from each tweet using regex, nltk, and string methods

import re
from nltk.tokenize import word_tokenize
from string import punctuation 
from nltk.corpus import stopwords 

class ProcessingTweets:
    def __init__(self):
        #removing the "non-necessary" words in the english language from the tweets
        self._stopwords = set(stopwords.words('english') + list(punctuation) + ['AT_USER','URL'])
        
    def processTweets(self, list_of_tweets):
        processedTweets=[]
        for tweet in list_of_tweets:
            processedTweets.append((self.editTweet(tweet["text"]),tweet["label"]))
        return processedTweets
    
    def editTweet(self, tweet):
        tweet = tweet.lower() # convert text to lower-case
        tweet = re.sub(r'((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet) # remove URLs
        tweet = re.sub(r'@[^\s]+', 'AT_USER', tweet) # remove usernames
        tweet = re.sub(r'#([^\s]+)', r'\1', tweet) # remove the # in #hashtag
        tweet = word_tokenize(tweet) # remove repeated characters (helloooooooo into hello)
        return [word for word in tweet if word not in self._stopwords]
    
tweetProcessor = ProcessingTweets()
preprocessedTrainingSet = tweetProcessor.processTweets(trainingData)
preprocessedTestSet = tweetProcessor.processTweets(testDataSet)

#building the vocabulary

import nltk 

def buildVocabulary(preprocessedTrainingData):
    all_words = []
    # creating a list of all_words we have in the Training set and breaking it into words
    for tup in preprocessedTrainingData:
        all_words.extend(tup[0])

    #taking the list of  words and counting each words'frequency
    wordlist = nltk.FreqDist(all_words)
    word_features = wordlist.keys()
    
    return word_features

# comparing the tweets to the vocabulary

def extract_features(tweet):
    tweet_words=set(tweet)
    features={}
    for word in word_features:
        features['contains(%s)' % word]=(word in tweet_words)
    return features 


# extracting all of the features 
word_features = buildVocabulary(preprocessedTrainingSet)
trainingFeatures=nltk.classify.apply_features(extract_features,preprocessedTrainingSet)
NBayesClassifier=nltk.NaiveBayesClassifier.train(trainingFeatures)
NBResultLabels = [NBayesClassifier.classify(extract_features(tweet[0])) for tweet in preprocessedTestSet]


# get the majority vote
if NBResultLabels.count('positive') > NBResultLabels.count('negative'):
    print("Overall Positive Sentiment")
    print("Positive Sentiment Percentage = " + str(100*NBResultLabels.count('positive')/len(NBResultLabels)) + "%")
else: 
    print("Overall Negative Sentiment")
    print("Negative Sentiment Percentage = " + str(100*NBResultLabels.count('negative')/len(NBResultLabels)) + "%")