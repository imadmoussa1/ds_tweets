from app.api import db, log, config_env, parser, Resource, jsonify, request, DataStoreClient, tweet_search, tweet_stream, celery
from flask_jwt_extended import (JWTManager, create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

from ..models.user import User
from ..schema.tweet_schema import tweet_schema
import csv

parser.add_argument('title')


class TweetApi(Resource):
    @jwt_required
    def get(self, title):
        tweet = DataStoreClient.tweets_collection().find_one(
            {"title": title}, {'_id': False})
        result = tweet_schema.dump(tweet)
        return jsonify(result.data)

    @jwt_required
    def post(self):
        request_json = request.get_json()
        title = request_json.get("title")
        user_name = get_jwt_identity()
        tweet_json = {"title": title, "user": user_name}
        try:
            DataStoreClient.tweets_collection().update_one(
                {'title': tweet_json['title']}, {"$set": tweet_json}, upsert=True)
            log.info("New tweet added by %s" % user_name)
        except Exception as e:
            log.error(e)
        result = tweet_schema.dump(tweet_json)
        return jsonify(result.data)


class SearchTweetApi(Resource):
    def get(self):
        query = request.args.get('query')
        searching.apply_async(args=[query])
        cursor_searching.apply_async(args=[query])
        return jsonify({"message": "Start searching"})


class PremiumSearchTweetApi(Resource):
    def get(self):
        query = request.args.get('query')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        task = premuim_search.apply_async(args=[query, from_date, to_date])
        return jsonify({"message": "Start premuim searching"})


class StreamTweetApi(Resource):
    def get(self):
        query = request.args.get('query')
        stream_tweets.apply_async(args=[query])
        return jsonify({"message": "start stream"})


class ExportTweetsApi(Resource):
    def get(self):
        fields = request.args.get('fields')
        task = export_tweets.apply_async(args=[fields])
        return jsonify({"message": "start exporting"})


@celery.task(name="tweets_search_task")
def searching(query):
    try:
        log.info("start searching for %s" % (query))
        search = tweet_search()
        search.get_tweets("#%s" % query)
        log.info("done searching")
    except Exception as e:
        log.error(e)

@celery.task(name="tweets_cursor_search_task")
def cursor_searching(query):
    try:
        log.info("start cursor searching for %s" % (query))
        search = tweet_search()
        search.get_tweets_cursor("#%s" % query)
        log.info("done searching")
    except Exception as e:
        log.error(e)

@celery.task(name="premuim_tweets_search_task")
def premuim_search(query, from_date, to_date):
    try:
        search = tweet_search()
        search.get_premuin_tweets(query, from_date, to_date)
    except Exception as e:
        log.error(e)

@celery.task(name="stream_tweets_task")
def stream_tweets(query):
    try:
        tracks_filter = ["#%s"%query]
        search = tweet_search()
        search.stream_tweets(tracks_filter)
    except Exception as e:
        log.error(e)

@celery.task(name="export_tweets")
def export_tweets(fields):
    # print("start")
    # for a in DataStoreClient.tweets_collection('tweets').find({}, {'_id': 0}):
    #     # print(a)
    #     DataStoreClient.tweets_collection().update_one({'id_str': a['id_str']}, {"$set": a}, upsert=True)
    # print("start1")
    # for a in DataStoreClient.tweets_collection('tweets_2').find({}, {'_id': 0}):
    #     # print(a)
    #     DataStoreClient.tweets_collection().update_one({'id_str': a['id_str']}, {"$set": a}, upsert=True)
    # print("end")
    try:
        cursor = DataStoreClient.tweets_collection().find(
            {'$or': [
                {'retweet_count': {'$gt': 10}},
                {'favorite_count': {'$gt': 10}}
            ]},
            {
            'text': 1,
            'full_text': 1,
            'reply_count': 1,
            'retweet_count': 1,
            'favorite_count': 1,
            'source': 1,
            '_id': 0,
            'id': 1
        })

        fields = ['text', 'full_text', 'reply_count', 'retweet_count', 'favorite_count', 'source', 'id']
        with open('export/%s.csv' % config_env.tweets_collection_name(), 'w') as outfile:
            write = csv.DictWriter(outfile, fieldnames=fields)
            write.writeheader()
            for record in cursor:
                write.writerow(record)
    except Exception as e:
        log.error(e)
