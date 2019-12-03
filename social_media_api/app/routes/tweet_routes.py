from app.api import db, log, config_env, parser, Resource, jsonify, request, DataStoreClient
from flask_jwt_extended import (JWTManager, create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

from ..models.user import User
from ..schema.tweet_schema import tweet_schema
from ..utils.celery_task import searching, cursor_searching, premuim_search, stream_tweets, remove_tweets_duplicate, export_tweets, extract_tweet_quote
parser.add_argument('name')


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
        collection_name = request.args.get('collection_name')
        task = export_tweets.apply_async(args=[fields, collection_name])
        return jsonify({"message": "start exporting"})

class ExtractQuoteTweetsApi(Resource):
    def get(self):
        collection_name = request.args.get('collection_name')
        task = extract_tweet_quote.apply_async(args=[collection_name])
        return jsonify({"message": "start exporting"})

class RemoveTweetsDuplicatesApi(Resource):
    def get(self):
        remove_tweets_duplicate.apply_async(args=[])
        return jsonify({"message": "start removing text tweets duplicate"})

