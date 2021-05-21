from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('SIGN IN')

class MessageForm(FlaskForm):
    message = TextAreaField('text', validators=[DataRequired(), Length(min=1, max=160)])
    submit = SubmitField('ADD')

class DeleteForm(FlaskForm):
    record = IntegerField('id', validators=[DataRequired()])
    submit = SubmitField('DELETE')

class EditForm(FlaskForm):
    record = IntegerField('id', validators=[DataRequired()])
    message = TextAreaField('text', validators=[DataRequired(), Length(min=1, max=160)])
    submit = SubmitField('EDIT')
