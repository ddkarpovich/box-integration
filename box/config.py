import os


class Config(object):
    DEBUG = os.environ.get('FLASK_DEBUG', False)
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('FLASK_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
