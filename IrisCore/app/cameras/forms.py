from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FloatField, BooleanField, SelectField, ValidationError
from flask_wtf.file import MultipleFileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired, NumberRange

from app.cameras.models import Camera
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
    
    submit = SubmitField('Upload')

class CalibrationConfigForm(FlaskForm):
    
    checkerboard_x = IntegerField('Width', validators=[DataRequired(), NumberRange(min=1)])
    checkerboard_y = IntegerField('Height', validators=[DataRequired(), NumberRange(min=1)])