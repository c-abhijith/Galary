from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy
migrate = Migrate()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)

