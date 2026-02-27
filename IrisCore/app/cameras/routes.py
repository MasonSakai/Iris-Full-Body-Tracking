from flask import Blueprint, render_template, flash, redirect, url_for, jsonify, request, abort

bp_cam = Blueprint('cameras', __name__, static_folder='static', template_folder='templates', static_url_path='/cameras')

@bp_cam.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')
