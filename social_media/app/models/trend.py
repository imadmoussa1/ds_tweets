from app.api import db, datetime
from flask_login import current_user


class Trend(db.Model):
  __tablename__ = 'trend'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String(240), unique=True, nullable=False)
  url = db.Column(db.String, nullable=True)
  promoted_content = db.Column(db.String, nullable=True)
  trend_query = db.Column(db.String, nullable=True)
  tweet_volume = db.Column(db.Integer, nullable=True)
  as_of = db.Column(db.DateTime, nullable=True)
  woeid = db.Column(db.Integer, nullable=False)
  active = db.Column(db.Boolean)
  created_at = db.Column(db.DateTime, nullable=True)
  updated_at = db.Column(db.DateTime, nullable=True)

  def __init__(self, name=None, url=None, promoted_content=None, trend_query=None, tweet_volume=None, as_of=None, woeid=None, active=True, updated=None):
    self.name = name
    self.url = url
    self.promoted_content = promoted_content
    self.trend_query = trend_query
    self.tweet_volume = tweet_volume
    self.woeid = woeid
    self.as_of = as_of
    self.active = active
    self.created_at = updated

    if updated is None:
      self.created_at = datetime.now()
    else:
      self.updated_at = datetime.now()
