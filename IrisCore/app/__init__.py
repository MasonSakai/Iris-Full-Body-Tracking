import atexit
import os
import sys
from flask import Flask
import numpy as np
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
    
    from utils import debug
    debug.LoadConfig(config_class)
    
    os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
    lifecycle.init_app(app)

    return app


def initialize_runtime(app: Flask):
    lifecycle.initialize()
    def shutdown():
        lifecycle.shutdown()
    atexit.register(shutdown)

    @app.context_processor
    def inject_jinja():
        def form_class(field):
            match(field.type):
                case 'BooleanField':
                    return 'form-check-input'
                case 'SelectField':
                    return 'form-select'
                case _:
                    return 'form-control'

        return {
            'np': np,
            'form_class': form_class,
            'validate_class': (lambda *fields, has_validation=True: 'has-validation' if has_validation and any([field.errors for field in fields]) else ''),
            'invalid_class': (lambda field, has_validation=True: 'is-invalid' if has_validation and field.errors else ''),
            'join_classes': (lambda *classes: ' '.join(classes).strip())
        }

def start_app(app):
    initialize_runtime(app)
    socketio.run(app, debug=True, use_reloader=False, host='0.0.0.0', port=2674)
