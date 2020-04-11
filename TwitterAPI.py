import twitter

# initialize api instance
twitter_api = twitter.Api(consumer_key='SVaUMV92pJosw7f95Fdif2Eqi',
                        consumer_secret='fTVKKnHpsA5WbCZanXFfyxbKh0QDDsjM7ZZpYv1jIhP0IzrhUE',
                        access_token_key='2249378049-VGOJPkBMvlaAb3m7xpySNoAIITwW274TucQq72x',
                        access_token_secret='KdedfOf5aruqkwPhCvYSPgjLgp6FKkezjpbiCbbxFMhZM')

# test authentication
print(twitter_api.VerifyCredentials())

def buildTestSet(search_keyword):
    try:
        tweets_fetched = twitter_api.GetSearch(search_keyword, count = 100)
        
        print("Fetched " + str(len(tweets_fetched)) + " tweets for the term " + search_keyword)
        
        return [{"text":status.text, "label":None} for status in tweets_fetched]
    except:
        print("Something went wrong...")
        return None

search_term = input("Enter a search keyword:")
testDataSet = buildTestSet(search_term)

print(testDataSet[0:4])
