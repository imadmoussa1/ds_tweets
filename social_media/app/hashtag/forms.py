from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError


class AddHashtagForm(FlaskForm):
  hashtag = StringField('hashtag', validators=[DataRequired(), Length(min=1, max=100)])
  active = BooleanField('Active')
  submit = SubmitField('Add')


class EditHashtagForm(FlaskForm):
  hashtag = StringField('hashtag', validators=[DataRequired(), Length(min=1, max=100)])
  active = BooleanField('Active')
  submit = SubmitField('Save')
