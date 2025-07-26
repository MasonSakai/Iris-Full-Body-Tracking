from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FloatField, BooleanField
from wtforms.validators import DataRequired, NumberRange

from app import db
from app.apriltag.models import AprilTagDetector, AprilTag
import sqlalchemy as sqla

class DetectorForm(FlaskForm):
    
    families = StringField('Tag Families', validators=[DataRequired()])
    nthreads = IntegerField('Number of threads', validators=[NumberRange(min=1)])
    quad_decimate = FloatField('Quad Decimate', validators=[NumberRange(min=0)])
    quad_sigma = FloatField('Quad Sigma', validators=[NumberRange(min=0)])
    refine_edges = BooleanField('Refine Edges')
    decode_sharpening = FloatField('Decode Sharpening', validators=[NumberRange(min=0)])
    default_tag_size = FloatField('Default tag size (cm)', validators=[NumberRange(min=0)])

    submit = SubmitField('Submit')

    #add families validator to prevent duplicates?

class FoundTagForm(FlaskForm):
    
    display_name = StringField('Display Name', validators=[DataRequired()])
    tag_size = FloatField('Tag Size (cm)', validators=[NumberRange(min=0)])

    submit = SubmitField('Create')
    
class EditTagForm(FoundTagForm):

    submit = SubmitField('Submit')