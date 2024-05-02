# app/models.py

import json
import jwt
from datetime import datetime, timedelta
from flask import current_app
from app import db, login_manager
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import relationship
import base64
import urllib.parse

bcrypt = Bcrypt()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    phone_number = db.Column(db.String(20))
    preferences = db.Column(db.Text)
    categories = db.relationship('Category', backref='owner', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def get_upcoming_tasks(self):
        now = datetime.utcnow()
        return Task.query.join(Category).filter(
            Category.user_id == self.id,
            Task.due_date >= now
        ).order_by(Task.due_date)
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': datetime.utcnow() + timedelta(seconds=expires_in)},
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    @staticmethod
    def verify_reset_password_token(token):
        try:
            decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            id = decoded_token['reset_password']
            expiration_time = decoded_token['exp']
        except Exception as e:
            print(f"Error decoding token: {e}")
            return None
        
        if datetime.utcnow() > datetime.fromtimestamp(expiration_time):
            return None

        return User.query.get(id)

    def __repr__(self):
        return f'<User {self.username}>'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    category_type = db.Column(db.String(64))  # e.g., Vehicle Maintenance, Healthcare Appointments, Family Commitments
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tasks = db.relationship('Task', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'
    
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_data = db.Column(db.LargeBinary, nullable=False)
    file_type = db.Column(db.String(255), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)

    def __repr__(self):
        return f'<File {self.file_name}>'

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    attachment = db.Column(db.String(256))  # Path to the attachment file
    files = db.relationship('File', backref='task', lazy='dynamic')
    reminders = db.relationship('Reminder', backref='task', lazy='dynamic')

    def __repr__(self):
        return f'<Task {self.title}>'

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notification_method = db.Column(db.String(64), default='email')
    reminder_datetime = db.Column(db.DateTime, index=True)
    sent_at = db.Column(db.DateTime, index=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))

    def __repr__(self):
        return f'<Reminder for Task {self.task_id}>'