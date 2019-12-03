from app.api import db, api, auth_required, Resource, sha256, request, log
from flask_jwt_extended import (JWTManager, create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

from ..models.revoked_token import RevokedToken
from ..models.user import User


class UserLogin(Resource):
    @api.doc(security="basicAuth")
    @auth_required
    def get(self):
        pass


class UserRegister(Resource):
    def post(self):
        try:
            request_json = request.get_json()
            email = request_json.get('email')
            user_name = request_json.get('user_name')
            password = str(sha256.hash(request_json.get('password')))
            user = User.query.filter(User.email == email).first()
            if not user:
                user = User(user_name=user_name, email=email, password=password, is_admin=True)
                db.session.add(user)
                db.session.commit()
                log.info("Adding new user")
                return {"message": "Registered"}, 200
            else:
                return {"message": "User exist"}, 401
        except:
            return {"message": "Something went wrong"}, 500


class UserTokenRefresh(Resource):
    @jwt_refresh_token_required
    def get(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {"access_token": access_token}, 200


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def get(self):
        jti = get_raw_jwt()["jti"]
        try:
            revoked_token = RevokedToken(jti=jti)
            revoked_token.add()
            return {"message": "Refresh token has been revoked!"}, 200
        except:
            return {"message": "Something went wrong"}, 500


class UserLogoutAccess(Resource):
    @jwt_required
    def get(self):
        jti = get_raw_jwt()["jti"]
        try:
            revoked_token = RevokedToken(jti=jti)
            revoked_token.add()
            return {"message": "Access token has been revoked!"}, 200
        except:
            return {"message": "Something went wrong"}, 500
