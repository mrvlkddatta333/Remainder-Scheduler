# app/forms.py

from flask_wtf import FlaskForm
from wtforms import DateTimeLocalField, FieldList, SelectField, StringField, PasswordField, SubmitField, TextAreaField, DateField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from flask_wtf.file import FileAllowed

from app.models import Category

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone_number = StringField('Phone Number')
    preferences = TextAreaField('Preferences')
    submit = SubmitField('Register')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone_number = StringField('Phone Number')
    preferences = TextAreaField('Preferences')
    submit = SubmitField('Update Profile')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField('Change Password')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Reset Password')

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(max=64)])
    category_type = StringField('Category Type', validators=[DataRequired(), Length(max=64)])
    submit = SubmitField('Create Category')

class TaskForm(FlaskForm):
    title = StringField('Task Title', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Task Description')
    due_date = DateField('Due Date', validators=[DataRequired()])
    attachments = FieldList(FileField('Attachments'), min_entries=1)
    submit = SubmitField('Create Task')

from wtforms import IntegerField, validators

class ReminderForm(FlaskForm):
    reminder_datetime = DateTimeLocalField('Reminder Date and Time', validators=[DataRequired()])
    submit = SubmitField('Set Reminder')

class SearchForm(FlaskForm):
    search_query = StringField('Search Query', validators=[DataRequired()])
    submit = SubmitField('Search')

class FilterForm(FlaskForm):
    category = SelectField('Category', coerce=int)
    due_date_from = DateField('From Date', validators=[Optional()])
    due_date_to = DateField('To Date', validators=[Optional()])
    custom_filter = StringField('Custom Filter', validators=[Optional()])
    submit = SubmitField('Apply Filter')

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.category.choices = [(0, 'All Categories')] + [(c.id, c.name) for c in Category.query.all()]