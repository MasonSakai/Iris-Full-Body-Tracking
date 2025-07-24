from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
from flask_socketio import SocketIO

db = SQLAlchemy()
migrate = Migrate()
moment = Moment()
socketio = SocketIO()

from app.IrisModules import getSubModules

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app,db)
    moment.init_app(app)
    socketio.init_app(app)

    # blueprint registration
    from app.main import main_blueprint as main
    app.register_blueprint(main)

    from app.apriltag import apriltag_blueprint as apriltag
    app.register_blueprint(apriltag)
    
    getSubModules(app, config_class)

    return app


def start_app(app, config_class=Config):
    socketio.run(app, debug=True, host='0.0.0.0', port=2674)
