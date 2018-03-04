from flask import Flask
from flask import render_template, flash, redirect, request
from flask import url_for, session, logging
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField
from wtforms import PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=6, max=30)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('E-mail', [validators.Length(min=10, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=6, max=255)])
    body = TextAreaField('Username', [validators.Length(min=30)])



app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'neuedeutscheharte'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Init MySQL
mysql = MySQL(app)

Articles = Articles()


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/articles')
def articles():
    return render_template('articles.html', articles=Articles)


@app.route('/article/<string:id>')
def article(id):
    return render_template('article.html', id=id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are registered and can log in', 'success')

        return redirect(url_for('login'))

    return render_template('register.html', form=form)

# User login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        # Get form fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Select by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get hash
            data = cur.fetchone()
            password = data['password']

            # Compare passwords
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username

                flash('You are logged in', 'success')
                return redirect(url_for('dashboard'))

                cur.close()
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)


    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized. Please log in', 'danger')
            return redirect(url_for('login'))
    return wrap
    
# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are logged out', 'success')
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')

# Add Article Route
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data

        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)", (title, body, session['username']))

        mysql.connection.commit()

        cur.close()

        flash('Article created', 'success')

        return redirect(url_for('dashboard'))

    return render_template('add_article', form=form)


if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True)
