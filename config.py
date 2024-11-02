# config.py
import os
from dotenv import load_dotenv

<<<<<<< HEAD
# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')  # Default key for development
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///site.db')  # Default to SQLite
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable modification tracking for performance
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads/')  # Default upload folder
=======
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'upload_files')
    ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'png,jpg,jpeg,gif').split(','))
>>>>>>> master
