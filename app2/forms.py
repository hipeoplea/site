from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class UserForm(FlaskForm):
    comand_name = StringField('team_name', validators=[DataRequired()])
    username = StringField('nickname', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('submit')


class AdminForm(FlaskForm):
    ad_username = StringField('nickname', validators=[DataRequired()])
    ad_password = PasswordField('password', validators=[DataRequired()])
    ad_submit = SubmitField('submit')
