from app.api import db, log, config_env, parser, Resource, jsonify, request, DataStoreClient
from flask_jwt_extended import (JWTManager, create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

from ..models.user import User

# from ..utils.celery_task import searching, cursor_searching, premuim_search, stream_tweets, remove_tweets_duplicate, export_tweets, extract_tweet_quote
parser.add_argument('name')


class FacebookApi(Resource):
    def get(self):
        import facebook
        fb_id = request.args.get('fb_id')
        fields = request.args.get('fields')
        graph = facebook.GraphAPI(access_token=config_env.facebook_access_token(), version="3.1")
        post = graph.get_object(id=fb_id, fields=fields)
        log.info(post)
        # searching.apply_async(args=[fb_id])
        # cursor_searching.apply_async(args=[fb_id])
        return jsonify({"message": "Start searching"})
