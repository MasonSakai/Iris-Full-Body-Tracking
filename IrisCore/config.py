import os

basedir = os.path.abspath(os.path.dirname(__file__))
appdata_dir = os.path.join(os.getenv('APPDATA'), '/IrisFBT/')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    ROOT_PATH = basedir
    MODULE_PATH = os.path.join(basedir, 'modules')
    APPDATA_PATH = appdata_dir
    CONFIG_FILE = os.path.join(appdata_dir, '/core_conf.xml')