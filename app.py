import os
from flask import Flask, render_template, redirect, url_for, flash
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

@app.route('/')
def index():
    form = TaskForm()
    tasks = Task.query.all()

    return render_template('index.html', tasks=tasks, form=form)

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

