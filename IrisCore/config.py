import os

basedir = os.path.abspath(os.path.dirname(__file__))
appdata_dir = os.getenv('APPDATA')

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'project.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ROOT_PATH = basedir
    MODULE_PATH = os.path.join(basedir, 'modules')
    APPDATA_PATH = appdata_dir