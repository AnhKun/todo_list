import os
from flask import Flask, render_template, redirect, url_for 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField 
from wtforms.validators import InputRequired

app = Flask(__name__)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = 1

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(50))

class TaskForm(FlaskForm):
    task = StringField('Your task', validators=[InputRequired()])
    submit = SubmitField('Save')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = TaskForm()
    tasks = Task.query.all()

    if form.validate_on_submit():
        new_task = Task(name=form.task.data, status='In progress')
        db.session.add(new_task)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('index.html', tasks=tasks, form=form)
