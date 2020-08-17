from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()

class Company(db.Model):

    __tablename__ = "companies"

    id = db.Column(
        db.Integer,
        primary_key=True
        )
    name = db.Column(
        db.Text
        )
    symbol = db.Column(
        db.Text
        )
    exchange = db.Column(
        db.Text
        )
    
    def __init__(self,name,symbol,exchange):
        self.name = name
        self.symbol = symbol
        self.exchange = exchange


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
    fullname = db.Column(
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

    def __init__(self, fullname, username, password, email):
        self.fullname = fullname
        self.username = username
        self.password = password
        self.email = email

    @classmethod
    def signup(cls, fullname, username, email, password):

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            fullname=fullname,
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
    db.create_all()
    db.session.commit()
    dir(db)


