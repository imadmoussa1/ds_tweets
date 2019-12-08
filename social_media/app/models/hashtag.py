from app.api import db, datetime
from flask_login import current_user


class Hashtag(db.Model):
  __tablename__ = 'hashtag'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  hashtag = db.Column(db.String(240), unique=True, nullable=False)
  active = db.Column(db.Boolean)
  created_at = db.Column(db.DateTime, nullable=True)
  updated_at = db.Column(db.DateTime, nullable=True)
  added_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
  user = db.relationship("User")

  def __init__(self, hashtag=None, active=True, updated=None):
    self.hashtag = hashtag
    self.active = active
    self.added_by = None if current_user.is_anonymous else current_user.id

    if updated is None:
      self.created_at = datetime.now()
    else:
      self.updated_at = datetime.now()
