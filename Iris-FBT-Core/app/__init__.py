from flask import Flask
from config import Config
from model import Model
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.static_folder = config_class.STATIC_FOLDER
    app.template_folder = config_class.TEMPLATE_FOLDER_MAIN
    
    db.init_app(app)



    return app