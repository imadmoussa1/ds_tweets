from app.api import db, datetime


class Trend(db.Model):
    __tablename__ = 'trend'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(240), unique=True, nullable=False)
    url = db.Column(db.String, nullable=True)
    promoted_content = db.Column(db.String, nullable=True)
    query = db.Column(db.String, nullable=True)
    tweet_volume = db.Column(db.Integer, nullable=True)
    active = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    added_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user = db.relationship("User")

    def __init__(self, name=None, url=None, promoted_content=None, query=None, tweet_volume=None, active=None, updated=None, user=None):
        self.name = name
        self.url = url
        self.promoted_content = promoted_content
        self.query = query
        self.tweet_volume = tweet_volume
        self.active = active
        self.user = user

        if updated is None:
            self.created_at = datetime.now()
        else:
            self.updated_at = datetime.now()
