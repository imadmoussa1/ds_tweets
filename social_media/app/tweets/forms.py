from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError


class TweetsForm(FlaskForm):
  query = StringField('query', validators=[DataRequired(), Length(min=1, max=100)])
  search = SubmitField('Search')
