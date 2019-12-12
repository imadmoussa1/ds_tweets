import sys
import json
import os
import time
import tweepy
import requests
import datetime
from pymongo import UpdateOne, InsertOne
from pymongo.errors import BulkWriteError
from .config import Config
from tweepy import OAuthHandler
from .data_store_client import DataStoreClient, modify_tweet
from .tweet_stream_listener import TweetStreamListener
from ..models.trend import Trend
from app.api import log, db


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

  def get_tweets_cursor(self, search_query=None, screen_name=None):
    tweet_count = 0
    db_query = []
    db_query_insert = []
    if screen_name:
      log.info("Start user %s searching using cursor"%screen_name)
      tweets = tweepy.Cursor(self.api_connected().user_timeline, tweet_mode="extended", screen_name=screen_name, result_type="mixed").items()
    if search_query:
      log.info("Start query %s searching using cursor"%search_query)
      tweets = tweepy.Cursor(self.api_connected().search, tweet_mode="extended", q="#%s" % search_query, result_type="mixed").items(200000)
    for tweet in tweets:
      if tweet:
        tweet_count += 1
        db_query.append(UpdateOne({'id_str': tweet._json['id_str']}, {"$set": modify_tweet(tweet._json)}, upsert=True))
        db_query_insert.append(InsertOne(modify_tweet(tweet._json)))
        time.sleep(1)
    try:
      bulk_update = DataStoreClient.tweets_collection().bulk_write(db_query)
      log.info("Insert update: %s" % bulk_update.bulk_api_result)
      bulk_insert = DataStoreClient.tweets_collection('tweets').bulk_write(db_query_insert)
      log.info("Insert result: %s" % bulk_insert.bulk_api_result)
    except BulkWriteError as bwe:
      log.error(bwe.details)
    log.info(tweet_count)

  def get_tweets(self, search_query):
    try:
      log.info("Start searching using old method")
      db_query = []
      db_query_insert = []
      alltweets = []
      new_tweets = self.api_connected().search(q=search_query, tweet_mode="extended", result_type="mixed", count=200)
      alltweets.extend(new_tweets)
      oldest = alltweets[-1].id - 1
      while len(new_tweets) > 0:
        log.info("getting %s tweets before %s" % (search_query, oldest))
        for tweet in new_tweets:
          db_query.append(UpdateOne({'id_str': tweet._json['id_str']}, {"$set": modify_tweet(tweet._json)}, upsert=True))
          db_query_insert.append(InsertOne(modify_tweet(tweet._json)))
        new_tweets = self.api_connected().search(q=search_query, tweet_mode="extended", result_type="mixed", count=200, max_id=oldest)
        #all subsiquent requests use the max_id param to prevent duplicates
        alltweets.extend(new_tweets)
        #update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1
        log.info("...%s, %s tweets downloaded so far" % (len(alltweets), search_query))
        try:
          bulk_update = DataStoreClient.tweets_collection().bulk_write(db_query)
          log.info("Insert update: %s" % bulk_update.bulk_api_result)
          bulk_insert = DataStoreClient.tweets_collection('tweets').bulk_write(db_query_insert)
          log.info("Insert result: %s" % bulk_insert.bulk_api_result)
        except BulkWriteError as bwe:
          log.error(bwe.details)
    except tweepy.TweepError as e:
      log.error("some error : " + str(e))

  def get_user_tweets(self, screen_name):
    log.info("Start user: %s tweets search" % screen_name)
    db_query = []
    db_query_insert = []
    alltweets = []
    # try:
    new_tweets = self.api_connected().user_timeline(screen_name=screen_name, tweet_mode="extended", result_type="mixed", count=200)
    alltweets.extend(new_tweets)
    if len(alltweets) > 190:
      oldest = alltweets[-1].id-1
      while len(new_tweets) > 0:
        log.info("getting %s tweets before %s" % (screen_name, oldest))
        for tweet in new_tweets:
          db_query.append(UpdateOne({'id_str': tweet._json['id_str']}, {"$set": modify_tweet(tweet._json)}, upsert=True))
          db_query_insert.append(InsertOne(modify_tweet(tweet._json)))
        new_tweets = self.api_connected().user_timeline(screen_name=screen_name, tweet_mode="extended", result_type="mixed", count=200, max_id=oldest)
        alltweets.extend(new_tweets)
        oldest = alltweets[-1].id-1
        log.info("...%s, %s tweets downloaded so far" % (len(alltweets), screen_name))
    elif len(alltweets) > 1:
      oldest = alltweets[-1].id-1
      for tweet in alltweets:
        db_query.append(UpdateOne({'id_str': tweet._json['id_str']}, {"$set": modify_tweet(tweet._json)}, upsert=True))
        db_query_insert.append(InsertOne(modify_tweet(tweet._json)))
    elif len(alltweets) > 0:
      for tweet in alltweets:
        db_query.append(UpdateOne({'id_str': tweet._json['id_str']}, {"$set": modify_tweet(tweet._json)}, upsert=True))
        db_query_insert.append(InsertOne(modify_tweet(tweet._json)))
    try:
      bulk_update = DataStoreClient.tweets_collection(screen_name).bulk_write(db_query)
      log.info("Insert update: %s" % bulk_update.bulk_api_result)
      bulk_insert = DataStoreClient.tweets_collection('%s_raw' % screen_name).bulk_write(db_query_insert)
      log.info("Insert result: %s" % bulk_insert.bulk_api_result)
    except BulkWriteError as bwe:
      log.error(bwe.details)
    # except tweepy.TweepError as e:
    #   log.error("some error : " + str(e))

  def get_premuin_tweets(self, search_query, from_date, to_date):
    next_token = None
    endpoint = "https://api.twitter.com/1.1/tweets/search/30day/teweets.json"
    # endpoint = "https://api.twitter.com/1.1/tweets/search/fullarchive/teweets.json"
    headers = {"Authorization": "Bearer %s" % (Config.twitter_bearer_token()), "Content-Type": "application/json"}
    db_query = []
    while True:
      if next_token is None:
        data = '{"query": "#%s", "fromDate":"%s", "toDate":"%s"}' % (search_query, from_date, to_date)
      else:
        data = '{"query": "#%s", "fromDate":"%s", "toDate":"%s", "next":"%s"}' % (search_query, from_date, to_date, next_token)
      response = requests.post(endpoint, data=data.encode('utf-8'), headers=headers).json()
      if "error" in response:
        log.error(response['error'])
      if "results" in response:
        # DataStoreClient.tweets_collection().update_one({'id_str': tweet._json['id_str']}, {"$set": tweet._json}, upsert=True)
        # DataStoreClient.tweets_collection('tweets').insert_many(response['results'])
        for tweet in response['results']:
          db_query.append(UpdateOne({'id_str': tweet['id_str']}, {"$set": modify_tweet(tweet)}, upsert=True))
      if 'next' not in response:
        break
      next_token = response['next']
      time.sleep(1)
      # print(json.dumps(response['results'], indent = 2))
    try:
      bulk_insert = DataStoreClient.tweets_collection().bulk_write(db_query)
      log.info("Insert result: %s" % bulk_insert.bulk_api_result)
    except BulkWriteError as bwe:
      log.error(bwe.details)

  def get_trends_request(self, location_woeid):
    # 23424873
    log.info("Get trends")
    endpoint = "https://api.twitter.com/1.1/trends/place.json"
    headers = {"Authorization": "Bearer %s" % (Config.twitter_bearer_token()), "Content-Type": "application/json"}
    params = {"id": location_woeid}
    response = requests.get(endpoint, params=params, headers=headers).json()
    # log.info(response)
    if "errors" in response:
      log.error(response)
    else:
      trends = response[0]['trends']
      location = response[0]['locations'][0]['name']
      as_of = datetime.datetime.strptime(response[0]['as_of'], "%Y-%m-%dT%H:%M:%SZ")
      created_at = datetime.datetime.strptime(response[0]['created_at'], "%Y-%m-%dT%H:%M:%SZ")
      date = {"as_of": as_of, "created_at": created_at}
      result = [dict(item, **date) for item in trends]
      DataStoreClient.trends_collection(location).insert_many(result)
      for trend_data in trends:
        trend = Trend.query.filter(Trend.name == trend_data['name']).first()
        if not trend:
          trend = Trend(name=trend_data['name'],
                        url=trend_data['url'],
                        promoted_content=trend_data['promoted_content'],
                        trend_query=trend_data['query'],
                        tweet_volume=trend_data['tweet_volume'],
                        as_of=as_of,
                        woeid=location_woeid,
                        updated=created_at)
          db.session.add(trend)
          db.session.commit()
        else:
          trend.name = trend_data['name']
          trend.url = trend_data['url']
          trend.trend_query = trend_data['query']
          trend.promoted_content = trend_data['promoted_content']
          trend.tweet_volume = trend_data['tweet_volume']
          trend.as_of = as_of
          trend.woeid = location_woeid
          trend.updated = created_at
          db.session.commit()
        log.info("Adding new trend")
