from flask_wtf import FlaskForm
from pupil_apriltags import Detector
from wtforms import StringField, SubmitField, IntegerField, FloatField, BooleanField, ValidationError
from wtforms.validators import DataRequired, NumberRange, Regexp

from app.apriltag.models import AprilTag, AprilTagDetector
from utils.registry import ThingDatabase

class DetectorForm(FlaskForm):

	
	def __init__(self, existing_detector: AprilTagDetector = None, **kwargs):
		super().__init__(**kwargs)
		self.existing_detector = existing_detector
	
	families = StringField('Tag Families', validators=[DataRequired(),
													   Regexp(r'^[a-zA-Z0-9\s]+$', message="Tag families must be separated only by spaces")])
	nthreads = IntegerField('Number of threads', validators=[NumberRange(min=1)])
	quad_decimate = FloatField('Quad Decimate', validators=[NumberRange(min=0)])
	quad_sigma = FloatField('Quad Sigma', validators=[NumberRange(min=0)])
	refine_edges = BooleanField('Refine Edges')
	decode_sharpening = FloatField('Decode Sharpening', validators=[NumberRange(min=0)])
	default_tag_size = FloatField('Default tag size (cm)', validators=[NumberRange(min=0)])

	submit = SubmitField('Confirm')

	def validate_families(self, field: StringField):
		for thing in ThingDatabase(AprilTagDetector).AllThingsListForReading():
			if thing != self.existing_detector and thing.families == field.data:
				raise ValidationError('Families match existing detector')

		try:
			Detector(families=field.data)
		except Exception as ex:
			raise ValidationError(str(ex))

class CreateDetectorForm(DetectorForm):
	
	display_name = StringField('Detector Name', validators=[DataRequired()])
	submit = SubmitField('Create')

	def validate_display_name(self, field: StringField):
		for thing in ThingDatabase(AprilTagDetector).AllThingsListForReading():
			if thing.display_name == field.data:
				raise ValidationError('Name matches existing detector')

class TagForm(FlaskForm):
	
	def __init__(self, existing_tag: AprilTag = None, **kwargs):
		super().__init__(**kwargs)
		self.existing_tag = existing_tag

	display_name = StringField('Display Name', validators=[DataRequired()])
	tag_size = FloatField('Tag Size (cm)', validators=[NumberRange(min=0)])

	submit = SubmitField('Create')

	def validate_display_name(self, field: StringField):
		for thing in ThingDatabase(AprilTag).AllThingsListForReading():
			if thing != self.existing_tag and thing.display_name == field.data:
				raise ValidationError('Name matches existing detector')
	
class EditTagForm(TagForm):
	ensure_static = BooleanField('Ensure Static')
	submit = SubmitField('Submit')