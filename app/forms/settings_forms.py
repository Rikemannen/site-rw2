from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo

class ProfileSettingsForm(FlaskForm):
    """Form for profile settings."""
    display_name = StringField('Visningsnamn', validators=[Length(max=20)])
    emblem = SelectField('Utrustad Emblem', coerce=int, choices=[])
    submit = SubmitField('Uppdatera Profil')

class UsernameChangeForm(FlaskForm):
    """Form for changing username."""
    username = StringField('Användarnamn', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Lösenord', validators=[DataRequired(), Length(min=8, max=100)])
    submit = SubmitField('Uppdatera Användarnamn')

class PasswordChangeForm(FlaskForm):
    """For for changing password."""
    current_password = PasswordField('Nuvarande Lösenord', validators=[
        DataRequired(),
        Length(min=8, max=100)
    ])
    new_password = PasswordField('Nytt Lösenord', validators=[DataRequired()])
    confirm_password = PasswordField('Bekräfta Lösenord', validators=[
        DataRequired(),
        EqualTo('new_password', message='Lösenorden matchar inte.')
    ])
    submit = SubmitField('Uppdatera Lösenord')

class DeleteUserForm(FlaskForm):
    """Form for deleting account."""
    username = StringField('Användarnamn', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Lösenord', validators=[DataRequired(), Length(min=8, max=100)])
    confirm = BooleanField('Jag förstår att detta inte går att göra om.', validators=[DataRequired()])
    submit = SubmitField('Ta bort konto')
