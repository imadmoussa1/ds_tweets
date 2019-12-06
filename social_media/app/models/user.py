from app.api import db, datetime, sha256, bcrypt


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    user_name = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    hashed_password = db.Column(db.Binary(60), nullable=False)
    authenticated = db.Column(db.Boolean, default=False)
    registered_on = db.Column(db.DateTime, nullable=True)
    role = db.Column(db.String, default='user')
    is_admin = db.Column(db.Boolean, nullable=False)

    def __init__(self, email, password, is_admin=True):
        self.user_name = email
        self.email = email
        self.password = password
        self.hashed_password = bcrypt.generate_password_hash(password)
        self.authenticated = False
        self.registered_on = datetime.now()
        self.is_admin = is_admin

    def get_id(self):
        """Return the id of a user to satisfy Flask-Login's requirements."""
        return str(self.id)

    def __repr__(self):
        return '<User {}>'.format(self.email)

    @classmethod
    def find_by_username(cls, user_name):
        return cls.query.filter_by(user_name=user_name).first()

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)
    
    def set_password(self, plaintext_password):
        self.hashed_password = bcrypt.generate_password_hash(plaintext_password)

    def is_correct_password(self, plaintext_password):
      return bcrypt.check_password_hash(self.hashed_password, plaintext_password)

    @property
    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    @property
    def is_active(self):
        """Always True, as all users are active."""
        return True

    @property
    def is_anonymous(self):
        """Always False, as anonymous users aren't supported."""
        return False

