from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, logout_user
from flask_wtf import FlaskForm

from wtforms import PasswordField, StringField, IntegerField, EmailField, SubmitField, BooleanField
from wtforms.validators import DataRequired

from data import db_session
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nice'
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/mainDB.sqlite")
    app.run()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')


@app.route('/post')
def post():
    return render_template('post.html')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log in')


@app.route('/login', methods=['GET', 'POST'])
def login():
    db_session.global_init("db/mars_explorer.sqlite")
    form = LoginForm()
    params = {
        'form': form,
    }
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Wrong login or password",
                               **params)
    return render_template('login.html', **params)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/index')


if __name__ == "__main__":
    main()
