from flask_jwt_extended import (JWTManager, create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

from app.api import Resource, jsonify
from ..schema.blog_schema import blogs_schema
from ..models.blog import Blog
from ..models.user import User

class BlogListApi(Resource):
    @jwt_required
    def get(self):
        user_name = get_jwt_identity()
        user = User.query.filter(User.user_name == user_name).first()
        blogs = Blog.query.filter(Blog.active == True, Blog.user == user)
        result = blogs_schema.dump(blogs)
        return jsonify(result)
