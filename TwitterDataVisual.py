from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import auth_twitter
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


#  Client
class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets


# Authentication
class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(auth_twitter.CONSUMER_KEY, auth_twitter.CONSUMER_SECRET)
        auth.set_access_token(auth_twitter.ACCESS_TOKEN, auth_twitter.ACCESS_TOKEN_SECRET)
        return auth


# Streaming service for twitter
class TwitterStreamer():
    """
    Class for streaming and processing live tweets.
    """

    def __init__(self):
        self.twitter_autenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        # This handles Twitter authetification and the connection to Twitter Streaming API
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_autenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)

        # This line filter Twitter Streams to capture data by the keywords:
        stream.filter(track=hash_tag_list)


# Listener for Twitter Stream
class TwitterListener(StreamListener):
    """
    This is a basic listener that just prints received tweets to stdout.
    """
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on_data %s" % str(e))
        return True

    def on_error(self, status):
        if status == 420:
            # Returning False on_data method in case rate limit occurs.
            return False
        print(status)

# Content Analyzer
class TweetAnalyzer():
    """
    Functionality for analyzing and categorizing content from tweets.
    """

    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['tweets'])

        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])

        return df


if __name__ == '__main__':
    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()

    api = twitter_client.get_twitter_client_api()

    tweets = api.user_timeline(screen_name="realDonaldTrump", count=20)


    df = tweet_analyzer.tweets_to_data_frame(tweets)


    print(np.mean(df['len']))     # Average length over tweets #
    print(np.max(df['likes'])) # Most Liked Tweet's number of likes #
    print(np.max(df['retweets']))  # Number of re-tweets for most re-tweeted tweet #

    # print(df.head(10))

## Remove comment based on requirement ##

    #  Number of Likes in terms of time series
    # time_likes = pd.Series(data=df['len'].values, index=df['date'])
    # time_likes.plot(figsize=(16, 4), color='r')
    # plt.show()

    # Number of retweets in terms of time series
    # time_retweets = pd.Series(data=df['retweets'].values, index=df['date'])
    # time_retweets.plot(figsize=(16, 4), color='r')
    # plt.show()

    # Layered Time Series for both likes and retweets:
    time_likes = pd.Series(data=df['likes'].alues, index=df['date'])
    time_likes.plot(figsize=(16, 4), label="likes", legend=True)

    time_retweets = pd.Series(data=df['retweets'].values, index=df['date'])
    time_retweets.plot(figsize=(16, 4), label="retweets", legend=True)

    plt.show()