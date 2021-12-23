import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import InputRequired
from flask_wtf.file import FileField, FileAllowed
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_uploads import IMAGES, UploadSet, configure_uploads
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

photos = UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST'] = 'static/images'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = 1
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

configure_uploads(app, photos)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255))
    tasks = db.relationship('Task', backref='user', lazy='dynamic')

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class TaskForm(FlaskForm):
    task = StringField('Your task', validators=[InputRequired()])
    submit = SubmitField('Save')

class RegisterForm(FlaskForm):
    username = StringField('username', validators=[InputRequired()])
    password = PasswordField('password', validators=[InputRequired()])
    remember = BooleanField('Remember me')
    image = FileField('image', validators=[FileAllowed(IMAGES)])


@app.route('/')
def index():
    form = TaskForm()
    tasks = Task.query.all()

    return render_template('index.html', tasks=tasks, form=form, logged_in_user=current_user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        image = 'Anonymous'
        if form.image.data:
            image = photos.save(form.image.data)

        new_user = User(
            username = form.username.data,
            password = generate_password_hash(form.password.data),
            image = image
        )
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for('index'))
        
    return render_template('register.html', form=form)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = RegisterForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('index'))
            flash('Login failed!')
        else:
            flash('Login failed!')

    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/add', methods=['POST'])
def add():
    form = TaskForm()

    available_task = Task.query.filter_by(name=form.task.data).first()

    if form.validate():
        if available_task:
            flash('This task alredy exist!')
        else:
            new_task = Task(name=form.task.data, status='In progress')
            db.session.add(new_task)
            db.session.commit()

        return redirect(url_for('index'))

@app.route('/completed/<id>')
def completed(id):
    task = Task.query.filter_by(id=id).first()

    task.status = 'Completed'
    db.session.add(task)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/delete/<id>')
def delete(id):
    task = Task.query.filter_by(id=id).first()

    db.session.delete(task)
    db.session.commit()

    return redirect(url_for('index'))

