from flask import *
from app import app
from app.forms import *
from app.models import *
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

@app.route('/')

# MESSAGE-VIEW
@app.route('/index')
def index():
    messages = Message.query.all()
    for message in messages:
        message.counter = Message.counter + 1 # +1 to 'msg-shown' counter for every /index viewing
    db.session.commit()
    return render_template("index.html", title='Posts', messages=messages)

@app.route('/login', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout', )
def logout():
    logout_user()
    return redirect('/')

# ADD-MESSAGE-VIEW
@app.route('/add', methods=('GET', 'POST'))
@login_required
def add():
    form = MessageForm()
    if form.validate_on_submit():
        message = Message(text=form.message.data, user=current_user, counter=0)
        db.session.add(message)
        db.session.commit()
        flash('Your message is now live!')
        return redirect(url_for('index'))
    return render_template("add.html", title='Add', form=form)

# REMOVE-MESSAGE-VIEW
@app.route('/remove', methods=('GET', 'POST'))
@login_required
def remove():
    form = DeleteForm()
    if form.validate_on_submit():
        record = Message.query.filter_by(id=form.record.data, user=current_user).first()
        if record is None:
            flash('Invalid id')
            return redirect(url_for('remove'))
        else:
            db.session.delete(record)
            db.session.commit()
            flash('Your message has been removed!')
            return redirect(url_for('index'))
    messages = current_user.messages
    return render_template('remove.html', messages=messages, form=form)

# EDIT-MESSAGE-VIEW
@app.route('/edit', methods=('GET', 'POST'))
@login_required
def edit():
    form = EditForm()
    if form.validate_on_submit():
        record = Message.query.filter_by(id=form.record.data, user=current_user).first()
        if record is None:
            flash('Invalid id')
            return redirect(url_for('edit'))
        else:
            record.text = form.message.data
            record.counter = 0 #editing messages resets 'msg-shown counter'
            db.session.commit()
            flash('Your changes have been saved!')
            return redirect(url_for('index'))
    messages = current_user.messages
    return render_template('edit.html', messages=messages, form=form)
