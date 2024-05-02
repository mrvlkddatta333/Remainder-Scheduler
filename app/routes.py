# app/routes.py

import io
from flask import Blueprint, make_response, render_template, redirect, send_file, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from app.models import File, User, Category, Task, Reminder
from app.forms import ForgotPasswordForm, LoginForm, RegistrationForm, CategoryForm, ResetPasswordForm, TaskForm, ReminderForm, SearchForm, EditProfileForm, ChangePasswordForm, FilterForm
from app import db
from sqlalchemy import or_
from datetime import datetime, timedelta
from app.utils import send_password_reset_email, send_reminder_notification
import os
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from sqlalchemy.exc import IntegrityError
from datetime import datetime

main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user)
        return redirect(url_for('main.index'))
    return render_template('login.html', title='Sign In', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, first_name=form.first_name.data, last_name=form.last_name.data, phone_number=form.phone_number.data, preferences=form.preferences.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Register', form=form)

@main_bp.route('/', methods=['GET'])
@main_bp.route('/index', methods=['GET'])
def index():
    return render_template('index.html', title='Home')

@main_bp.route('/categories', methods=['GET', 'POST'])
@login_required
def categories():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data, category_type=form.category_type.data, owner=current_user)
        db.session.add(category)
        db.session.commit()
        flash('New category created!')
        return redirect(url_for('main.categories'))
    categories = current_user.categories.all()
    return render_template('categories.html', title='Categories', form=form, categories=categories)

@main_bp.route('/tasks/<category_id>', methods=['GET', 'POST'])
@login_required
def tasks(category_id):
    form = TaskForm()
    category = Category.query.get_or_404(category_id)
    if form.validate_on_submit():
        task = Task(title=form.title.data, description=form.description.data, due_date=form.due_date.data, category=category)
        db.session.add(task)
        db.session.flush()  # Flush to get the task.id

        for attachment in form.attachments.data:
            if attachment:
                file = File(
                    file_name=attachment.filename,
                    file_data=attachment.read(),
                    file_type=attachment.content_type,
                    task_id=task.id
                )
                db.session.add(file)

        db.session.commit()
        flash('New task created!')
        return redirect(url_for('main.tasks', category_id=category_id))

    tasks = category.tasks.all()
    return render_template('tasks.html', title='Tasks', form=form, tasks=tasks, category=category)

@main_bp.route('/download/<int:file_id>', methods=['GET'])
@login_required
def download_file(file_id):
    file = File.query.get_or_404(file_id)
    view_in_browser = request.args.get('view', False)

    if view_in_browser:
        response = make_response(file.file_data)
        response.headers.set('Content-Type', file.file_type)
        return response

    response = make_response(file.file_data)
    response.headers.set('Content-Type', file.file_type)
    response.headers.set('Content-Disposition', 'attachment', filename=file.file_name)
    return response

@main_bp.route('/reminders/<task_id>', methods=['GET', 'POST'])
@login_required
def reminders(task_id):
    form = ReminderForm()
    task = Task.query.get_or_404(task_id)
    if form.validate_on_submit():
        reminder = Reminder(reminder_datetime=form.reminder_datetime.data, task=task)
        db.session.add(reminder)
        db.session.commit()
        flash('New reminder set!')
        # send_reminder_notification(reminder)
        return redirect(url_for('main.reminders', task_id=task_id))
    reminders = task.reminders.all()
    return render_template('reminders.html', title='Reminders', form=form, reminders=reminders, task=task)

@main_bp.route('/events', methods=['GET', 'POST'])
@login_required
def events():
    form = FilterForm()
    tasks_query = current_user.get_upcoming_tasks()

    if form.validate_on_submit():
        category_id = form.category.data
        due_date_from = form.due_date_from.data
        due_date_to = form.due_date_to.data
        custom_filter = form.custom_filter.data.lower()

        if category_id:
            tasks_query = tasks_query.filter(Task.category_id == category_id)
        if due_date_from:
            tasks_query = tasks_query.filter(Task.due_date >= due_date_from)
        if due_date_to:
            tasks_query = tasks_query.filter(Task.due_date <= due_date_to)
        if custom_filter:
            tasks_query = tasks_query.filter(
                or_(Task.title.ilike(f'%{custom_filter}%'),
                    Task.description.ilike(f'%{custom_filter}%'),
                    Category.name.ilike(f'%{custom_filter}%'))
            )

    tasks = tasks_query.all()

    return render_template('events.html', title='Upcoming Events', tasks=tasks, form=form)

@main_bp.route('/events/search', methods=['GET', 'POST'])
@login_required
def search_events():
    form = SearchForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            search_query = form.search_query.data
            tasks = Task.query.join(Category).filter(
                Category.user_id == current_user.id,
                Task.due_date >= datetime.utcnow(),
                (Task.title.like(f'%{search_query}%') |
                 Task.description.like(f'%{search_query}%') |
                 Category.name.like(f'%{search_query}%'))
            ).all()
            return render_template('events.html', title='Upcoming Events', tasks=tasks)
    return render_template('search_events.html', title='Search Events', form=form)

@main_bp.route('/categories/<category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.name = form.name.data
        category.category_type = form.category_type.data
        db.session.commit()
        flash('Category updated successfully!')
        return redirect(url_for('main.categories'))
    return render_template('edit_category.html', title='Edit Category', form=form, category=category)

@main_bp.route('/categories/<category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)

    # Delete associated tasks and their related objects
    for task in category.tasks:
        for reminder in task.reminders:
            db.session.delete(reminder)
        for file in task.files:
            db.session.delete(file)
        db.session.delete(task)

    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!')
    return redirect(url_for('main.categories'))

@main_bp.route('/tasks/<task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    form = TaskForm(obj=task)
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.due_date = form.due_date.data

        # Delete existing files
        for file in task.files:
            db.session.delete(file)

        # Add new files
        for attachment in form.attachments.data:
            if attachment:
                file = File(
                    file_name=attachment.filename,
                    file_data=attachment.read(),
                    file_type=attachment.content_type,
                    task_id=task.id
                )
                db.session.add(file)

        db.session.commit()
        flash('Task updated successfully!')
        return redirect(url_for('main.tasks', category_id=task.category_id))
    return render_template('edit_task.html', title='Edit Task', form=form, task=task)

@main_bp.route('/tasks/<task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    category_id = task.category_id

    # Delete associated reminders
    for reminder in task.reminders:
        db.session.delete(reminder)

    # Delete associated files
    for file in task.files:
        db.session.delete(file)

    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!')
    return redirect(url_for('main.tasks', category_id=category_id))

@main_bp.route('/reminders/<reminder_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_reminder(reminder_id):
    reminder = Reminder.query.get_or_404(reminder_id)
    form = ReminderForm(obj=reminder)
    if form.validate_on_submit():
        reminder.reminder_datetime = form.reminder_datetime.data
        db.session.commit()
        flash('Reminder updated successfully!')
        return redirect(url_for('main.reminders', task_id=reminder.task_id))
    return render_template('edit_reminder.html', title='Edit Reminder', form=form, reminder=reminder)

@main_bp.route('/reminders/<reminder_id>/delete', methods=['POST'])
@login_required
def delete_reminder(reminder_id):
    reminder = Reminder.query.get_or_404(reminder_id)
    task_id = reminder.task_id
    db.session.delete(reminder)
    db.session.commit()
    flash('Reminder deleted successfully!')
    return redirect(url_for('main.reminders', task_id=task_id))

def handle_unique_constraint_violation(error, field_name):
    if f"user.ix_user_{field_name}" in str(error):
        flash(f"The {field_name} you entered is already registered. Please choose a different one.", "error")
    else:
        flash("An unexpected error occurred. Please try again later.", "error")

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)

    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()

        if existing_user and existing_user != current_user:
            flash('That username is already taken. Please choose a different one.', 'error')
            return redirect(url_for('auth.edit_profile'))

        try:
            current_user.username = form.username.data
            current_user.email = form.email.data
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            current_user.phone_number = form.phone_number.data
            current_user.preferences = form.preferences.data
            db.session.commit()
            flash('Your profile has been updated.', 'success')
            return redirect(url_for('main.index'))
        except IntegrityError as e:
            db.session.rollback()
            handle_unique_constraint_violation(e, "email")
            handle_unique_constraint_violation(e, "phone_number")

    return render_template('edit_profile.html', title='Edit Profile', form=form)

@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.get(current_user.id)
        if user.check_password(form.current_password.data):
            user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been changed successfully.', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid current password.', 'error')
    return render_template('change_password.html', title='Change Password', form=form)

# app/routes.py
@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.get_reset_password_token()
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            send_password_reset_email(user.email, reset_url)
            flash('An email with instructions to reset your password has been sent to you.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid email address.', 'error')
    return render_template('forgot_password.html', title='Forgot Password', form=form)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.verify_reset_password_token(token)
    if not user:
        flash('Invalid or expired token.', 'error')
        return redirect(url_for('auth.login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.new_password.data)
        db.session.commit()
        flash('Your password has been reset.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', title='Reset Password', form=form, token=token)