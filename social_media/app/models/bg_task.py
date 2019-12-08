from app.api import db, datetime
from flask_login import current_user


class BgTask(db.Model):
  __tablename__ = 'bg_task'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  task_name= db.Column(db.String(240), unique=True, nullable=False)
  task_status = db.Column(db.String(240), unique=True, nullable=False)
  task_response = db.Column(db.Json(240), unique=True, nullable=False)
  error = db.Column(db.Boolean)
  active = db.Column(db.Boolean)
  created_at = db.Column(db.DateTime, nullable=True)
  updated_at = db.Column(db.DateTime, nullable=True)
  added_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
  user = db.relationship("User")

  def __init__(self, task_name=None, task_status=None, task_response=None, error=False, active=True, updated=None):
    self.task_name = task_name
    self.task_status = task_status
    self.task_response = task_response
    self.error = error
    self.active = active
    self.added_by = None if current_user.is_anonymous else current_user.id

    if updated is None:
      self.created_at = datetime.now()
    else:
      self.updated_at = datetime.now()
