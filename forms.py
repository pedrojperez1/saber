from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Email, Length
from models import State, Official

class QuestionForm(FlaskForm):
    """Form for adding questions."""

    official = SelectField('Official', validate_choice=False)
    text = TextAreaField('Text', validators=[DataRequired()])


class UserForm(FlaskForm):
    """Form for adding users."""
    def enabled_states():
        return State.query.all()

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('Profile Image URL')
    city = StringField('City', validators=[DataRequired()])
    state = QuerySelectField(
        'State', 
        query_factory=enabled_states,
        get_label='name',
        validators=[DataRequired()]
    )

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

