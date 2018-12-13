#models for our database
from datetime import datetime
#importing db, login instance from bacefook __init__ file
from bacefook import db, login_manager
#UserMixin helps authenticate Users
from flask_login import UserMixin

#this function is for the login_manager class, telling it how to find a user_id
#querying the database for a user_id
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    #posts attribute has a relationship to Post model
    #backref allows us to use author attribute to get the user who created post
    #'author' references the user_id
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    likes = db.relationship('PostLike', backref='author', lazy=True)
    # c_likes = db.relationship('CommentLike', backref='author', lazy=True)

    def __repr__(self): #dunder method/magic method, how our object is printed
    #self variable is a python specific variable, seems similar to this in java
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    #able to use post.id rather than Post.id because SQLAlc names table with lowercase
    comments = db.relationship('Comment', backref='postId', lazy=True)
    likes = db.relationship('PostLike', backref='postId', lazy=True)

    def __repr__(self): #dunder method/magic method, how our object is printed
    #self variable is a python specific variable, seems similar to this in java
        return f"Post('{self.title}', '{self.date_posted}')"

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment_content = db.Column(db.Text, nullable=False)
    comment_date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # c_likes = db.relationship('CommentLike', backref='commentId', lazy=True)

    def __repr__(self): #dunder method/magic method, how our object is printed
    #self variable is a python specific variable, seems similar to this in java
        return f"Comment('{self.comment_content}', '{self.comment_date_posted}')"

class PostLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

# class CommentLike(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)
