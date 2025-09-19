from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, SelectField, FloatField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from app import User, CorrectionFactor

class FactorForm(FlaskForm):
    # e.g., 'sep/25'
    month_year = StringField('Month/Year (e.g., sep/25)', validators=[DataRequired(), Length(min=6, max=7)])
    value = FloatField('Factor Value', validators=[DataRequired()])
    submit = SubmitField('Save Factor')

    def validate_month_year(self, month_year):
        # This validation is for creating new factors. We'll bypass it for editing.
        if not hasattr(self, 'editing') or not self.editing:
            factor = CorrectionFactor.query.filter_by(month_year=month_year.data).first()
            if factor:
                raise ValidationError('This month/year already has a factor. Please edit the existing one.')

class SimulationForm(FlaskForm):
    server_name = StringField('Server Name', validators=[DataRequired(), Length(min=2, max=100)])
    dob = DateField('Date of Birth', validators=[DataRequired()], format='%Y-%m-%d')
    benefit_type = StringField('Benefit Type', validators=[DataRequired(), Length(min=2, max=100)])
    gender = SelectField('Gender', choices=[('FEMININO', 'Feminino'), ('MASCULINO', 'Masculino')],
                         validators=[DataRequired()])
    submit = SubmitField('Create Simulation')

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
