from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SelectMultipleField, IntegerField, TimeField, RadioField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class ProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    bio = TextAreaField('Bio', validators=[Length(max=500)])
    goals = TextAreaField('Goals', validators=[Length(max=500)])
    skills = SelectMultipleField('Skills', coerce=int)
    submit = SubmitField('Update Profile')

class AdminUserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    role = SelectField('Role', choices=[('admin', 'Admin'), ('mentor', 'Mentor'), ('mentee', 'Mentee')], validators=[DataRequired()])
    password = PasswordField('Password')
    submit = SubmitField('Save')

class MentorshipRequestForm(FlaskForm):
    message = TextAreaField('Message (optional)', validators=[Length(max=500)])
    submit = SubmitField('Send Request')

class AvailabilityForm(FlaskForm):
    day_of_week = SelectField('Day', choices=[
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday')
    ], validators=[DataRequired()])
    start_time = TimeField('Start Time', format='%H:%M', validators=[DataRequired()])
    end_time = TimeField('End Time', format='%H:%M', validators=[DataRequired()])
    submit = SubmitField('Add Availability')

class SessionFeedbackForm(FlaskForm):
    feedback = TextAreaField('Feedback', validators=[Length(max=500)])
    rating = RadioField('Rating', choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')], validators=[DataRequired()])
    submit = SubmitField('Submit Feedback')