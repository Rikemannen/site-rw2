from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, BooleanField, SelectMultipleField, IntegerField, TextAreaField, ColorField
from wtforms.widgets import CheckboxInput, ListWidget
from wtforms.validators import DataRequired, Length

# User forms

class ProfileSettingsForm(FlaskForm):
    """Form for profile settings."""
    display_name = StringField('Visningsnamn', validators=[Length(max=20)])
    emblem = SelectField('Utrustad Emblem', coerce=int, choices=[])
    submit = SubmitField('Uppdatera')

class EmblemAssignmentForm(FlaskForm):
    """Add an emblem to a user's "inventory"."""
    emblems = SelectMultipleField('Tillgängliga emblem', coerce=int, option_widget=CheckboxInput(), widget=ListWidget(prefix_label=False))
    submit = SubmitField('Uppdatera')

class UsernameChangeForm(FlaskForm):
    """Form for changing username."""
    username = StringField('Användarnamn', validators=[DataRequired(), Length(min=3, max=20)])
    submit = SubmitField('Uppdatera')

class PasswordResetForm(FlaskForm):
    """Form for creating password/account recovery link."""
    submit = SubmitField('Skapa Återställningslänk')

class DeleteUserForm(FlaskForm):
    """Form for deleting account."""
    submit = SubmitField('Ta bort kontot')

class VerifyUserForm(FlaskForm):
    """Form for verifying/unverifying user."""
    verified = BooleanField('Verifierad')
    submit = SubmitField('Uppdatera')

class ElevateUserForm(FlaskForm):
    """Form for giving a user admin rights."""
    admin = BooleanField('Admin')
    submit = SubmitField('Uppdatera (Bara om du litar på denna användare!)')

# Exercise forms

class ExerciseInfoForm(FlaskForm):
    """Form for setting basic data, name and description."""
    name = StringField('Namn', validators=[DataRequired()])
    description = StringField('Beskrivning', validators=[DataRequired()])
    submit = SubmitField('Uppdatera')

class ExerciseDataForm(FlaskForm):
    """Form for setting static data, owner_id, created (date+time), approval status."""
    owner = IntegerField('Ägare (id)', validators=[DataRequired()])
    created = IntegerField('Skapad (unix)', validators=[DataRequired()])
    approved = BooleanField('Godkänd')
    submit = SubmitField('Uppdatera')

class ExerciseStatisticForm(FlaskForm):
    """Form for setting statistic data, attempts, finished."""
    attempts = IntegerField('Försök', validators=[DataRequired()])
    completions = IntegerField('Avklarad', validators=[DataRequired()])
    submit = SubmitField('Uppdatera')

class ExerciseAnswerForm(FlaskForm):
    """Form for editing correct answers. (raw json)"""
    json = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Uppdatera')

class ExerciseHTMLForm(FlaskForm):
    """Form for editing exercise html."""
    html = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Uppdatera')

class DeleteExerciseForm(FlaskForm):
    """Form for deleting an exercise."""
    submit = SubmitField('Ta bort övning')

# Emblem forms

class EmblemAppearanceForm(FlaskForm):
    """Form for changing emblem appearance."""
    name = StringField('Namn', validators=[DataRequired()])
    color = ColorField('Färg', validators=[DataRequired()])
    submit = SubmitField('Uppdatera')

class DeleteEmblemForm(FlaskForm):
    """Form for deleting an emblem."""
    submit = SubmitField('Ta bort emblem')

class EmblemCreationForm(FlaskForm):    # Used in separate template
    """Form for creating an emblem"""
    name = StringField('Namn', validators=[DataRequired()])
    color = ColorField('Färg', validators=[DataRequired()])
    submit = SubmitField('Skapa')
