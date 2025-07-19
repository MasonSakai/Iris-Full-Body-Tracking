from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
from flask_socketio import SocketIO


db = SQLAlchemy()
socket = SocketIO()
migrate = Migrate()
moment = Moment()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.static_folder = config_class.STATIC_FOLDER
    app.template_folder = config_class.TEMPLATE_FOLDER_MAIN

    db.init_app(app)
    migrate.init_app(app,db)
    moment.init_app(app)
    socket.init_app(app)

    # blueprint registration
    from app.main import main_blueprint as main
    main.template_folder = config_class.TEMPLATE_FOLDER_MAIN
    app.register_blueprint(main)
    
    from app.IrisModules import getSubModules
    getSubModules(app, config_class)

    return app

