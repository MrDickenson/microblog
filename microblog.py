# ==============================================================================
# CHAPTER 1: Hello, World!
# ==============================================================================
'''
from flask import Flask

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(debug=True)
'''

# ==============================================================================
# CHAPTER 2: Templates (Jinja2)
# ==============================================================================
'''
from flask import Flask, render_template
from jinja2 import DictLoader

app = Flask(__name__)

TEMPLATES_CH2 = {
    'base.html': """
    <!doctype html>
    <html>
        <head>
            {% if title %}
            <title>{{ title }} - Microblog</title>
            {% else %}
            <title>Welcome to Microblog</title>
            {% endif %}
        </head>
        <body>
            <div>Microblog: <a href="/index">Home</a></div>
            <hr>
            {% block content %}{% endblock %}
        </body>
    </html>
    """,
    'index.html': """
    {% extends "base.html" %}
    {% block content %}
        <h1>Hi, {{ user.username }}!</h1>
        {% for post in posts %}
        <div><p>{{ post.author.username }} says: <b>{{ post.body }}</b></p></div>
        {% endfor %}
    {% endblock %}
    """
}
app.jinja_loader = DictLoader(TEMPLATES_CH2)

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Miguel'}
    posts = [
        {'author': {'username': 'John'}, 'body': 'Beautiful day in Portland!'},
        {'author': {'username': 'Susan'}, 'body': 'The Avengers movie was so cool!'}
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)

if __name__ == '__main__':
    app.run(debug=True)
'''

# ==============================================================================
# CHAPTER 3: Web Forms (Flask-WTF)
# ==============================================================================
'''
from flask import Flask, render_template, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from jinja2 import DictLoader

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

TEMPLATES_CH3 = {
    'base.html': """
    <!doctype html>
    <html>
        <head>
            {% if title %}
            <title>{{ title }} - Microblog</title>
            {% else %}
            <title>Welcome to Microblog</title>
            {% endif %}
        </head>
        <body>
            <div>
                Microblog:
                <a href="{{ url_for('index') }}">Home</a>
                <a href="{{ url_for('login') }}">Login</a>
            </div>
            <hr>
            {% with messages = get_flashed_messages() %}
            {% if messages %}
            <ul>
                {% for message in messages %}
                <li>{{ message }}</li>
                {% endfor %}
            </ul>
            {% endif %}
            {% endwith %}
            {% block content %}{% endblock %}
        </body>
    </html>
    """,
    'index.html': """
    {% extends "base.html" %}
    {% block content %}
        <h1>Hi, {{ user.username }}!</h1>
        {% for post in posts %}
        <div><p>{{ post.author.username }} says: <b>{{ post.body }}</b></p></div>
        {% endfor %}
    {% endblock %}
    """,
    'login.html': """
    {% extends "base.html" %}
    {% block content %}
        <h1>Sign In</h1>
        <form action="" method="post" novalidate>
            {{ form.hidden_tag() }}
            <p>
                {{ form.username.label }}<br>
                {{ form.username(size=32) }}<br>
                {% for error in form.username.errors %}
                <span style="color: red;">[{{ error }}]</span>
                {% endfor %}
            </p>
            <p>
                {{ form.password.label }}<br>
                {{ form.password(size=32) }}<br>
                {% for error in form.password.errors %}
                <span style="color: red;">[{{ error }}]</span>
                {% endfor %}
            </p>
            <p>{{ form.remember_me() }} {{ form.remember_me.label }}</p>
            <p>{{ form.submit() }}</p>
        </form>
    {% endblock %}
    """
}
app.jinja_loader = DictLoader(TEMPLATES_CH3)

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Miguel'}
    posts = [
        {'author': {'username': 'John'}, 'body': 'Beautiful day in Portland!'},
        {'author': {'username': 'Susan'}, 'body': 'The Avengers movie was so cool!'}
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(f'Login requested for user {form.username.data}, remember_me={form.remember_me.data}')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

if __name__ == '__main__':
    app.run(debug=True)
'''

# ==============================================================================
# CHAPTER 4: Database (Flask-SQLAlchemy & Flask-Migrate)
# ==============================================================================
'''
import os
from datetime import datetime, timezone
from flask import Flask, render_template, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from jinja2 import DictLoader

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Post {self.body}>'


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


TEMPLATES_CH4 = {
    'base.html': """
    <!doctype html>
    <html>
        <head>
            {% if title %}
            <title>{{ title }} - Microblog</title>
            {% else %}
            <title>Welcome to Microblog</title>
            {% endif %}
        </head>
        <body>
            <div>
                Microblog:
                <a href="{{ url_for('index') }}">Home</a>
                <a href="{{ url_for('login') }}">Login</a>
            </div>
            <hr>
            {% with messages = get_flashed_messages() %}
            {% if messages %}
            <ul>
                {% for message in messages %}
                <li>{{ message }}</li>
                {% endfor %}
            </ul>
            {% endif %}
            {% endwith %}
            {% block content %}{% endblock %}
        </body>
    </html>
    """,
    'index.html': """
    {% extends "base.html" %}
    {% block content %}
        <h1>Hi, {{ user.username }}!</h1>
        {% for post in posts %}
        <div><p>{{ post.author.username }} says: <b>{{ post.body }}</b></p></div>
        {% endfor %}
    {% endblock %}
    """,
    'login.html': """
    {% extends "base.html" %}
    {% block content %}
        <h1>Sign In</h1>
        <form action="" method="post" novalidate>
            {{ form.hidden_tag() }}
            <p>
                {{ form.username.label }}<br>
                {{ form.username(size=32) }}<br>
                {% for error in form.username.errors %}
                <span style="color: red;">[{{ error }}]</span>
                {% endfor %}
            </p>
            <p>
                {{ form.password.label }}<br>
                {{ form.password(size=32) }}<br>
                {% for error in form.password.errors %}
                <span style="color: red;">[{{ error }}]</span>
                {% endfor %}
            </p>
            <p>{{ form.remember_me() }} {{ form.remember_me.label }}</p>
            <p>{{ form.submit() }}</p>
        </form>
    {% endblock %}
    """
}
app.jinja_loader = DictLoader(TEMPLATES_CH4)


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Miguel'}
    posts = [
        {'author': {'username': 'John'}, 'body': 'Beautiful day in Portland!'},
        {'author': {'username': 'Susan'}, 'body': 'The Avengers movie was so cool!'}
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(f'Login requested for user {form.username.data}, remember_me={form.remember_me.data}')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    '''
# ==============================================================================
# CHAPTER 5: User Logins (Flask-Login & Password Hashing)
# ==============================================================================
'''
import os
from datetime import datetime, timezone
from urllib.parse import urlsplit
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from jinja2 import DictLoader

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')

db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(db.select(User).where(User.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = db.session.scalar(db.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')


TEMPLATES_CH5 = {
    'base.html': """
    <!doctype html>
    <html>
        <head>
            <title>{{ title ~ ' - Microblog' if title else 'Welcome to Microblog' }}</title>
        </head>
        <body>
            <div>
                Microblog:
                <a href="{{ url_for('index') }}">Home</a>
                {% if current_user.is_anonymous %}
                <a href="{{ url_for('login') }}">Login</a>
                {% else %}
                <a href="{{ url_for('logout') }}">Logout</a>
                {% endif %}
            </div>
            <hr>
            {% with messages = get_flashed_messages() %}
            {% if messages %}
            <ul>
                {% for message in messages %}
                <li>{{ message }}</li>
                {% endfor %}
            </ul>
            {% endif %}
            {% endwith %}
            {% block content %}{% endblock %}
        </body>
    </html>
    """,
    'index.html': """
    {% extends "base.html" %}
    {% block content %}
        <h1>Hi, {{ current_user.username }}!</h1>
        {% for post in posts %}
        <div><p>{{ post.author.username }} says: <b>{{ post.body }}</b></p></div>
        {% endfor %}
    {% endblock %}
    """,
    'login.html': """
    {% extends "base.html" %}
    {% block content %}
        <h1>Sign In</h1>
        <form action="" method="post" novalidate>
            {{ form.hidden_tag() }}
            <p>{{ form.username.label }}<br>{{ form.username(size=32) }}
            {% for error in form.username.errors %}<span style="color: red;">[{{ error }}]</span>{% endfor %}</p>
            <p>{{ form.password.label }}<br>{{ form.password(size=32) }}
            {% for error in form.password.errors %}<span style="color: red;">[{{ error }}]</span>{% endfor %}</p>
            <p>{{ form.remember_me() }} {{ form.remember_me.label }}</p>
            <p>{{ form.submit() }}</p>
        </form>
        <p>New User? <a href="{{ url_for('register') }}">Click to Register!</a></p>
    {% endblock %}
    """,
    'register.html': """
    {% extends "base.html" %}
    {% block content %}
        <h1>Register</h1>
        <form action="" method="post">
            {{ form.hidden_tag() }}
            <p>{{ form.username.label }}<br>{{ form.username(size=32) }}
            {% for error in form.username.errors %}<span style="color: red;">[{{ error }}]</span>{% endfor %}</p>
            <p>{{ form.email.label }}<br>{{ form.email(size=64) }}
            {% for error in form.email.errors %}<span style="color: red;">[{{ error }}]</span>{% endfor %}</p>
            <p>{{ form.password.label }}<br>{{ form.password(size=32) }}
            {% for error in form.password.errors %}<span style="color: red;">[{{ error }}]</span>{% endfor %}</p>
            <p>{{ form.password2.label }}<br>{{ form.password2(size=32) }}
            {% for error in form.password2.errors %}<span style="color: red;">[{{ error }}]</span>{% endfor %}</p>
            <p>{{ form.submit() }}</p>
        </form>
    {% endblock %}
    """
}
app.jinja_loader = DictLoader(TEMPLATES_CH5)


@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [
        {'author': {'username': 'John'}, 'body': 'Beautiful day in Portland!'},
        {'author': {'username': 'Susan'}, 'body': 'The Avengers movie was so cool!'}
    ]
    return render_template('index.html', title='Home', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
'''

# ==============================================================================
# CHAPTER 6: Profile Page and Avatars
# ==============================================================================
'''
import os
from hashlib import md5
from datetime import datetime, timezone
from urllib.parse import urlsplit
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from jinja2 import DictLoader

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')

db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')


TEMPLATES_CH6 = {
    '_post.html': """
    <table>
        <tr valign="top">
            <td><img src="{{ post.author.avatar(36) }}"></td>
            <td>{{ post.author.username }} says:<br>{{ post.body }}</td>
        </tr>
    </table>
    """,
    'user.html': """
    {% extends "base.html" %}
    {% block content %}
        <table>
            <tr valign="top">
                <td><img src="{{ user.avatar(128) }}"></td>
                <td>
                    <h1>User: {{ user.username }}</h1>
                    {% if user.about_me %}<p>{{ user.about_me }}</p>{% endif %}
                    {% if user.last_seen %}<p>Last seen on: {{ user.last_seen }}</p>{% endif %}
                    {% if user == current_user %}<p><a href="{{ url_for('edit_profile') }}">Edit your profile</a></p>{% endif %}
                </td>
            </tr>
        </table>
        <hr>
        {% for post in posts %}
            {% include '_post.html' %}
        {% endfor %}
    {% endblock %}
    """,
    'edit_profile.html': """
    {% extends "base.html" %}
    {% block content %}
        <h1>Edit Profile</h1>
        <form action="" method="post">
            {{ form.hidden_tag() }}
            <p>{{ form.username.label }}<br>{{ form.username(size=32) }}</p>
            <p>{{ form.about_me.label }}<br>{{ form.about_me(cols=50, rows=4) }}</p>
            <p>{{ form.submit() }}</p>
        </form>
    {% endblock %}
    """
}
# (Full routing combined in Chapter 8 below)
'''

# ==============================================================================
# CHAPTER 7: Error Handling (404, 500 & File Logging)
# ==============================================================================
'''
import logging
from logging.handlers import RotatingFileHandler

# Custom error handlers & logging setup (integrated into Chapter 8 below):
# @app.errorhandler(404)
# def not_found_error(error):
#     return render_template('404.html'), 404
#
# @app.errorhandler(500)
# def internal_error(error):
#     db.session.rollback()
#     return render_template('500.html'), 500
'''

# ==============================================================================
# CHAPTER 8: Followers (Many-to-Many Self-Referential Relationship)
# ==============================================================================
'''
import os
import logging
from logging.handlers import RotatingFileHandler
from hashlib import md5
from datetime import datetime, timezone
from urllib.parse import urlsplit
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from jinja2 import DictLoader

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')

db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'

# Chapter 7: Logging setup
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')

# Chapter 8: Followers association table
followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    following = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def follow(self, user):
        if not self.is_following(user):
            self.following.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        return self.following.filter(followers.c.followed_id == user.id).count() > 0

    def followers_count(self):
        return self.followers.count()

    def following_count(self):
        return self.following.count()

    def following_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)
        ).filter(followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        if db.session.scalar(db.select(User).where(User.username == username.data)):
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        if db.session.scalar(db.select(User).where(User.email == email.data)):
            raise ValidationError('Please use a different email address.')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            if db.session.scalar(db.select(User).where(User.username == username.data)):
                raise ValidationError('Please use a different username.')


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


TEMPLATES_CH8 = {
    'base.html': """
    <!doctype html>
    <html>
        <head>
            <title>{{ title ~ ' - Microblog' if title else 'Welcome to Microblog' }}</title>
        </head>
        <body>
            <div>
                Microblog:
                <a href="{{ url_for('index') }}">Home</a>
                {% if current_user.is_anonymous %}
                <a href="{{ url_for('login') }}">Login</a>
                {% else %}
                <a href="{{ url_for('user', username=current_user.username) }}">Profile</a>
                <a href="{{ url_for('logout') }}">Logout</a>
                {% endif %}
            </div>
            <hr>
            {% with messages = get_flashed_messages() %}
            {% if messages %}
            <ul>
                {% for message in messages %}
                <li>{{ message }}</li>
                {% endfor %}
            </ul>
            {% endif %}
            {% endwith %}
            {% block content %}{% endblock %}
        </body>
    </html>
    """,
    '_post.html': """
    <table>
        <tr valign="top">
            <td><img src="{{ post.author.avatar(36) }}"></td>
            <td><a href="{{ url_for('user', username=post.author.username) }}">{{ post.author.username }}</a> says:<br>{{ post.body }}</td>
        </tr>
    </table>
    """,
    'index.html': """
    {% extends "base.html" %}
    {% block content %}
        <h1>Hi, {{ current_user.username }}!</h1>
        {% for post in posts %}
            {% include '_post.html' %}
        {% endfor %}
    {% endblock %}
    """,
    'login.html': """
    {% extends "base.html" %}
    {% block content %}
        <h1>Sign In</h1>
        <form action="" method="post" novalidate>
            {{ form.hidden_tag() }}
            <p>{{ form.username.label }}<br>{{ form.username(size=32) }}
            {% for error in form.username.errors %}<span style="color: red;">[{{ error }}]</span>{% endfor %}</p>
            <p>{{ form.password.label }}<br>{{ form.password(size=32) }}
            {% for error in form.password.errors %}<span style="color: red;">[{{ error }}]</span>{% endfor %}</p>
            <p>{{ form.remember_me() }} {{ form.remember_me.label }}</p>
            <p>{{ form.submit() }}</p>
        </form>
        <p>New User? <a href="{{ url_for('register') }}">Click to Register!</a></p>
    {% endblock %}
    """,
    'register.html': """
    {% extends "base.html" %}
    {% block content %}
        <h1>Register</h1>
        <form action="" method="post">
            {{ form.hidden_tag() }}
            <p>{{ form.username.label }}<br>{{ form.username(size=32) }}
            {% for error in form.username.errors %}<span style="color: red;">[{{ error }}]</span>{% endfor %}</p>
            <p>{{ form.email.label }}<br>{{ form.email(size=64) }}
            {% for error in form.email.errors %}<span style="color: red;">[{{ error }}]</span>{% endfor %}</p>
            <p>{{ form.password.label }}<br>{{ form.password(size=32) }}
            {% for error in form.password.errors %}<span style="color: red;">[{{ error }}]</span>{% endfor %}</p>
            <p>{{ form.password2.label }}<br>{{ form.password2(size=32) }}
            {% for error in form.password2.errors %}<span style="color: red;">[{{ error }}]</span>{% endfor %}</p>
            <p>{{ form.submit() }}</p>
        </form>
    {% endblock %}
    """,
    'user.html': """
    {% extends "base.html" %}
    {% block content %}
        <table>
            <tr valign="top">
                <td><img src="{{ user.avatar(128) }}"></td>
                <td>
                    <h1>User: {{ user.username }}</h1>
                    {% if user.about_me %}<p>{{ user.about_me }}</p>{% endif %}
                    {% if user.last_seen %}<p>Last seen on: {{ user.last_seen }}</p>{% endif %}
                    <p>{{ user.followers_count() }} followers, {{ user.following_count() }} following.</p>
                    {% if user == current_user %}
                        <p><a href="{{ url_for('edit_profile') }}">Edit your profile</a></p>
                    {% elif not current_user.is_following(user) %}
                        <p>
                            <form action="{{ url_for('follow', username=user.username) }}" method="post">
                                {{ form.hidden_tag() }}
                                {{ form.submit(value='Follow') }}
                            </form>
                        </p>
                    {% else %}
                        <p>
                            <form action="{{ url_for('unfollow', username=user.username) }}" method="post">
                                {{ form.hidden_tag() }}
                                {{ form.submit(value='Unfollow') }}
                            </form>
                        </p>
                    {% endif %}
                </td>
            </tr>
        </table>
        <hr>
        {% for post in posts %}
            {% include '_post.html' %}
        {% endfor %}
    {% endblock %}
    """,
    'edit_profile.html': """
    {% extends "base.html" %}
    {% block content %}
        <h1>Edit Profile</h1>
        <form action="" method="post">
            {{ form.hidden_tag() }}
            <p>{{ form.username.label }}<br>{{ form.username(size=32) }}
            {% for error in form.username.errors %}<span style="color: red;">[{{ error }}]</span>{% endfor %}</p>
            <p>{{ form.about_me.label }}<br>{{ form.about_me(cols=50, rows=4) }}
            {% for error in form.about_me.errors %}<span style="color: red;">[{{ error }}]</span>{% endfor %}</p>
            <p>{{ form.submit() }}</p>
        </form>
    {% endblock %}
    """,
    '404.html': """
    {% extends "base.html" %}
    {% block content %}
        <h1>File Not Found</h1>
        <p><a href="{{ url_for('index') }}">Back</a></p>
    {% endblock %}
    """,
    '500.html': """
    {% extends "base.html" %}
    {% block content %}
        <h1>An unexpected error has occurred</h1>
        <p>The administrator has been notified. Sorry for the inconvenience!</p>
        <p><a href="{{ url_for('index') }}">Back</a></p>
    {% endblock %}
    """
}
app.jinja_loader = DictLoader(TEMPLATES_CH8)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = current_user.following_posts().all()
    return render_template('index.html', title='Home', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(db.select(User).where(User.username == username))
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts, form=form)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).where(User.username == username))
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(f'You are following {username}!')
        return redirect(url_for('user', username=username))
    return redirect(url_for('index'))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).where(User.username == username))
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You are not following {username}.')
        return redirect(url_for('user', username=username))
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    '''
# ==============================================================================
# CHAPTER 9: Pagination (Posts Creation, Explore Page & Next/Prev Links)
# ==============================================================================
'''
# Key additions in Chapter 9 (integrated into final Chapter 12 below):
# - PostForm for publishing new posts directly from the Home page
# - /explore route showing global stream of all users' posts
# - db.paginate() for splitting posts into pages (POSTS_PER_PAGE = 3)
'''

# ==============================================================================
# CHAPTER 10: Email Support (Password Reset with JWT & Flask-Mail)
# ==============================================================================
'''
# Key additions in Chapter 10 (integrated into final Chapter 12 below):
# - Flask-Mail configuration (prints reset links to console/SMTP)
# - User.get_reset_password_token() & User.verify_reset_password_token() using PyJWT
# - /reset_password_request and /reset_password/<token> routes and forms
'''

# ==============================================================================
# CHAPTER 11: Facelift (Bootstrap 5 Responsive UI & Navigation Bar)
# ==============================================================================
'''
# Key additions in Chapter 11 (integrated into final Chapter 12 below):
# - Bootstrap 5.3 CDN CSS & JS bundle in base.html
# - Responsive navbar, styled alerts, cards, and pagination buttons
'''

# ==============================================================================
# CHAPTER 12: Dates and Times (Flask-Moment UTC to Local Time Conversion)
# ==============================================================================
import os
import logging
from logging.handlers import RotatingFileHandler
from hashlib import md5
from datetime import datetime, timezone
from time import time
from urllib.parse import urlsplit
import jwt
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from flask_mail import Mail, Message
from flask_moment import Moment
from werkzeug.security import generate_password_hash, check_password_hash
from jinja2 import DictLoader

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['POSTS_PER_PAGE'] = 3

# Mail settings (Chapter 10)
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER') or 'localhost'
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT') or 8025)
app.config['ADMINS'] = ['admin@microblog.local']

db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'
mail = Mail(app)
moment = Moment(app)

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    following = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def follow(self, user):
        if not self.is_following(user):
            self.following.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        return self.following.filter(followers.c.followed_id == user.id).count() > 0

    def followers_count(self):
        return self.followers.count()

    def following_count(self):
        return self.following.count()

    def following_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)
        ).filter(followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256'
        )

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except Exception:
            return None
        return db.session.get(User, id)


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    reset_url = url_for('reset_password', token=token, _external=True)
    print(f'\n[EMAIL SIMULATION] Password reset link for {user.email}: {reset_url}\n')
    try:
        msg = Message('[Microblog] Reset Your Password',
                      sender=app.config['ADMINS'][0],
                      recipients=[user.email])
        msg.body = f'To reset your password click the following link:\n{reset_url}'
        mail.send(msg)
    except Exception:
        pass


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        if db.session.scalar(db.select(User).where(User.username == username.data)):
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        if db.session.scalar(db.select(User).where(User.email == email.data)):
            raise ValidationError('Please use a different email address.')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            if db.session.scalar(db.select(User).where(User.username == username.data)):
                raise ValidationError('Please use a different username.')


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')


TEMPLATES_CH12 = {
    'base.html': """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{{ title ~ ' - Microblog' if title else 'Welcome to Microblog' }}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
      </head>
      <body>
        <nav class="navbar navbar-expand-lg bg-body-tertiary mb-4 border-bottom">
          <div class="container">
            <a class="navbar-brand fw-bold" href="{{ url_for('index') }}">Microblog</a>
            <div class="collapse navbar-collapse show">
              <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                <li class="nav-item"><a class="nav-link" href="{{ url_for('index') }}">Home</a></li>
                <li class="nav-item"><a class="nav-link" href="{{ url_for('explore') }}">Explore</a></li>
              </ul>
              <ul class="navbar-nav mb-2 mb-lg-0">
                {% if current_user.is_anonymous %}
                <li class="nav-item"><a class="nav-link" href="{{ url_for('login') }}">Login</a></li>
                {% else %}
                <li class="nav-item"><a class="nav-link" href="{{ url_for('user', username=current_user.username) }}">Profile</a></li>
                <li class="nav-item"><a class="nav-link" href="{{ url_for('logout') }}">Logout</a></li>
                {% endif %}
              </ul>
            </div>
          </div>
        </nav>
        <div class="container">
          {% with messages = get_flashed_messages() %}
          {% if messages %}
            {% for message in messages %}
            <div class="alert alert-info" role="alert">{{ message }}</div>
            {% endfor %}
          {% endif %}
          {% endwith %}
          {% block content %}{% endblock %}
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        {{ moment.include_moment() }}
      </body>
    </html>
    """,
    '_post.html': """
    <div class="card mb-3">
      <div class="card-body d-flex align-items-start gap-3">
        <img src="{{ post.author.avatar(48) }}" class="rounded-circle">
        <div>
          <h6 class="card-subtitle mb-1 text-muted">
            <a href="{{ url_for('user', username=post.author.username) }}" class="text-decoration-none fw-bold">{{ post.author.username }}</a>
            said {{ moment(post.timestamp).fromNow() }}:
          </h6>
          <p class="card-text mb-0">{{ post.body }}</p>
        </div>
      </div>
    </div>
    """,
    'index.html': """
    {% extends "base.html" %}
    {% block content %}
      <h1 class="mb-3">Hi, {{ current_user.username }}!</h1>
      {% if form %}
      <form action="" method="post" class="mb-4">
        {{ form.hidden_tag() }}
        <div class="mb-2">
          {{ form.post.label(class="form-label") }}
          {{ form.post(class="form-control", rows=3) }}
          {% for error in form.post.errors %}<div class="text-danger small">{{ error }}</div>{% endfor %}
        </div>
        {{ form.submit(class="btn btn-primary") }}
      </form>
      {% endif %}
      {% for post in posts %}
        {% include '_post.html' %}
      {% endfor %}
      <nav aria-label="Post navigation">
        <ul class="pagination">
          <li class="page-item{% if not prev_url %} disabled{% endif %}">
            <a class="page-link" href="{{ prev_url or '#' }}">&larr; Newer posts</a>
          </li>
          <li class="page-item{% if not next_url %} disabled{% endif %}">
            <a class="page-link" href="{{ next_url or '#' }}">Older posts &rarr;</a>
          </li>
        </ul>
      </nav>
    {% endblock %}
    """,
    'login.html': """
    {% extends "base.html" %}
    {% block content %}
      <h1>Sign In</h1>
      <form action="" method="post" novalidate class="col-md-5">
        {{ form.hidden_tag() }}
        <div class="mb-3">
          {{ form.username.label(class="form-label") }}
          {{ form.username(class="form-control") }}
          {% for error in form.username.errors %}<div class="text-danger small">{{ error }}</div>{% endfor %}
        </div>
        <div class="mb-3">
          {{ form.password.label(class="form-label") }}
          {{ form.password(class="form-control") }}
          {% for error in form.password.errors %}<div class="text-danger small">{{ error }}</div>{% endfor %}
        </div>
        <div class="mb-3 form-check">
          {{ form.remember_me(class="form-check-input") }}
          {{ form.remember_me.label(class="form-check-label") }}
        </div>
        {{ form.submit(class="btn btn-primary") }}
      </form>
      <p class="mt-3">New User? <a href="{{ url_for('register') }}">Click to Register!</a></p>
      <p>Forgot Your Password? <a href="{{ url_for('reset_password_request') }}">Click to Reset It</a></p>
    {% endblock %}
    """,
    'register.html': """
    {% extends "base.html" %}
    {% block content %}
      <h1>Register</h1>
      <form action="" method="post" class="col-md-5">
        {{ form.hidden_tag() }}
        <div class="mb-3">{{ form.username.label(class="form-label") }}{{ form.username(class="form-control") }}
        {% for error in form.username.errors %}<div class="text-danger small">{{ error }}</div>{% endfor %}</div>
        <div class="mb-3">{{ form.email.label(class="form-label") }}{{ form.email(class="form-control") }}
        {% for error in form.email.errors %}<div class="text-danger small">{{ error }}</div>{% endfor %}</div>
        <div class="mb-3">{{ form.password.label(class="form-label") }}{{ form.password(class="form-control") }}
        {% for error in form.password.errors %}<div class="text-danger small">{{ error }}</div>{% endfor %}</div>
        <div class="mb-3">{{ form.password2.label(class="form-label") }}{{ form.password2(class="form-control") }}
        {% for error in form.password2.errors %}<div class="text-danger small">{{ error }}</div>{% endfor %}</div>
        {{ form.submit(class="btn btn-primary") }}
      </form>
    {% endblock %}
    """,
    'user.html': """
    {% extends "base.html" %}
    {% block content %}
      <div class="card mb-4">
        <div class="card-body d-flex align-items-center gap-4">
          <img src="{{ user.avatar(128) }}" class="rounded-circle">
          <div>
            <h1>User: {{ user.username }}</h1>
            {% if user.about_me %}<p>{{ user.about_me }}</p>{% endif %}
            {% if user.last_seen %}<p class="text-muted">Last seen on: {{ moment(user.last_seen).format('LLL') }}</p>{% endif %}
            <p>{{ user.followers_count() }} followers, {{ user.following_count() }} following.</p>
            {% if user == current_user %}
              <a href="{{ url_for('edit_profile') }}" class="btn btn-outline-secondary btn-sm">Edit your profile</a>
            {% elif not current_user.is_following(user) %}
              <form action="{{ url_for('follow', username=user.username) }}" method="post">
                {{ form.hidden_tag() }}{{ form.submit(value='Follow', class="btn btn-primary btn-sm") }}
              </form>
            {% else %}
              <form action="{{ url_for('unfollow', username=user.username) }}" method="post">
                {{ form.hidden_tag() }}{{ form.submit(value='Unfollow', class="btn btn-secondary btn-sm") }}
              </form>
            {% endif %}
          </div>
        </div>
      </div>
      {% for post in posts %}{% include '_post.html' %}{% endfor %}
      <nav aria-label="User posts navigation">
        <ul class="pagination">
          <li class="page-item{% if not prev_url %} disabled{% endif %}"><a class="page-link" href="{{ prev_url or '#' }}">&larr; Newer posts</a></li>
          <li class="page-item{% if not next_url %} disabled{% endif %}"><a class="page-link" href="{{ next_url or '#' }}">Older posts &rarr;</a></li>
        </ul>
      </nav>
    {% endblock %}
    """,
    'edit_profile.html': """
    {% extends "base.html" %}
    {% block content %}
      <h1>Edit Profile</h1>
      <form action="" method="post" class="col-md-5">
        {{ form.hidden_tag() }}
        <div class="mb-3">{{ form.username.label(class="form-label") }}{{ form.username(class="form-control") }}</div>
        <div class="mb-3">{{ form.about_me.label(class="form-label") }}{{ form.about_me(class="form-control", rows=4) }}</div>
        {{ form.submit(class="btn btn-primary") }}
      </form>
    {% endblock %}
    """,
    'reset_password_request.html': """
    {% extends "base.html" %}
    {% block content %}
      <h1>Reset Password</h1>
      <form action="" method="post" class="col-md-5">
        {{ form.hidden_tag() }}
        <div class="mb-3">{{ form.email.label(class="form-label") }}{{ form.email(class="form-control") }}</div>
        {{ form.submit(class="btn btn-primary") }}
      </form>
    {% endblock %}
    """,
    'reset_password.html': """
    {% extends "base.html" %}
    {% block content %}
      <h1>Reset Your Password</h1>
      <form action="" method="post" class="col-md-5">
        {{ form.hidden_tag() }}
        <div class="mb-3">{{ form.password.label(class="form-label") }}{{ form.password(class="form-control") }}</div>
        <div class="mb-3">{{ form.password2.label(class="form-label") }}{{ form.password2(class="form-control") }}</div>
        {{ form.submit(class="btn btn-primary") }}
      </form>
    {% endblock %}
    """,
    '404.html': """
    {% extends "base.html" %}
    {% block content %}
      <h1>File Not Found</h1>
      <p><a href="{{ url_for('index') }}">Back</a></p>
    {% endblock %}
    """,
    '500.html': """
    {% extends "base.html" %}
    {% block content %}
      <h1>An unexpected error has occurred</h1>
      <p><a href="{{ url_for('index') }}">Back</a></p>
    {% endblock %}
    """
}
app.jinja_loader = DictLoader(TEMPLATES_CH12)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = db.paginate(current_user.following_posts(), page=page,
                        per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Home', form=form,
                           posts=posts.items, next_url=next_url, prev_url=prev_url)


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    query = db.select(Post).order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page,
                        per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Explore',
                           posts=posts.items, next_url=next_url, prev_url=prev_url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).where(User.email == form.email.data))
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(db.select(User).where(User.username == username))
    page = request.args.get('page', 1, type=int)
    query = user.posts.order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page,
                        per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('user', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).where(User.username == username))
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(f'You are following {username}!')
        return redirect(url_for('user', username=username))
    return redirect(url_for('index'))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).where(User.username == username))
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You are not following {username}.')
        return redirect(url_for('user', username=username))
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)