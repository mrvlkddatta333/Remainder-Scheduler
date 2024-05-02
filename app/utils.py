from datetime import datetime, timedelta
from app.models import Task, Reminder
from flask import app, current_app
from flask_mail import Message
from app import db, mail
from sqlalchemy.orm import joinedload

def send_reminder_notification(reminder):
    task = reminder.task
    user_email = task.category.owner.email
    current_app.logger.info(f'Sending reminder for task: {task.title} to {user_email}')
    msg = Message(f'Reminder: {task.title}', recipients=[user_email])
    msg.body = f'You have an upcoming task: {task.title}\nDue Date: {task.due_date}\nDescription: {task.description}'
    mail.send(msg)

#10 min before sending remainder
def send_reminders(app):
    with app.app_context():
        try:
            app.logger.info('Sending reminders job started')
    
            reminders = Reminder.query.join(Task).filter(
                Reminder.sent_at.is_(None),
                Reminder.reminder_datetime <= datetime.now() + timedelta(minutes=10),  # Check reminders within 10 minutes
                Task.due_date >= Reminder.reminder_datetime  # Ensure task due date is after the reminder datetime
            ).options(joinedload(Reminder.task)).all()

            app.logger.info(f'Found {len(reminders)} reminders to send')

            for reminder in reminders:
                remaining_time = reminder.reminder_datetime - datetime.now()
                minutes_remaining = int(remaining_time.total_seconds() // 60)

                if minutes_remaining >= 0:
                    app.logger.info(f"Sending reminder for {reminder.task.category.owner.username}:")
                    app.logger.info(f"- Task: {reminder.task.description}")
                    app.logger.info(f"- Due Date: {reminder.task.due_date}")
                    app.logger.info(f"- Reminder Date: {reminder.reminder_datetime}")
                    app.logger.info(f"- Remaining Time: {minutes_remaining} minutes")

                    send_reminder_notification(reminder)
                    reminder.sent_at = datetime.now()
                    db.session.add(reminder)

            db.session.commit()
            app.logger.info('Sending reminders job finished')

        except Exception as e:
            app.logger.error(f'Error occurred during sending reminders: {str(e)}')
            db.session.rollback()

#--------------------------------------------------------------
#exact time sending remainder
# def send_reminders(app):
#     with app.app_context():
#         try:
#             app.logger.info('Sending reminders job started')
    
#             reminders = Reminder.query.join(Task).filter(
#                 Reminder.sent_at.is_(None),
#                 Reminder.reminder_datetime <= datetime.now(),  # Check for exact match with current time
#                 Task.due_date >= Reminder.reminder_datetime  # Ensure task due date is after or same as the reminder datetime
#             ).options(joinedload(Reminder.task)).all()

#             app.logger.info(f'Found {len(reminders)} reminders to send')

#             for reminder in reminders:
#                 if reminder.reminder_datetime == datetime.now():
#                     app.logger.info(f"Sending reminder for {reminder.task.category.owner.username}:")
#                     app.logger.info(f"- Task: {reminder.task.description}")
#                     app.logger.info(f"- Due Date: {reminder.task.due_date}")
#                     app.logger.info(f"- Reminder Date: {reminder.reminder_datetime}")

#                     send_reminder_notification(reminder)
#                     reminder.sent_at = datetime.now()
#                     db.session.add(reminder)

#             db.session.commit()
#             app.logger.info('Sending reminders job finished')

#         except Exception as e:
#             app.logger.error(f'Error occurred during sending reminders: {str(e)}')
#             db.session.rollback()
# def send_reminders(app):
#     with app.app_context():
#         try:
#             app.logger.info('Sending reminders job started')
    
#             reminders = Reminder.query.join(Task).filter(
#                 Reminder.sent_at.is_(None),
#                 Reminder.reminder_datetime <= datetime.now() + timedelta(minutes=0),  # Check reminders at exact time
#                 Task.due_date >= Reminder.reminder_datetime  # Ensure task due date is after the reminder datetime
#             ).options(joinedload(Reminder.task)).all()

#             app.logger.info(f'Found {len(reminders)} reminders to send')

#             for reminder in reminders:
#                 remaining_time = reminder.reminder_datetime - datetime.now()
#                 minutes_remaining = int(remaining_time.total_seconds() // 60)

#                 if minutes_remaining >= 0:
#                     app.logger.info(f"Sending reminder for {reminder.task.category.owner.username}:")
#                     app.logger.info(f"- Task: {reminder.task.description}")
#                     app.logger.info(f"- Due Date: {reminder.task.due_date}")
#                     app.logger.info(f"- Reminder Date: {reminder.reminder_datetime}")
#                     app.logger.info(f"- Remaining Time: {minutes_remaining} minutes")

#                     send_reminder_notification(reminder)
#                     reminder.sent_at = datetime.now()
#                     db.session.add(reminder)

#             db.session.commit()
#             app.logger.info('Sending reminders job finished')

#         except Exception as e:
#             app.logger.error(f'Error occurred during sending reminders: {str(e)}')
#             db.session.rollback()
#--------------------------------------------------------------

def send_password_reset_email(email, reset_url):
    msg = Message('Reset Your Password', recipients=[email])
    msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request, please ignore this email.
'''
    mail.send(msg)


def get_upcoming_tasks(user):
    now = datetime.utcnow()
    tasks = user.tasks.filter(Task.due_date >= now).order_by(Task.due_date).all()
    return tasks