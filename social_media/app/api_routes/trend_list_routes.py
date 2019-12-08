from flask_jwt_extended import (JWTManager, create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

from app.api import Resource, jsonify
from ..schema.trend_schema import trends_schema
from ..models.trend import Trend
from ..models.user import User


class TrendListApi(Resource):
  @jwt_required
  def get(self):
    user_name = get_jwt_identity()
    user = User.query.filter(User.user_name == user_name).first()
    trends = Trend.query.filter(Trend.active == True, Trend.user == user)
    result = trends_schema.dump(trends)
    return jsonify(result)
