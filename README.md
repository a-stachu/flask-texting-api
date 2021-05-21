# flask-texting-api
Simple API for creating, editing, removing and viewing text messages with its own authentication system (Flask, Flask-login, SQLAlchemy, Sqlite3).

### Reference:
- Form-handling: [WTForms](https://wtforms.readthedocs.io/en/2.3.x/)
- Authentication: [Flask-login](https://flask-login.readthedocs.io/en/latest/) + [Werkzeug-security](https://werkzeug.palletsprojects.com/en/2.0.x/utils/) 
- SQL ORM: [SQL-Alchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/)
- Testing: [Flask-WebTest](https://flask-webtest.readthedocs.io/en/latest/)

## Getting started
Before you start the app, make sure you:
  1. Are using `Python 3.x.`,
  2. Have already installed `Flask` and its dependencies,
  3. Have activated your `virtualenv`.

To run the app, enter its folder in Terminal and type:
`python flask_app.py`

Then you may access the app from [localhost:5000/](http://localhost:5000/) typed in your address bar.

## Flask Application Structure
```
.
|──────app/
| |────templates/
| | |────add.html
| | |────base.html
| | |────edit.html
| | |────index.html
| | |────login.html
| | └────remove.html
| |────__init__.py
| |────data.db
| |────forms.py
| |────models.py
| |────routes.py
| └────test.db
|──────config.py
|──────flask_app.py
└──────tests.py

```
### Templates
`Templates` folder includes html files used for better perception of routes and mechanisms incorporated in them.
```
| |────templates/
| | |────add.html
| | |────base.html
| | |────edit.html
| | |────index.html
| | |────login.html
| | └────remove.html
```
### __init__.py
`__init__.py` creates the application object as an instance of class `Flask`. Location of the module passed here is used as a starting point when app needs to load associated resources(templates etc.).

```
|──────app/
| |────__init__.py
```
### data.db
`data.db` is the database, where all registered users and their messages are stored. `Config.py` file has code that connects us to the database: `SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app/data.db').
`
```
|──────app/
| |────data.db
```
### forms.py
`forms.py` stores web forms which are used in routes: `LoginForm`, `MessageForm`, `DeleteForm`, `EditForm`
```
|──────app/
| |────forms.py
```
### models.py
`models.py` stores database's models: `User` and `Messages`.
```
|──────app/
| |────models.py
```
### routes.py
`routes.py` contains routes which usage is explained later in `Routes-overview`.
```
|──────app/
| |────routes.py
```
### test.db
`test.db` is the database used for testing purposes in unit tests conducted in `tests.py`.
```
| └────test.db
```
### config.py
`config.py` stores configuration variables, like SECRET_KEY which is randomly generated as system variable and loaded when the app is run, or location of the application's database.
```
|──────config.py
```
### flask_app.py
`flask_app.py` defines the Flask application instance.
```
|──────flask_app.py
```
### tests.py
`tests.py` are unit tests explained later in `Unit-test`.
```
└──────tests.py
```

## Tables schema
### User
```
sqlite> .schema user
CREATE TABLE user (
        id INTEGER NOT NULL,
        username VARCHAR(20) NOT NULL,
        password_hash VARCHAR(128),
        PRIMARY KEY (id),
        UNIQUE (username)
);
```
### Message
```
sqlite> .schema message
CREATE TABLE message (
        id INTEGER NOT NULL,
        text VARCHAR(160) NOT NULL,
        counter INTEGER,
        user_id INTEGER NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY(user_id) REFERENCES user (id)
);
```
## Routes-overview

### /login | [url](http://localhost:5000/login)

[LOGIN] view function enables registering user as logged in, so that any page that user navigates to will have `current_user` set to that particular user.

Firstly, function checks whether `current_user` is authenticated (which means that the user has provided valid creditials) and if he returns `True`, he is redirected to the index page (since he has been already logged in).
``` 
@app.route('/login', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect('/')
```

If nobody is logged in, user is to be loaded from the database. Due to the username coming with the submission form, the database can be queried with it, so that this exact user can be found. To incorporate that, `filter_by()` method is used: it includes objects which match the properties: `username=form.username.data`. Adding `first()` at the end of the query returns objects (if it exsists) and since usernames are `UNIQUE` in our database, the query returns desired result, which is our username.

```     
form = LoginForm()
if form.validate_on_submit():
    user = User.query.filter_by(username=form.username.data).first()
```

If username does not exsist in the database, query returns `None`, and if password is not valid (which is checked using `check_password` method defined in `User db.model` - it compares password hashes), app flashes a message and redirects the user to the login page once again, so that he can enter right data. 

```
    if user is None or not user.check_password(form.password.data):
        flash('Invalid username or password')
        return redirect(url_for('login'))
login_user(user) 
```

### Registration

New accounts can be registered via `Python shell` using commands:
```
>>> from app import db
>>> from app.models import User
>>> test_user = User(username='USER')
>>> test_user.set_password('PASSWORD')
>>> db.session.add(test_user)
>>> db.session.commit()
```

To test out the app you may use one of accounts that already exsists in the database:
```
1. username: TEST_USER | password: PASSWORD
2. username: TEST_USER2 | password: PASSWROD2
```

### /logout | [url](http://localhost:5000/logout)

If `current_user.is_anonymous = False` (when somebody is logged in), [LOGOUT] view function logs the user out. The `current_user.is_anonymous` expression becomes `True` and the user is redirected to `/` route.

```
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')
```

### /index | [url](http://localhost:5000/index)

[INDEX] view function, messages created by users are queried from the database, so that they can be shown both to users who logged in and those who are anonymous. Additionally, for every `/index` view summoning, the `counter` next to messages gets incremented by 1 (`counter` indicates how many times every message has been shown to the user). Since `counter` is stored in the database in `Message` table, there is a `db.session.commit()` after that.

```
@app.route('/index')
def index():
    messages = Message.query.all()
    for message in messages:
        message.counter = Message.counter + 1
    db.session.commit()
```

### /add | [url](http://localhost:5000/add)

[ADD] view function uses form processing to insert a new `Message` record into the database. `validate_on_submit` function checks POST request and its validation. In the end template receives the `form` object which is used to render the text field. After the message being added successfully, the user is redirected to `/index` view.
In the very beggining of the function there is a `@login_required` function, which ensures that the current user is logged in and authenticated before calling the view.

```
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
```

### /edit | [url](http://localhost:5000/edit)

[EDIT] view function also uses `validate_on_submit` function to check POST request and its validation, and is protected by `@login_required` function so that only logged in users can use `edit` view. Querying database, searching for record which matches chosen id, it `edit` function ensures, that chosen database record actually exsist. Id chosen id does not match the criteria (`is None`), user is redirected back to the edit page again, so that he can enter correct data.

```
def edit():
    form = EditForm()
    if form.validate_on_submit():
        record = Message.query.filter_by(id=form.record.data, user=current_user).first()
        if record is None:
            flash('Invalid id')
            return redirect(url_for('edit'))
```
If the criteria are met, message's of choice text is swapped with this provided in the `Form` by the user. What's more, `counter` is set to 0 - edting messages resets it.

```
        else:
            record.text = form.message.data
            record.counter = 0 #editing messages resets 'msg-shown counter'
            db.session.commit()
            flash('Your changes have been saved!')
            return redirect(url_for('index'))
 ```
The user can see his messages on the same page, where `Form` is located, so that he can choose records to edit more easily.
```
    messages = current_user.messages
```

### /remove | [url](http://localhost:5000/remove)

[REMOVE] view function is protected by `@login_required` function and uses the very same mechanism as [EDIT] view function - `validate_on_submit()` checks POST request and its validation, and the database is queried to find records that match the criteria (`id`). If they do not match, user is redirected back to `(/remove)` view, and if they match, the record with this exact id is removed from the database. Once again, messages available to removal are shown on the same page to ease the burden of choosing records to delete.

```
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
```

## Unit-test (automated)
To run the unit tests, enter their folder in Terminal and type:
``` python tests.py ```

There are 6 tests in total:
### test_user
Test ensures that `user model` behaves correctly by adding `test_user` to `test.db`.
```
    def test_user(self):
        test_user = User(username='USER')
        test_user.set_password('PASSWORD')
        db.session.add(test_user)
        db.session.commit()
        assert test_user in db.session
```
### test_message
Test ensures that `message model` behaves correctly by adding `test_message` to `test.db`.
```
    def test_message(self):
        test_user = User(username='USER')
        test_message = Message(text='MESSAGE', user=test_user)
        db.session.add(test_message)
        db.session.commit()
        assert test_message in db.session
```
### test_message_view
Test ensures that `counter` behaves correctly upon potentially encountering `/index` route.
```
    def test_message_view(self):
        test_user = User(username='USER')
        test_message = Message(text='MESSAGE', user=test_user)
        test_message2 = Message(text='MESSAGE2', user=test_user)
        db.session.add(test_message)
        db.session.add(test_message2)
        db.session.commit()
        messages = Message.query.all()
        for message in messages:
            message.counter = Message.counter + 1
        db.session.commit()
        assert test_message in db.session
        assert test_message2 in db.session
```
### test_message_removal
Test ensures that `message` is removed from `test.db` correctly.
```
    def test_message_removal(self):
        test_user = User(username='USER')
        test_message = Message(text='MESSAGE', user=test_user, id=1)
        db.session.add(test_message)
        db.session.commit()
        removed_message = Message.query.filter_by(id=test_message.id, user=test_message.user).first()
        db.session.delete(removed_message)
        db.session.commit()
        assert test_message in db.session
```
### test_message_edit
Test ensures that `message` is edited in `test.db` correctly.
```
    def test_message_edit(self):
        test_user = User(username='USER')
        test_message = Message(text='MESSAGE', user=test_user, id=1)
        db.session.add(test_message)
        db.session.commit()
        new_message = Message.query.filter_by(id=test_message.id, user=test_message.user).first()
        new_message.text = 'NEW MESSAGE'
        new_message.counter = 0
        db.session.commit()
        assert new_message in db.session
        print(test_message.text)
```
### test_pages
Test checks whether routes load properly while being summoned and whether received HTTP responses are matching predicted results.
```
    def test_pages(self):
        with app.test_client() as c:
            response = c.get('/login')
            self.assertEqual(response.status_code, 200)
            response = c.get('/logout')
            self.assertEqual(response.status_code, 302)
            response = c.get('/index')
            self.assertEqual(response.status_code, 200)
            if (AnonymousUserMixin == False):
                response = c.get('/add')
                self.assertEqual(response.status_code, 200)
                response = c.get('/edit')
                self.assertEqual(response.status_code, 200)
                response = c.get('/remove')
                self.assertEqual(response.status_code, 200)
```

## Unit-test (manual)
Beside automated testing, there have been performed also manual tests (that is what `templates` were used for).

1. User visits `/login` route but logs in with incorrect data and gets redirected back to `login` route. Upon entering valid data, he gets redirected to `/index` route.
```
127.0.0.1 - - [21/May/2021 20:50:43] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [21/May/2021 20:50:46] "GET /login HTTP/1.1" 200 -
127.0.0.1 - - [21/May/2021 20:50:53] "POST /login HTTP/1.1" 302 -
127.0.0.1 - - [21/May/2021 20:50:53] "GET /login HTTP/1.1" 200 -
127.0.0.1 - - [21/May/2021 20:51:02] "POST /login HTTP/1.1" 302 -
127.0.0.1 - - [21/May/2021 20:51:02] "GET /index HTTP/1.1" 200 -
```
2. User visits `/add` route and adds new `message`. It met the criteria so user gets redirected to `/index` route.
```
127.0.0.1 - - [21/May/2021 20:51:15] "GET /add HTTP/1.1" 200 -
127.0.0.1 - - [21/May/2021 20:51:24] "POST /add HTTP/1.1" 302 -
127.0.0.1 - - [21/May/2021 20:51:24] "GET /index HTTP/1.1" 200 -
```
3. User visits `/edit` route and edits newly added `message`. It met the criteria so user gets redirected to `/index` route.
```
127.0.0.1 - - [21/May/2021 20:51:30] "GET /edit HTTP/1.1" 200 -
127.0.0.1 - - [21/May/2021 20:51:40] "POST /edit HTTP/1.1" 302 -
127.0.0.1 - - [21/May/2021 20:51:40] "GET /index HTTP/1.1" 200 -
```
4. User visits `/remove` route and removes recently edited `message`. `Id` met the criteria so user gets redirected to `/index` route.
```
127.0.0.1 - - [21/May/2021 20:51:45] "GET /remove HTTP/1.1" 200 -
127.0.0.1 - - [21/May/2021 20:51:48] "POST /remove HTTP/1.1" 302 -
127.0.0.1 - - [21/May/2021 20:51:48] "GET /index HTTP/1.1" 200 -
```
5. User visits `/logout` route and logs out successfully - as an anonymous user he gets redirected to `/` route.
```
127.0.0.1 - - [21/May/2021 20:51:52] "GET /logout HTTP/1.1" 302 -
127.0.0.1 - - [21/May/2021 20:51:52] "GET / HTTP/1.1" 200 -
```
Manual tests have given positive results.
