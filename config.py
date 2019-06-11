import os


class Config(object):
    basedir = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.urandom(16)


class ProductionConfig(Config):
    # gets values from Config overrides any that are set here
    pass


class DevelopmentConfig(Config):
    # You have to set development before the app runs as an env variable
    # export DEBUG=True
    # export FLASK_ENV=development
    SECRET_KEY = 'apples'
