from app.api import db, datetime


class Trend(db.Model):
    __tablename__ = 'trend'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(240), unique=True, nullable=False)
    description = db.Column(db.String(240), nullable=False)
    hashtag = db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    added_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user = db.relationship("User")

    def __init__(self, title=None, description=None, hashtag=None, active=None, updated=None, user=None):
        self.title = title
        self.description = description
        self.hashtag = hashtag
        self.active = active
        self.user = user

        if updated is None:
            self.created_at = datetime.now()
        else:
            self.updated_at = datetime.now()
