from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

class SendMessageForm(FlaskForm):
    """Form for sending a message."""
    recipient = SelectField('Mottagare', coerce=int, choices=[])
    content = TextAreaField('Meddelande', validators=[DataRequired(), Length(max=500, min=1)])
    send = SubmitField('Skicka')
