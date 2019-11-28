from app.api import db, log, parser, Resource, jsonify, request
from flask_jwt_extended import (JWTManager, create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

from ..models.trend import Trend
from ..models.user import User
from ..schema.trend_schema import trend_schema


parser.add_argument('title')


class TrendApi(Resource):
    @jwt_required
    def get(self, trend_id):
        trend = Trend.query.filter(Trend.id == trend_id).first()
        result = trend_schema.dump(trend)
        return jsonify(result)

    @jwt_required
    def post(self):
        request_json = request.get_json()
        title = request_json.get("title")
        description = request_json.get("description")
        content = request_json.get("content")
        user_name = get_jwt_identity()
        user = User.query.filter(User.user_name == user_name).first()
        trend = Trend.query.filter(Trend.title == title, Trend.user == user).first()
        if not trend:
            trend = Trend(title=title, description=description, content=content, active=True, user=user)
            db.session.add(trend)
            db.session.commit()
            log.info("New trend added by %s" % user_name)
            result = trend_schema.dump(trend)
            return jsonify(result)
        else:
            return {"message": "Trend exist"}, 401

    @jwt_required
    def put(self, trend_id):
        request_json = request.get_json()
        title = request_json.get("title")
        description = request_json.get("description")
        content = request_json.get("content")
        trend = Trend.query.filter(Trend.id == trend_id).first()
        if not trend:
            trend.title = title
            trend.description = description
            trend.content = content
            db.session.add(trend)
            db.session.commit()
            log.info("Trend %s updated by %s" %(title, user_name))
            result = trend_schema.dump(trend)
            return jsonify(result)
        else:
            return {"message": "Trend exist"}, 401
