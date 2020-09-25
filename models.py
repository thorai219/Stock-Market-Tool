from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()

class Following(db.Model):

    __tablename__ = 'following' 

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer
    )

    company_symbol = db.Column(
        db.Text
    )

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    fullname = db.Column(
        db.Text,
        nullable=False,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    following = db.Column(
        db.Text,
    )

    @classmethod
    def signup(cls, username, fullname, email, password):

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            fullname=fullname,
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

class Company(db.Model):

    __tablename__ = 'companies'

    symbol = db.Column(
      db.Text,
      primary_key=True
    )

    name = db.Column(
      db.Text
    )


def connect_db(app):

    db.app = app
    db.init_app(app)
    db.create_all()
    db.session.commit()
    dir(db)






