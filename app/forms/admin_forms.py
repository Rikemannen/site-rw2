from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, BooleanField, SelectMultipleField
from wtforms.widgets import CheckboxInput, ListWidget
from wtforms.validators import DataRequired, Length

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
