import sys
import json
import os
import tweepy
from .config import Config
from tweepy import OAuthHandler
from .data_store_client import DataStoreClient
from .logger import Logger

log = Logger.log(__name__)


class TweetApi:

    def api_connected(self):
        auth = OAuthHandler(Config.twitter_consumer_key(), Config.twitter_consumer_secret())
        auth.set_access_token(Config.twitter_access_token(), Config.twitter_access_token_secret())
        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        if not api:
            sys.exit(-1)
        return api

    def get_tweets(self, searchQuery):
        maxTweets = 10000000  # Some arbitrary large number
        tweetsPerQry = 100  # this is the max the API permits

        for tweet in tweepy.Cursor(self.api_connected().search, tweet_mode="extended", q=searchQuery, lang="en", locale="en").items(10):
            print(tweet)
            if tweet:
                DataStoreClient.tweets_collection().update_one({'tweet_id': tweet._json['id_str']}, {"$set": tweet._json}, upsert=True)

        log.info("Downloading max {0} tweets".format(maxTweets))

