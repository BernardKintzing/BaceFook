#using packages in this way, helps us to eliminate issues cause by running
#python from the command line, (e.g., using __main__) as well as issues
#that arise from creating db instance without splitting app into packages

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


#setting app as an instance of the Flask Class
#(__name__) is a python convention, (__name__) == (__main__)
app = Flask(__name__)
#this is going to help prevent request forgery attacks
app.config['SECRET_KEY'] = 'AlexBernardDestin'
#using "///" means create this .db file in the current directory
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///BaceFook.db'
#initializing flask package classes
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
#making sure user must be logged in to access account information
login_manager.login_view = 'login'
#accessing 'info' bootsrap class to make it look purrrty
login_manager.login_message_category = 'info'

#importing routes after app initialization to avoid circular import problems
from bacefook import routes
