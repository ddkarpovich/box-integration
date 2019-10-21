import os


class Config(object):
    DEBUG = os.environ.get('FLASK_DEBUG', True)
    SECRET_KEY = 'dAasasiu^2891792gh!'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@localhost/dbname'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
