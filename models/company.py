from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Company(db.Model):

    __tablename__ = "companies"

    id = db.Column(
        db.Integer,
        primary_key=True
        )
    company_name = db.Column(
        db.Text,
        nullable=False
        )
    company_ticker = db.Column(
        db.Text,
        nullable=False
        )


