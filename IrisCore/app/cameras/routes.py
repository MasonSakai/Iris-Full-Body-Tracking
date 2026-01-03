from flask import render_template, flash, redirect, url_for, jsonify, request, abort

from app.cameras import cam_blueprint as bp_cam
from app.cameras.models import Camera


@bp_cam.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')
