from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    """Form for user login."""
    username = StringField('Användarnamn', validators=[DataRequired(), Length(min=3, max=25)])
    password = PasswordField('Lösenord', validators=[DataRequired(), Length(min=8, max=100)])
    submit = SubmitField('Logga in')

class SignupForm(FlaskForm):
    """Form for user signup."""
    display_name = StringField('Visningsnamn', validators=[Length(max=50)])
    username = StringField('Användarnamn', validators=[DataRequired(), Length(min=3, max=25)])
    password = PasswordField('Lösenord', validators=[DataRequired(), Length(min=8, max=100)])
    submit = SubmitField('Registrera')

class SettingsForm(FlaskForm):
    """Form for user settings."""
    display_name = StringField('Visningsnamn', validators=[Length(max=50)])
    username = StringField('Användarnamn', validators=[DataRequired(), Length(min=3, max=25)])
    password = PasswordField('Lösenord', validators=[DataRequired(), Length(min=8, max=100)])
    emblem = SelectField('Utrustad Emblem', coerce=int, choices=[])
    submit = SubmitField('Uppdatera Inställningar')