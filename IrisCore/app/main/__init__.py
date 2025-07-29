from flask import Blueprint

main_blueprint = Blueprint('main', __name__, static_folder='static', template_folder='templates', static_url_path='/main')

from app.main import models, routes, math_worker