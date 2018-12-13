import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
#importing from init file, application, database and password hasher
from bacefook import app, db, bcrypt
#using bacefook.forms instead of just forms due to use of packages
from bacefook.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, CommentForm, SearchForm, PostLikeForm
from bacefook.models import User, Post, Comment, PostLike
from flask_login import login_user, current_user, logout_user, login_required

#decorators that allow us to navigate to our pages
@app.route("/")
@app.route("/home")
def home():
    #requesting from flask that home show the first page of posts, must be int
    page = request.args.get('page', 1, type=int)
    #using paginate method to only load 5 posts on the home page
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    #using flask to render HTML templates that use instanciated queries to the database "Post"
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    #error checking, if valid flash success message
    if form.validate_on_submit():
        #hashing the password entered by user
        #storing it as a string by using UTF-8
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        #create new instance of user
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        #add user to database via SQLAlchemy
        db.session.add(user)
        db.session.commit()
        #alert user of successful account creation and redirect to login page
        flash('Your account has been created, welcome to the Terror Dome!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        #checking the database to validate user login
        user = User.query.filter_by(email=form.email.data).first()
        #check to see if the user exists and that entered password mathches database password
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            #using get method so that if 'next' doesn't exist we don't throw an error
            #using the traditiong [] would throw an error if next did not have a value
            next_page = request.args.get('next')
            #turnary conditional that smartly redirects a user after logging in
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

#instead of using the name of the image uploaded by user
#it is better to create a random 8 byte name to avoid collisions in the database
#resizes image before saving to DB via the Pillow (PIL) package
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    #keeping the extension of the user image file
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    #in order to save image into profile_pics in static folder we need access to root path
    #it would be a good idea to learn more about "os" module
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    #resizing User image to 125 pixels
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn
#it would be nice to add code to delete User picture after a successful update



#@decorators @login_required tells route (account) user must be logged in
@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    #When user updates either username or email we first validate the new entries
    #then we overwrite the username and email in the database
    if form.validate_on_submit():
        if form.picture.data:
            #function is above
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        #'success' boostrap class
        flash('You have successfully updated your BaceFook!', 'success')
        #redirect here stops browser from allowing user to POST again
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    #accessing the database for a users image via image_file from models
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post on tiny poster!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')

#casting the post_id as an int, just to make sure
@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):
    #give me the post with this id, or return 404 error
    post = Post.query.get_or_404(post_id)
    comment = Comment.query.join(Post).join(User).filter(Post.id==post_id)
    likes = PostLike.query.join(Post).filter(Post.id==post_id).count()
    # c_likes = CommentLike.query.join(Comment).filter(Comment.id==CommentLike.comment_id).count()
    form = PostLikeForm()
    # c_form = CommentLikeForm()
    # if c_form.validate_on_submit():
    #     c_like = CommentLike(author=current_user, comment_id=commentID)
    #     db.session.add(c_like)
    #     db.session.commit()
    #     flash('You like comments, you really like them!', 'success')
    #     return redirect(url_for('post', post_id=post.id))
    if form.validate_on_submit():
        like = PostLike(author=current_user, post_id=post.id)
        db.session.add(like)
        db.session.commit()
        flash('Like on tiny liker!', 'success')
        return redirect(url_for('post', post_id=post.id))
    return render_template('post.html', title=post.title, post=post, comment=comment, form=form, likes=likes)

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    #give me the post with this id, or return 404 error
    post = Post.query.get_or_404(post_id)
    #if the user isn't the author of the post, don't let them update
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')

@app.route("/post/<int:post_id>/comment", methods=['GET', 'POST'])
@login_required
def comment_on_post(post_id):
    #give me the post with this id, or return 404 error
    post = Post.query.get_or_404(post_id)
    #if the user isn't the author of the post, don't let them update
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(comment_content=form.comment.data, post_id=post.id, author=current_user)
        db.session.add(comment)
        db.session.commit()
        flash('A man with a nickle for every comment is now 5 cents richer', 'success')
        return redirect(url_for('post', post_id=post.id))
    return render_template('comment_on_post.html', title='Comment Post', form=form, post=post, post_id=post_id, legend='Comment')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    #if the user isn't the author of the post, don't let them update
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

#allowing the user to click on a username and see posts only by that user
@app.route("/user/<string:username>")
def user_posts(username):
    #requesting from flask that home show the first page of posts, must be int
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    #filtering all posts by author/user, then descending order,
    #then using paginate to only display the first 5 posts
    posts = Post.query.filter_by(author=user)\
    .order_by(Post.date_posted.desc())\
    .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)
