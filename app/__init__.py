from flask import Flask
from flask_migrate import Migrate
from .models import db  # Import the database instance
from .routes import register_routes  # Import the function to register routes

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'  # Use environment variables for sensitive info
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://newdb_7uox_user:1Zr2DXeq0EHtC7GHA0RFucaUBgae4HJg@dpg-csg2oitds78s73e9bu50-a.oregon-postgres.render.com/newdb_7uox'

    # Initialize database and migration
    db.init_app(app)
    migrate = Migrate(app, db)

    # Register routes
    register_routes(app)

    return app
