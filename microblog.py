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