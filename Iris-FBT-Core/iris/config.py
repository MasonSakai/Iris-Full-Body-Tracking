import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'iris.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ROOT_PATH = basedir
    STATIC_FOLDER = os.path.join(basedir, 'app//static')
    TEMPLATE_FOLDER_MAIN = os.path.join(basedir, 'app//main//templates')
    TEMPLATE_FOLDER_AUTH = os.path.join(basedir, 'app//auth//templates')
    TEMPLATE_FOLDER_STUDENT = os.path.join(basedir, 'app//student//templates')
    TEMPLATE_FOLDER_FACULTY = os.path.join(basedir, 'app//faculty//templates')
    TEMPLATE_FOLDER_ERRORS = os.path.join(basedir, 'app//errors//templates')

