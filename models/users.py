from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class Watchlist(db.Model):

    __tablename__ = "watchlists"

    company_id = db.Column(
      db.Integer,
      db.ForeignKey('companies.id', ondelete="cascade"),
      primary_key=True,
    )

    following_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
        )
    first_name = db.Column(
        db.Text,
        nullable=False
        )
    last_name = db.Column(
        db.Text,
        nullable=False
        )
    username = db.Column(
        db.Text,
        nullable=False
        )
    password = db.Column(
        db.Text,
        nullable=False
        )
    email = db.Column(
        db.Text,
        nullable=False,
        unique=True
        )
    following_comapny = db.Relationship(
        "User",
        secondary="followed_company",
        primaryjoin=(Watchlist.following_user_id == id)
        )

    @classmethod
    def signup(cls, username, email, password, image_url):

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=hashed_pwd,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

def connect_db(app):

    db.app = app
    db.init_app(app)
