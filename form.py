from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo



class  searchForm(FlaskForm):
    search = StringField('Search here',
                        validators=[DataRequired()])
    submit = SubmitField('search')
