from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, photos, db, login_manager
from forms import TaskForm, RegisterForm
from models import User, Task

@app.route('/')
def index():
    form = TaskForm()

    if current_user.is_anonymous:
        tasks = Task.query.filter_by(user_id=0).all()
    else:
        tasks = Task.query.filter_by(user_id=current_user.id).all()

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
@login_required
def add():
    form = TaskForm()
    if form.validate():
        new_task = Task(name=form.task.data, status='In progress', user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()

        return redirect(url_for('index'))

@app.route('/completed/<id>')
@login_required
def completed(id):
    task = Task.query.filter_by(id=id).first()

    task.status = 'Completed'
    db.session.add(task)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/delete/<id>')
@login_required
def delete(id):
    task = Task.query.filter_by(id=id).first()

    db.session.delete(task)
    db.session.commit()

    return redirect(url_for('index'))