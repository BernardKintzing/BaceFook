from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from bacefook.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    #protecting against db errors caused by duplicate user information
    def validate_username(self, username):
        #querying the db to see the the username from the registration form
        #already exists, if the user exists, throw validation error
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Early bird gets the username, sorry, choose another one.')

        #protecting against db errors caused by duplicate user information
    def validate_email(self, email):
            #querying the db to see if the email from the registration form
            #already exists, if the email exists, throw validation error
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already in use, sorry, choose another one.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    #protecting against db errors caused by duplicate user information
    def validate_username(self, username):
        if username.data != current_user.username:
        #querying the db to see the the username from the registration form
        #already exists, if the user exists, throw validation error
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Early bird gets the username, sorry, choose another one.')

        #protecting against db errors caused by duplicate user information
    def validate_email(self, email):
        if email.data != current_user.email:
            #querying the db to see if the email from the registration form
            #already exists, if the email exists, throw validation error
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is already is use, sorry, choose another one.')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

class CommentForm(FlaskForm):
    comment = TextAreaField('Comment', validators=[DataRequired()])
    submit_comment = SubmitField('Add comment')

class SearchForm(FlaskForm):
    searched_user = StringField('User', validators=[DataRequired()])
    submit_comment = SubmitField('Search')

class PostLikeForm(FlaskForm):
    submit_like = SubmitField('Like')
