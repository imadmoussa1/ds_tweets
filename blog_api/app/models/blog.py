from app.api import db, datetime


class Blog(db.Model):
    __tablename__ = 'blog'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(240), unique=True, nullable=False)
    description = db.Column(db.String(240), nullable=False)
    content = db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    added_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user = db.relationship("User")

    def __init__(self, title=None, description=None, content=None, active=None, updated=None, user=None):
        self.title = title
        self.description = description
        self.content = content
        self.active = active
        self.user = user

        if updated is None:
            self.created_at = datetime.now()
        else:
            self.updated_at = datetime.now()
