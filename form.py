from flask_wtf import FlaskForm
from wtforms import MultipleFileField, SelectMultipleField

class Organ(FlaskForm):
    organ1 = MultipleFileField('Tubuh', SelectMultipleField(True))

