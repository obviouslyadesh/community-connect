# app/forms.py - UPDATED WITH NEW FORMS
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DateTimeField, IntegerField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange
from datetime import datetime

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    user_type = SelectField('Account Type', choices=[('volunteer', 'Volunteer'), ('organization', 'Organization')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        from app.models import User
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        from app.models import User
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Link')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class ChangeUsernameForm(FlaskForm):
    new_username = StringField('New Username', validators=[DataRequired(), Length(min=3, max=80)])
    submit = SubmitField('Change Username')
    
    def validate_new_username(self, new_username):
        from app.models import User
        user = User.query.filter_by(username=new_username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    date = StringField('Event Date & Time', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired(), Length(max=300)])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    state = StringField('State', validators=[DataRequired(), Length(max=100)])
    zip_code = StringField('ZIP Code', validators=[DataRequired(), Length(max=20)])
    max_volunteers = IntegerField('Maximum Volunteers', default=10, 
                                  validators=[DataRequired(), NumberRange(min=1, max=100, message='Must be between 1 and 100')])
    submit = SubmitField('Create Event')
    
    def validate_date(self, date):
        try:
            event_datetime = datetime.strptime(date.data, '%Y-%m-%dT%H:%M')
            current_datetime = datetime.now()
            if event_datetime < current_datetime:
                raise ValidationError('Event date must be in the future.')
        except ValueError:
            pass
    
    def validate_max_volunteers(self, max_volunteers):
        if max_volunteers.data <= 0:
            raise ValidationError('Maximum volunteers must be greater than 0.')