# config.py

import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'mysql://{}:{}@{}:{}/{}'.format(os.environ.get('DB_USERNAME', 'root'),
                                    os.environ.get('DB_PASSWORD', 'admin'),
                                    os.environ.get('DB_HOST', 'localhost'),
                                    os.environ.get('DB_PORT', '3306'),
                                    os.environ.get('DB_NAME', 'scheduler_db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'  # Default to Gmail SMTP server
    MAIL_PORT = 587 # Default to Gmail SMTP port
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'bchag4102@gmail.com'  # Default to your Gmail email address
    MAIL_PASSWORD = 'wbwu lnzs ncrn xtle'  # Default to your Gmail password
    ADMINS = 'bchag4102@gmail.com' # Your email address for receiving error logs

    MAIL_DEFAULT_SENDER = 'bchag4102@gmail.com'