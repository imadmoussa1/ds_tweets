import sys
import json
import os
import time
import tweepy
import requests
from pymongo import UpdateOne, InsertOne
from pymongo.errors import BulkWriteError
from .config import Config
from tweepy import OAuthHandler
from .data_store_client import DataStoreClient
from .tweet_stream_listener import TweetStreamListener
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

    def stream_tweets(self, query):
        listener = TweetStreamListener()
        stream = tweepy.Stream(self.api_connected().auth, listener)
        stream.filter(track=query, filter_level="meduim", is_async=True)

    def get_tweets_cursor(self, search_query):
        tweet_count = 0
        log.info("Start searching using cursor")
        db_query = []
        db_query_insert= []
        for tweet in tweepy.Cursor(self.api_connected().search, tweet_mode="extended", q=search_query, result_type="mixed").items(200000):
            if tweet:
                tweet_count += 1
                db_query.append(UpdateOne({'id_str': tweet._json['id_str']}, {"$set": tweet._json}, upsert=True))
                db_query_insert.append(InsertOne(tweet._json))
                time.sleep(1)
        try:
            bulk_update = DataStoreClient.tweets_collection().bulk_write(db_query)
            log.info("Insert update: %s"%bulk_update.bulk_api_result)
            bulk_insert = DataStoreClient.tweets_collection('tweets').bulk_write(db_query_insert)
            log.info("Insert result: %s"%bulk_insert.bulk_api_result)
        except BulkWriteError as bwe:
            log.error(bwe.details)
        log.info(tweet_count)

    def get_tweets(self, search_query):
        maxTweets = 10000000 # Some arbitrary large number
        tweetsPerQry = 100 # this is the max the API permits
        sinceId = None
        max_id = -1
        tweetCount = 0
        log.info("Start searching using old method")
        db_query = []
        db_query_insert= []
        while tweetCount < maxTweets:
            try:
                if max_id <= 0:
                    if not sinceId:
                        new_tweets = self.api_connected().search(q=search_query, tweet_mode="extended", result_type="mixed", count=tweetsPerQry)
                    else:
                        new_tweets = self.api_connected().search(q=search_query, tweet_mode="extended", result_type="mixed", count=tweetsPerQry, since_id=sinceId)
                else:
                    if not sinceId:
                        new_tweets = self.api_connected().search(q=search_query, tweet_mode="extended", result_type="mixed", count=tweetsPerQry, max_id=str(max_id - 1))
                    else:
                        new_tweets = self.api_connected().search(q=search_query, tweet_mode="extended", result_type="mixed", count=tweetsPerQry, max_id=str(max_id - 1), since_id=sinceId)
                if not new_tweets:
                    log.info("No more tweets found")
                    break
                for tweet in new_tweets:
                    db_query.append(UpdateOne({'id_str': tweet._json['id_str']}, {"$set": tweet._json}, upsert=True))
                    db_query_insert.append(InsertOne(tweet._json))
                    # log.info(tweet._json)
                tweetCount += len(new_tweets)
                log.info("Downloading max {0} tweets".format(tweetCount))
                sinceId = new_tweets[-1].id
            except tweepy.TweepError as e:
                log.info("some error : " + str(e))
                continue
        try:
            bulk_update = DataStoreClient.tweets_collection().bulk_write(db_query)
            log.info("Insert update: %s"%bulk_update.bulk_api_result)
            bulk_insert = DataStoreClient.tweets_collection('tweets').bulk_write(db_query_insert)
            log.info("Insert result: %s"%bulk_insert.bulk_api_result)
        except BulkWriteError as bwe:
            log.error(bwe.details)

    def get_premuin_tweets(self, search_query, from_date, to_date):
        next_token = None
        endpoint = "https://api.twitter.com/1.1/tweets/search/30day/teweets.json"
        # endpoint = "https://api.twitter.com/1.1/tweets/search/fullarchive/teweets.json"
        headers = {"Authorization":"Bearer %s"%(Config.twitter_bearer_token()), "Content-Type": "application/json"}  
        db_query = []
        while True:
            if next_token is None:
                data = '{"query": "#%s", "fromDate":"%s", "toDate":"%s"}'%(search_query, from_date, to_date)
            else:
                data = '{"query": "#%s", "fromDate":"%s", "toDate":"%s", "next":"%s"}'%(search_query, from_date, to_date, next_token)
            response = requests.post(endpoint,data=data.encode('utf-8'),headers=headers).json()
            if "error" in response:
                log.error(response['error'])
            if "results" in response:
                # DataStoreClient.tweets_collection().update_one({'id_str': tweet._json['id_str']}, {"$set": tweet._json}, upsert=True)
                DataStoreClient.tweets_collection('tweets').insert_many(response['results'])
                for tweet in response['results']:
                    db_query.append(UpdateOne({'id_str': tweet['id_str']}, {"$set": tweet}, upsert=True))
            if 'next' not in response:
                break
            next_token = response['next']
            time.sleep(1)
            # print(json.dumps(response['results'], indent = 2))
        try:
            bulk_insert = DataStoreClient.tweets_collection().bulk_write(db_query)
            log.info("Insert result: %s"%bulk_insert.bulk_api_result)
        except BulkWriteError as bwe:
            log.error(bwe.details)
