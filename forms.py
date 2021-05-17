from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, PasswordField, DateField, SelectField, RadioField
from wtforms.validators import DataRequired, InputRequired, NumberRange, Length, EqualTo
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from models import Visitor, URL, User
from sqlalchemy import text


class UserLoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])


class RefreshPageForm(FlaskForm):
    refresh_every = RadioField("Refresh Every", validators=[DataRequired()])
