import sys
import json
import os
import time
import tweepy
import requests
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
        log.info(searchQuery)
        for tweet in tweepy.Cursor(self.api_connected().search, tweet_mode="extended", q=searchQuery, result_type="mixed", ).items(20000):
            if tweet:
                log.info(tweet._json['id_str'])
                DataStoreClient.tweets_collection().update_one({'tweet_id': tweet._json['id_str']}, {"$set": tweet._json}, upsert=True)

        log.info("Downloading max {0} tweets".format(maxTweets))

    def get_premuin_tweets(self, searchQuery, from_date, to_date):
        next_token = None
        endpoint = "https://api.twitter.com/1.1/tweets/search/30day/teweets.json"
        # endpoint = "https://api.twitter.com/1.1/tweets/search/fullarchive/teweets.json"
        headers = {"Authorization":"Bearer %s"%(Config.twitter_bearer_token()), "Content-Type": "application/json"}  

        while True:
            if next_token is None:
                data = '{"query": "#%s", "fromDate":"%s", "toDate":"%s"}'%(searchQuery, from_date, to_date)
            else:
                data = '{"query": "#%s", "fromDate":"%s", "toDate":"%s", "next":"%s"}'%(searchQuery, from_date, to_date, next_token)
            response = requests.post(endpoint,data=data.encode('utf-8'),headers=headers).json()
            if "error" in response:
                log.error(response['error'])
            if "results" in response:
                DataStoreClient.tweets_collection().insert_many(response['results'])
            if 'next' not in response:
                break
            next_token = response['next']
            time.sleep(1)
            # print(json.dumps(response['results'], indent = 2))

