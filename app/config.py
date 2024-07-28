import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    INITIAL_USERNAME = os.environ.get('INITIAL_USERNAME')
    INITIAL_PASSWORD = os.environ.get('INITIAL_PASSWORD')
