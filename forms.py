from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import InputRequired
from flask_uploads import IMAGES

class TaskForm(FlaskForm):
    task = StringField('Your task', validators=[InputRequired()])
    submit = SubmitField('Save')

class RegisterForm(FlaskForm):
    username = StringField('username', validators=[InputRequired()])
    password = PasswordField('password', validators=[InputRequired()])
    remember = BooleanField('Remember me')
    image = FileField('image', validators=[FileAllowed(IMAGES)])

