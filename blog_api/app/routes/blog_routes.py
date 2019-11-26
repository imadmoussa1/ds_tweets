from app.api import db, log, parser, Resource, jsonify, request
from flask_jwt_extended import (JWTManager, create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

from ..models.blog import Blog
from ..models.user import User
from ..schema.blog_schema import blog_schema


parser.add_argument('title')


class BlogApi(Resource):
    @jwt_required
    def get(self, blog_id):
        blog = Blog.query.filter(Blog.id == blog_id).first()
        result = blog_schema.dump(blog)
        return jsonify(result)

    @jwt_required
    def post(self):
        request_json = request.get_json()
        title = request_json.get("title")
        description = request_json.get("description")
        content = request_json.get("content")
        user_name = get_jwt_identity()
        user = User.query.filter(User.user_name == user_name).first()
        blog = Blog.query.filter(Blog.title == title, Blog.user == user).first()
        if not blog:
            blog = Blog(title=title, description=description, content=content, active=True, user=user)
            db.session.add(blog)
            db.session.commit()
            log.info("New blog added by %s" % user_name)
            result = blog_schema.dump(blog)
            return jsonify(result)
        else:
            return {"message": "Blog exist"}, 401

    @jwt_required
    def put(self, blog_id):
        request_json = request.get_json()
        title = request_json.get("title")
        description = request_json.get("description")
        content = request_json.get("content")
        blog = Blog.query.filter(Blog.id == blog_id).first()
        if not blog:
            blog.title = title
            blog.description = description
            blog.content = content
            db.session.add(blog)
            db.session.commit()
            log.info("Blog %s updated by %s" %(title, user_name))
            result = blog_schema.dump(blog)
            return jsonify(result)
        else:
            return {"message": "Blog exist"}, 401
