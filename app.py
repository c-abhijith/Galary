from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
import os

# Initialize the database object
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configure your app
    app.config['SECRET_KEY'] = 'your_secret_key'  # Use environment variables for sensitive info
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://newdb_7uox_user:1Zr2DXeq0EHtC7GHA0RFucaUBgae4HJg@dpg-csg2oitds78s73e9bu50-a.oregon-postgres.render.com/newdb_7uox'
    
    db.init_app(app)
    csrf = CSRFProtect(app)
    migrate = Migrate(app, db)

    # Ensure the upload directory exists
    UPLOAD_FOLDER = 'static/uploads/'  # Adjust the path as needed
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # Import routes after app context is created
    from routes import setup_routes
    setup_routes(app)

    return app

# Create tables
with app.app_context():
    db.create_all()

# Run the application
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
