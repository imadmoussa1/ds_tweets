from app.api import db, log, parser, Resource, jsonify, request, DataStoreClient
from flask_jwt_extended import (JWTManager, create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

from ..models.tweet import Tweet
from ..models.user import User
from ..schema.tweet_schema import tweet_schema


parser.add_argument('title')


class TweetApi(Resource):
    @jwt_required
    def get(self, title):
        tweet = DataStoreClient.tweets_collection().find_one({"title": title}, {'_id': False})
        result = tweet_schema.dump(tweet)
        return jsonify(result.data)

    @jwt_required
    def post(self):
        request_json = request.get_json()
        title = request_json.get("title")
        user_name = get_jwt_identity()
        tweet_json = {"title": title, "user": user_name}
        try:
            DataStoreClient.tweets_collection().update_one({'title': tweet_json['title']}, {"$set": tweet_json}, upsert=True)
            log.info("New tweet added by %s" % user_name)
        except Exception as e:
            log.error(e)
        result = tweet_schema.dump(tweet_json)
        return jsonify(result.data)


class SearchTweetApi(Resource):
    def get(self, title):
        tweet_api = TweetApi()
        tweet_api.get_tweets()
        blog = DataStoreClient.tweets_collection().find_one(
            {"title": title}, {'_id': False})
        result = tweet_schema.dump(blog)
        return jsonify(result.data)


class StreamTweetApi(Resource):
    def get(self, title):
        blog = DataStoreClient.tweets_collection().find_one({"title": title}, {'_id': False})
        result = tweet_schema.dump(blog)
        return jsonify(result.data)
