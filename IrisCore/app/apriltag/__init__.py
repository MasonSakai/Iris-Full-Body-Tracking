from flask import Blueprint

apriltag_blueprint = Blueprint('apriltag', __name__, static_folder='static', template_folder='templates', url_prefix='/apriltag')

from app.apriltag import models, routes