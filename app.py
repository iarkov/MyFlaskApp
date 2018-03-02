from flask import Flask
from flask import render_template, flash, redirect
from flask import url_for, session, logging
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField
from wtforms import PasswordField, validators


class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=6, max=30)])
    username = StringField('Username', [valisdators.Length(min=4, max=25)])
    email = StringField('E-mail', [vlaidators.Length(min=10, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


app = Flask(__name__)

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


if __name__ == '__main__':
    app.run(debug=True)
