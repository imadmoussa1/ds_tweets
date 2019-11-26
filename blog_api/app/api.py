import os
from datetime import datetime
from functools import wraps

from flask import Flask, request
from flask_cors import CORS
from flask.json import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_restplus import Resource, Api, reqparse
from flask_jwt_extended import (JWTManager, create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
from flask_jwt_extended import exceptions as jwt_extended_exceptions
from flask_marshmallow import Marshmallow
from passlib.hash import pbkdf2_sha256

from app.utils.config import Config
from app.utils.logger import Logger
from app.utils.data_store_client import DataStoreClient

sha256 = pbkdf2_sha256
request = request
log = Logger.log(__name__)
DataStoreClient = DataStoreClient
config_env = Config()
datetime = datetime
Resource = Resource
parser = reqparse.RequestParser()
jsonify = jsonify

jwt = JWTManager()
db = SQLAlchemy()
bcrypt = Bcrypt()
api = Api()
ma = Marshmallow()


@api.errorhandler(jwt_extended_exceptions.FreshTokenRequired)
def handle_expired_error():
    return {"message": "Token has expired!"}, 401


@api.errorhandler(jwt_extended_exceptions.RevokedTokenError)
def revoked_token_callback():
    return {"message": "Token has been revoked!"}, 402


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    from .models.revoked_token import RevokedToken
    jti = decrypted_token["jti"]
    return RevokedToken.is_jti_blacklisted(jti)


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        from .models.user import User
        auth = request.authorization
        if auth:
            current_user = User.find_by_username(auth.username)
            if not current_user:
                return {"message": "User {} doesn\"t exist".format(auth.username)}, 401
            if not current_user.is_admin:
                return {"message": "User {} not admin.".format(auth.username)}, 401
            if User.verify_hash(auth.password, current_user.password):
                access_token = create_access_token(identity=auth.username)
                refresh_token = create_refresh_token(identity=auth.password)
                return {"message": "Logged in as {}".format(current_user.user_name), "access_token": access_token, "refresh_token": refresh_token}, 200
            else:
                return {"message": "Wrong credentials"}, 401
        return {"message": "Could not verify your login!"}, 401, {"WWW-Authenticate": "Basic realm=\"Login required\""}

    return decorated


def create_app():
    from .models.user import User
    from .models.blog import Blog
    from .models.revoked_token import RevokedToken

    security = ["basicAuth", "apiKey"]
    authorizations = {
        "basicAuth": {
            "type": "basic",
            "in": "header",
            "name": "Authorization"
        },
        "apiKey": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization"
        },
    }

    app = Flask(__name__, instance_relative_config=True)
    app.config.update(
        BASEDIR=os.path.abspath(os.path.dirname(__file__)),
        JWT_TOKEN_LOCATION="headers",
        JWT_SECRET_KEY=config_env.jwt_secret_key(),
        JWT_BLACKLIST_ENABLED=True,
        JWT_BLACKLIST_TOKEN_CHECKS=["access", "refresh"],
        SQLALCHEMY_DATABASE_URI=config_env.sqlalchemy_database_uri(),
        SQLALCHEMY_TRACK_MODIFICATIONS=True,
        SECRET_KEY=config_env.secret_key(),
        DEBUG=config_env.debug(),
        PROPAGATE_EXCEPTIONS=True
    )
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    # cors = CORS(app, supports_credentials=True)

    jwt.init_app(app)
    db.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    app.app_context().push()

    db.create_all(app=app)
    db.session.commit()
    # Create index in mongodb collection
    DataStoreClient.create_index()
    # import alembic.config
    # from alembic import command
    # alembic_cfg = alembic.config.Config("alembic.ini")
    # command.upgrade(alembic_cfg, "head")

    from .routes.blog_routes import BlogApi
    api.add_resource(BlogApi, '/api/blog/<blog_id>')
    api.add_resource(BlogApi, '/api/blog')

    from .routes.blog_list_routes import BlogListApi
    api.add_resource(BlogListApi, '/api/blogs')

    from .routes.blog_draft_routes import BlogDraftApi
    api.add_resource(BlogDraftApi, '/api/drafts/<title>')
    api.add_resource(BlogDraftApi, '/api/drafts')

    from .routes.user_routes import UserLogin
    api.add_resource(UserLogin, '/api/login')

    from .routes.user_routes import UserRegister
    api.add_resource(UserRegister, '/api/register')

    from .routes.user_routes import UserTokenRefresh
    api.add_resource(UserTokenRefresh, '/api/token_refresh')

    from .routes.user_routes import UserLogoutRefresh
    api.add_resource(UserLogoutRefresh, '/api/logout_refresh')

    from .routes.user_routes import UserLogoutAccess
    api.add_resource(UserLogoutAccess, '/api/logout_access')

    api.init_app(app=app, authorizations=authorizations, security=security, version="0.0.1", description="REST Template")
    jwt._set_error_handler_callbacks(api)

    return app
