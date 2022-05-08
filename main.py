from os import listdir

from flask import Flask, abort, render_template, redirect, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm

from sqlalchemy import desc

from wtforms import PasswordField, StringField, SelectField, EmailField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired

import mail

from data import db_session
from data.users import User
from data.news import News
from data.subbedemails import SubEmail

##############################################
# App init
app = Flask(__name__)
app.config['SECRET_KEY'] = 'nice'
login_manager = LoginManager()
login_manager.init_app(app)
USER_IMAGE_PATH = 'static/assets/user_images'
DEFAULT_PROFILE_PICTURE_PATH = 'static/assets/default_images/profile_images/default_pfp.png'
DEFAULT_HEADER_PICTURE_PATH = 'static/assets/default_images/header_images/default.jpg'
DEFAULT_PREVIEW_PICTURE_PATH = 'static/assets/default_images/preview_images/default_preview.jpg'

with open(DEFAULT_PROFILE_PICTURE_PATH, "rb") as file:
        DEF_PROFILE_PIC = file.read()

with open(DEFAULT_HEADER_PICTURE_PATH, "rb") as file:
        DEF_HEADER_PIC = file.read()

with open(DEFAULT_PREVIEW_PICTURE_PATH, "rb") as file:
        DEF_PREVIEW_PIC = file.read()       

def main():
    db_session.global_init("db/mainDB.sqlite")
    mail.startMailServer()
    app.run(host='0.0.0.0', port=80)
    mail.stopMailServer()


def postCreated(news):
    db_sess = db_session.create_session()
    params = {
        'news': news,
    }
    for email in db_sess.query(SubEmail):
        params['mail'] = email.email
        mail.sendEmail(email.email, render_template("mail.html", **params))

##############################################
# Error handling


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
# Base routes


@app.route('/', methods=["GET", "POST"])
@app.route('/home', methods=["GET", "POST"])
def index():
    db_sess = db_session.create_session()

    if request.method == "POST":

        email = request.form["email"]
        
        if email:
            if db_sess.query(SubEmail).filter(SubEmail.email == email).first():
                return redirect('/')
            subEmail = SubEmail()
            subEmail.email = email

            db_sess.add(subEmail)
            db_sess.commit()

            mail.sendEmail(email, "Thanks for subscription")
        else:
            abort(404)
        flash("Mail has been subscribe")
        return redirect('/')

    if request.method == "GET":
        params = {
            "tags": {
                "travel": db_sess.query(News).filter(News.tag == "travel").order_by(News.views_count).first(),
                "food": db_sess.query(News).filter(News.tag == "food").order_by(News.views_count).first(),
                "technology": db_sess.query(News).filter(News.tag == "technology").order_by(News.views_count).first(),
                "health": db_sess.query(News).filter(News.tag == "health").order_by(News.views_count).first(),
                "nature": db_sess.query(News).filter(News.tag == "nature").order_by(News.views_count).first(),
                "fitness": db_sess.query(News).filter(News.tag == "fitness").order_by(News.views_count).first(),
            },

            "breaking_post": db_sess.query(News).order_by(desc(News.created_date)).first(),
            "latest_posts": db_sess.query(News).order_by(desc(News.created_date)).limit(3),
            "trending_news": db_sess.query(News).order_by(News.views_count).limit(5),
            "older_posts": db_sess.query(News).order_by(News.created_date).filter(
                News.id.notin_(db_sess.query(News.id).order_by(desc(News.created_date)).limit(3))).filter(
                    News.id.notin_(db_sess.query(News.id).order_by(
                        News.views_count).limit(5))
            ).limit(6),
            "quick_read": db_sess.query(News).order_by(desc(News.reading_time_in_seconds)).limit(7)
        }

        return render_template('index.html', **params)


@app.route('/post/<int:id>')
def post(id):

    db_sess = db_session.create_session()

    params = {
        "post": db_sess.query(News).filter(News.id == id).first(),
    }

    params['post'].views_count += 1
    db_sess.merge(params['post'])
    db_sess.commit()
    return render_template('post.html', **params)


@app.route('/unsub')
def unsubscribe_mail():
    db_sess = db_session.create_session()
    email = db_sess.query(SubEmail).filter(
        SubEmail.email == request.args.get('email')).first()
    db_sess.delete(email)
    flash('Mail has been unsubscribed!')
    return redirect('/')

##############################################
# Login handling


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


class LoginForm(FlaskForm):
    login = EmailField('Login', validators=[DataRequired()])
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
        user = db_sess.query(User).filter(User.login == form.login.data).first()
    
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash("User has been sucessfully logged in!")
            return redirect("/")
    
        return render_template('login.html',
                               message="Wrong login or password",
                               **params)
    
    return render_template('login.html', **params)


@app.route('/logout')
def logout():
    logout_user()
    
    flash('User has been sucessfully logged out!')

    return redirect('/')

##############################################
# Registration handling


class RegistrationForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    repeat_password = PasswordField(
        'Repeat password', validators=[DataRequired()])
    login = StringField('Login', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    user_description = TextAreaField('Short description', validators=[DataRequired()])
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
            description=form.user_description.data,
        )

        profile_image = request.files['profile_image']

        profile_image_path = f'{USER_IMAGE_PATH}/profile_images/profile_image_{len(listdir(f"{USER_IMAGE_PATH}/profile_images")) + 1}.png'
        
        if profile_image:
            with open(profile_image_path, "wb") as file:
                file.write(profile_image.read())
        
        else:
            with open(profile_image_path, "wb") as file:
                file.write(DEF_PROFILE_PIC.read())

        user.profile_image = profile_image_path

        user.set_password(form.password.data)

        db_sess.add(user)
        db_sess.commit()

        flash('Account has been created!')

        return redirect('/')
    return render_template('register.html', **params)


##########################################
# Account handle

@app.route('/account/<int:id>')
def account(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    
    if user:
        posts = user.news
    
    params = {
        "user": user,
        "posts": posts
    }
    
    return render_template('account.html', **params)

#############################################
# Posts creation


class CreatePostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    short_description = TextAreaField(
        'Short description', validators=[DataRequired()])
    tag = SelectField('Tags', choices=[
        ('fitness', 'Fitness'),
        ('travel', 'Travel'),
        ('food', 'Food'),
        ('nature', 'Nature'),
        ('health', 'Health'),
        ('technology', 'Technology'),
    ]
    )
    submit = SubmitField('Submit post')


@app.route('/create_new_post', methods=["GET", "POST"])
@login_required
def createPost():

    form = CreatePostForm()
    params = {
        "form": form,
    }

    if form.validate_on_submit():

        header_img = request.files['header_image']
        header_img_path = f'{USER_IMAGE_PATH}/header_images/header_image_{len(listdir(f"{USER_IMAGE_PATH}/header_images")) + 1}.png'
        if header_img:
            with open(header_img_path, "wb") as file:
                file.write(header_img.read())
        
        else:
            with open(header_img_path, "wb") as file:
                file.write(DEF_HEADER_PIC)

        preview_img = request.files['preview_image']
        preview_img_path = f'{USER_IMAGE_PATH}/preview_images/preview_image_{len(listdir(f"{USER_IMAGE_PATH}/preview_images")) + 1}.png'
        if preview_img:
            with open(preview_img_path, "wb") as file:
                file.write(preview_img.read())
        
        else:
            with open(preview_img_path, "wb") as file:
                file.write(DEF_PREVIEW_PIC)

        db_sess = db_session.create_session()

        news = News()
        news.header_img = header_img_path
        news.preview_img = preview_img_path
        news.title = form.title.data
        news.content = form.content.data
        news.short_description = form.short_description.data
        news.reading_time_in_seconds = round(
            len(form.content.data.split())/3, 35)
        news.reading_time_in_minutes = round(
            len(form.content.data.split())/201)
        news.tag = form.tag.data
        current_user.news.append(news)

        db_sess.merge(current_user)
        db_sess.commit()

        news = db_sess.query(News).filter(
            News.header_img == news.header_img).first()

        postCreated(news)
        flash('Post has been created!')

        return redirect('/')

    return render_template('createNewPost.html', **params)


##############################################
# Older posts route
@app.route('/older_posts')
def olderPosts():
    db_sess = db_session.create_session()

    params = {
        "older_posts": db_sess.query(News).order_by(News.created_date).filter(
            News.id.notin_(db_sess.query(News.id).order_by(desc(News.created_date)).limit(3))).filter(
            News.id.notin_(db_sess.query(News.id).order_by(
                News.views_count).limit(5))
        ).limit(6)
    }
    return render_template('olderPostsView.html', **params)

#############################################
# Search route


@app.route('/search')
def search():
    db_sess = db_session.create_session()
    
    params = {
        "search_string": request.args.get('search-field')
    }
    
    params["search_result"] = db_sess.query(News).order_by(News.created_date).filter(News.title.like(
        f"%{params['search_string']}%"
    ))
    return render_template('search.html', **params)


#############################################
# Edit/Delete posts

@login_required
@app.route('/edit_post', methods=['GET', 'POST'])
def edit_post():
    form = CreatePostForm()
    db_sess = db_session.create_session()
    post_id = request.args.get('post_id')
    post = db_sess.query(News).filter(News.id == post_id).first()
    
    if (not current_user.id == post.user.id) or (not post):
        abort(404)
    
    else:
        if request.method == "GET":

            form.title.data = post.title
            form.content.data = post.content
            form.short_description.data = post.short_description
            form.tag.data = post.tag
        
            return render_template("createNewPost.html", form=form)

        if form.validate_on_submit:
            header_img = request.files['header_image']
            header_img_path = post.header_img
            if header_img:
                with open(header_img_path, "wb") as file:
                    file.write(header_img.read())
            

            preview_img = request.files['preview_image']
            preview_img_path = post.preview_img
            if preview_img:
                with open(preview_img_path, "wb") as file:
                    file.write(preview_img.read())

            
            post.header_img = header_img_path
            post.preview_img = preview_img_path
            post.title = form.title.data
            post.content = form.content.data
            post.short_description = form.short_description.data
            post.reading_time_in_seconds = round(
                len(form.content.data.split())/3, 35)
            post.reading_time_in_minutes = round(
                len(form.content.data.split())/201)
            post.tag = form.tag.data

            db_sess.commit()
            
            db_sess.commit()
            flash('Post has been edited!')
            return redirect('/')



@login_required
@app.route('/delete_post')
def delete_post():
    db_sess = db_session.create_session()
    post_id = request.args.get('post_id')
    post = db_sess.query(News).filter(News.id == post_id).first()
    
    if (not current_user.id == post.user.id) or (not post):
        abort(404)
   
    else:
        db_sess.delete(post)
        db_sess.commit()
        flash('Post has been deleted!')
        return redirect('/')


@login_required
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    form = RegistrationForm()
    db_sess = db_session.create_session()
    user_id = request.args.get('user_id')
    user = db_sess.query(User).filter(User.id == user_id).first()
    if (not current_user.id == user.id) or (not user):
        abort(404)

    else:
        form.name.data = user.name
        form.surname.data = user.surname
        form.user_description.data = user.description
        form.email.data = user.email
        form.login.data = user.login
        
        if request.method == "GET":
            return render_template("register.html", form=form)

        if form.validate_on_submit:
            
            if form.password.data != form.repeat_password.data:
                return render_template('register.html', form=form,
                                    message="Password does not match")
            db_sess = db_session.create_session()

            if db_sess.query(User).filter(User.email == form.email.data).filter(User.id != user.id).first():
                return render_template('register.html', form=form,
                                    message="User with this email is already exists")

            if db_sess.query(User).filter(User.login == form.login.data).filter(User.id != user.id).first():
                return render_template('register.html', form=form,
                                    message="User with this login is already exists")

            user.email=form.email.data
            user.login=form.login.data
            user.surname=form.surname.data
            user.name=form.name.data
            user.description=form.user_description.data

            profile_image = request.files['profile_image']

            if profile_image:
                profile_image_path = user.profile_image

                with open(profile_image_path, "wb") as file:
                    file.write(profile_image.read())

            user.set_password(form.password.data)
            db_sess.commit()
            flash('Account has been redacted!')
            return redirect('/')

if __name__ == "__main__":
    main()
