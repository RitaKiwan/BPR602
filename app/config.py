import os
from datetime import timedelta


basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) 

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dream-secret-dev-key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-dev-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'users.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'rkiwan09@gmail.com'
    MAIL_PASSWORD = 'Place the 16-character code here' 
    MAIL_DEFAULT_SENDER = 'rkiwan09@gmail.com'
