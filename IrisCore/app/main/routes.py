from flask import render_template, flash, redirect, url_for, jsonify, request, abort
import sqlalchemy as sqla

from app import db
from app.main import main_blueprint as bp_main
#from app.main.models import ResearchField, ProgrammingLanguage, ResearchPosition, ResearchApplication


@bp_main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@bp_main.app_errorhandler(404)
def err404(error):
    return {}, 404


#@bp_main.route('/fields/list')
#def rf_list():
#    data = []
#    
#    fields = db.session.scalars(sqla.select(ResearchField)).all()
#    for field in fields:
#        data.append({
#            'id': field.id,
#            'title': field.title,
#            'position_count': len(db.session.scalars(field.positions.select()).all()),
#            'student_count': len(db.session.scalars(field.students.select()).all())
#        })

#    return jsonify(data)


#@bp_main.route('/positions/<pos_id>')
#def view_position(pos_id):
#    return render_template('_research.html',
#                           research_pos=db.session.get(ResearchPosition, pos_id))