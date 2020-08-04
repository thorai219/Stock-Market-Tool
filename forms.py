from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length


class UserSignUp(FlaskForm):
    
    first_name = StringField('First-Name', validators=[DataRequired()])
    last_name = StringField('Last-Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
