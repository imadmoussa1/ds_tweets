from app.api import db, log, parser, Resource, jsonify, request
from flask_jwt_extended import (JWTManager, create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

from ..models.trend import Trend
from ..models.user import User
from ..schema.trend_schema import trend_schema


parser.add_argument('name')


class TrendApi(Resource):
  @jwt_required
  def get(self, trend_id):
    trend = Trend.query.filter(Trend.id == trend_id).first()
    result = trend_schema.dump(trend)
    return jsonify(result)

  @jwt_required
  def post(self):
    request_json = request.get_json()
    name = request_json.get("name")
    url = request_json.get("url")
    promoted_content = request_json.get("promoted_content")
    query = request_json.get("query")
    tweet_volume = request_json.get("tweet_volume")
    user_name = get_jwt_identity()
    user = User.query.filter(User.user_name == user_name).first()
    trend = Trend.query.filter(Trend.name == name, Trend.user == user).first()
    if not trend:
      trend = Trend(name=name, url=url, promoted_content=promoted_content, query=query, tweet_volume=tweet_volume, active=True, user=user)
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
    name = request_json.get("name")
    url = request_json.get("url")
    promoted_content = request_json.get("promoted_content")
    query = request_json.get("query")
    tweet_volume = request_json.get("tweet_volume")
    trend = Trend.query.filter(Trend.id == trend_id).first()
    user_name = get_jwt_identity()
    if not trend:
      trend.name = name
      trend.url = url
      trend.promoted_content = promoted_content
      trend.query = query
      trend.tweet_volume = tweet_volume
      db.session.add(trend)
      db.session.commit()
      log.info("Trend %s updated by %s" % (name, user_name))
      result = trend_schema.dump(trend)
      return jsonify(result)
    else:
      return {"message": "Trend exist"}, 401
