from flask import Blueprint

cam_blueprint = Blueprint('cameras', __name__, static_folder='static', template_folder='templates', static_url_path='/cameras')

from app.cameras import models, routes
