import atexit
import os
import sys
from flask import Flask
from utils.modules.lifecycle import AppLifecycle
from config import Config
from flask_moment import Moment
from flask_socketio import SocketIO

moment = Moment()
socketio = SocketIO()
lifecycle = AppLifecycle()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    moment.init_app(app)
    socketio.init_app(app)

    from app.main import main_blueprint as bp_main
    app.register_blueprint(bp_main)
    
    from utils import debug
    debug.LoadConfig(config_class)

    lifecycle.init_app(app)
    return app


def initialize_runtime():
    lifecycle.initialize()
    def shutdown():
        lifecycle.shutdown()
    atexit.register(shutdown)

def start_app(app):
    initialize_runtime()
    socketio.run(app, debug=True, use_reloader=False, host='0.0.0.0', port=2674)
