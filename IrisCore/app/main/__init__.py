from flask import Blueprint

main_blueprint = Blueprint('main', __name__)

from app.main import models, routes