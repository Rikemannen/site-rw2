from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo

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

class RecoveryForm(FlaskForm):
    """Form for account recovery"""
    new_password = PasswordField('Nytt Lösenord', validators=[DataRequired()])
    confirm_password = PasswordField('Bekräfta Lösenord', validators=[
        DataRequired(),
        EqualTo('new_password', message='Lösenorden matchar inte.')
    ])
    submit = SubmitField('Återställ')
