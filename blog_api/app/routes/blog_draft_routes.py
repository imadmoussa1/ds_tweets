from app.api import db, log, parser, Resource, jsonify, request, DataStoreClient
from flask_jwt_extended import (JWTManager, create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

from ..models.blog import Blog
from ..models.user import User
from ..schema.blog_draft_schema import blog_draft_schema


parser.add_argument('title')


class BlogDraftApi(Resource):
    @jwt_required
    def get(self, title):
        blog = DataStoreClient.blog_drafts_collection().find_one({"title": title}, {'_id': False})
        result = blog_draft_schema.dump(blog)
        return jsonify(result.data)

    @jwt_required
    def post(self):
        request_json = request.get_json()
        title = request_json.get("title")
        description = request_json.get("description")
        content = request_json.get("content")
        user_name = get_jwt_identity()
        blog_json = {"title": title, "description": description, "content": content, "user": user_name}
        try:
            DataStoreClient.blog_drafts_collection().update_one({'title': blog_json['title']}, {"$set": blog_json}, upsert=True)
            log.info("New draft blog added by %s" % user_name)
        except Exception as e:
            log.error(e)
        result = blog_draft_schema.dump(blog_json)
        return jsonify(result.data)
