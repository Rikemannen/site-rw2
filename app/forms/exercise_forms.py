from wtforms import StringField, FileField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length
from flask_wtf import FlaskForm

class CreateExerciseForm(FlaskForm):
    """Form for creating a new exercise."""
    name = StringField('Namn', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Beskrivning', validators=[DataRequired(), Length(max=500)])
    answers = FileField('Svar (.json)', render_kw={"accept": ".json"}, validators=[DataRequired()])
    html = FileField('Utseende (.html)', render_kw={"accept": ".html"}, validators=[DataRequired()])
    submit = SubmitField('Skapa Övning')

class EditExerciseForm(FlaskForm):
    """Form for editing an existing exercise."""
    name = StringField('Namn', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Beskrivning', validators=[DataRequired(), Length(max=500)])
    answers = FileField('Svar (.json)', render_kw={"accept": ".json"})
    html = FileField('Utseende (.html)', render_kw={"accept": ".html"})
    submit = SubmitField('Uppdatera Övning')

class DeleteExerciseForm(FlaskForm):
    """Form for deleting an exercise."""
    submit = SubmitField('Ta Bort Övning')