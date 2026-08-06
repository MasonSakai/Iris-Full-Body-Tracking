from __future__ import annotations
import hashlib
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FloatField, BooleanField, SelectField, ValidationError
from flask_wtf.file import MultipleFileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired, NumberRange

from utils.registry import ThingDatabase

class CameraForm(FlaskForm):

	def __init__(self, existing_cam: Camera = None, **kwargs):
		super().__init__(**kwargs)
		self.existing_cam = existing_cam

	display_name = StringField('Camera Name', validators=[DataRequired()])
	submit = SubmitField('Confirm')

	def validate_display_name(self, field: StringField):
		if self.existing_cam and field.data == self.existing_cam.display_name:
			return

		for thing in ThingDatabase(Camera).AllThingsListForReading():
			if thing.display_name == field.data:
				raise ValidationError('Name matches existing camera')

class FileUploadForm(FlaskForm):

	image_files = MultipleFileField('Image Files', validators=[
		FileRequired(),
		FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
	])

class CalibrationConfigForm(FlaskForm):
	
	checkerboard_x = IntegerField('Width', validators=[DataRequired(), NumberRange(min=1)])
	checkerboard_y = IntegerField('Height', validators=[DataRequired(), NumberRange(min=1)])

class CameraReferenceForm(FlaskForm):

	autostart = BooleanField('Auto-start')

	submit = SubmitField('Confirm')

class NewLocalReferenceForm(CameraReferenceForm):

	def hashname(name: str, ident: str) -> str:
		return f"{name} ({ hashlib.sha256(ident.encode('utf-8')).hexdigest()[:4] })"
	
	def __init__(self, options: list[tuple[CameraIdent, CameraInfo]], *args, **kwargs):
		super().__init__(*args, **kwargs)

		choices = {}
		for [ident, info] in options:
			s_ident = ':'.join([str(v) if v != None else '' for v in ident])
			name = info.name
			if name in choices:
				if choices[name] == '':
					name = NewLocalReferenceForm.hashname(name, s_ident)
				elif choices[name] != s_ident:
					o_ident = choices[name]
					o_name = NewLocalReferenceForm.hashname(name, o_ident)
					choices[o_name] = o_ident
					choices[name] = ''
					name = NewLocalReferenceForm.hashname(name, s_ident)
			choices[name] = s_ident

		self.ident.choices = [('', 'Please Select'), *[(v, k) for k, v in choices.items() if v != '']]

	ident = SelectField('Identifier', choices=[], validators=[DataRequired()])

	submit = SubmitField('Create')

	
from app.cameras.models import Camera, CameraIdent, CameraInfo, CameraReference