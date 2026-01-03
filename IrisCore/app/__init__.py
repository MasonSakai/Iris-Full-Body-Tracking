from flask import Flask
from config import Config
from flask_moment import Moment
from flask_socketio import SocketIO

moment = Moment()
socketio = SocketIO()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    moment.init_app(app)
    socketio.init_app(app)
    
    from utils import debug
    debug.LoadConfig(config_class)

    # blueprint registration
    from app.main import main_blueprint as main
    app.register_blueprint(main)
    from app.main.math_worker import math_worker
    math_worker.init_app(app)

    from app.apriltag import apriltag_blueprint as apriltag
    app.register_blueprint(apriltag)
    
    from utils.modulemanager.IrisModules import getSubModules
    getSubModules(app, config_class)

    #Scribe.loader.InitLoading(config_class.CONFIG_FILE)
    return app


def start_app(app, config_class=Config):

    # Load camera, detector, and AI data and prime mathworker

    socketio.run(app, debug=True, host='0.0.0.0', port=2674)
