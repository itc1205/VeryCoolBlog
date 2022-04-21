from os import listdir

from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm

from sqlalchemy import desc

from wtforms import PasswordField, StringField, IntegerField, EmailField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired

from mail import sendEmail

from data import db_session
from data.users import User
from data.news import News
from data.subbedemails import SubEmail

from datetime import datetime as dt

##############################################
#App init
app = Flask(__name__)
app.config['SECRET_KEY'] = 'nice'
login_manager = LoginManager()
login_manager.init_app(app)
USER_IMAGE_PATH = 'static/assets/user_images'

def main():
    db_session.global_init("db/mainDB.sqlite")
    app.run(host='0.0.0.0', port=80)

def postCreated(post="New post has been created.\nGo and check it out"):
    db_sess = db_session.create_session()
    for email in db_sess.query(SubEmail):
        sendEmail(email.email, post)

##############################################
#Error handling
@app.errorhandler(401)
def handle_auth_error(e):
    error = {
        "number": 401,
        "message": "You must be logged in to view this page",
    }
    return render_template('baseHtmlError.html', **error), 401

@app.errorhandler(404)
def handle_not_found(e):
    error = {
        "number": 404,
        "message": "This is not the web page you are looking for",
    }
    return render_template('baseHtmlError.html', **error), 404

@app.errorhandler(500)
def genius_handle(e):
    error = {
        "number": 500,
        "message": "Serverside issue",
    }
    return render_template('baseHtmlError.html', **error), 500

##############################################
#Routes

@app.route('/', methods=["GET", "POST"])
@app.route('/home', methods=["GET", "POST"])
def index():
    db_sess = db_session.create_session()
    if request.method == "POST":
        
        email = request.form["email"]
        
        if db_sess.query(SubEmail).filter(SubEmail.email == email).first():
            return redirect('/')
        subEmail = SubEmail()
        subEmail.email = email
            
        db_sess.add(subEmail)
        db_sess.commit()
            
        sendEmail(email, text="Thanks for subscription")
        return redirect('/')
    
    elif request.method == "GET":
        params = {
            "latest_posts" : db_sess.query(News).order_by(desc(News.created_date)).limit(3),
            "trending_news" : db_sess.query(News).order_by(News.views_count).limit(5),
            "older_posts" : db_sess.query(News).order_by(News.created_date).filter(
                News.id.notin_(db_sess.query(News.id).order_by(desc(News.created_date)).limit(3))).filter(
                    News.id.notin_(db_sess.query(News.id).order_by(News.views_count).limit(5))
            ).limit(6)
        }
        return render_template('index.html', **params)

@app.route('/post<int:id>')
def post(id):
    db_sess = db_session.create_session()
    params = {
        "post": db_sess.query(News).filter(News.id == id).first(),
    }
    return render_template('post.html', **params)

##############################################
#Login handling

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log in')


@app.route('/login', methods=['GET', 'POST'])
def login():
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
    return redirect('/home')

##############################################
#Registration handling

class RegistrationForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    repeat_password = PasswordField('Repeat password', validators=[DataRequired()])
    login = StringField('Login', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    submit = SubmitField('Complete registration')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    params = {
        'form': form
    }
    if form.validate_on_submit():

        if form.password.data != form.repeat_password.data:
            return render_template('register.html', **params,
                                   message="Password does not match")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', **params,
                                   message="User with this email is already exists")
        if db_sess.query(User).filter(User.login == form.login.data).first():
            return render_template('register.html', **params,
                                   message="User with this login is already exists")
        user = User(
            email=form.email.data,
            login=form.login.data,
            surname=form.surname.data,
            name=form.name.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return render_template('register.html', **params,
                               regComplete=True)
    return render_template('register.html', **params)


##########################################
# Account handle

@app.route('/account') 
@login_required
def account(): 
    user = current_user
    print(user)
    params = { 
        "name": user.name,
        "id": user.id,
        "login": user.login,
    } 
    return render_template('account.html', **params) 

#############################################
# Posts creation

class CreatePostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    short_description = TextAreaField('Short description', validators=[DataRequired()])
    submit = SubmitField('Submit post')


@app.route('/create_new_post', methods=["GET", "POST"])
@login_required
def createPost():

    form = CreatePostForm()
    params = {
        "form" : form,
    }

    if form.validate_on_submit():
        
        header_img = request.files['header_image']
        header_img_path = f'{USER_IMAGE_PATH}/header_images/header_image_{len(listdir(f"{USER_IMAGE_PATH}/header_images")) + 1}.png'
        with open(header_img_path, "wb") as file:
            file.write(header_img.read())
        
        preview_img = request.files['preview_image']
        preview_img_path = f'{USER_IMAGE_PATH}/preview_images/preview_image_{len(listdir(f"{USER_IMAGE_PATH}/preview_images")) + 1}.png'
        with open(preview_img_path, "wb") as file:
            file.write(preview_img.read())


        db_session.global_init("db/mainDB.sqlite") 
        db_sess = db_session.create_session()
        
        news = News()
        news.header_img = header_img_path
        news.preview_img = preview_img_path
        news.title = form.title.data
        news.content = form.content.data
        news.short_description = form.short_description.data
        current_user.news.append(news)
        
        db_sess.merge(current_user)
        db_sess.commit()
        
        postCreated()

        return redirect('/')
    
     
    
    return render_template('createNewPost.html', **params) 


if __name__ == "__main__": 
    main()
