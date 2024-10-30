from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, SubmitField, DecimalField
from wtforms.validators import DataRequired, Email, Length, NumberRange
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from functools import wraps
from flask_migrate import Migrate
import os
from werkzeug.utils import secure_filename
from wtforms import HiddenField

# Initialize Flask app and database
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Use environment variables for sensitive info
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://newdb_7uox_user:1Zr2DXeq0EHtC7GHA0RFucaUBgae4HJg@dpg-csg2oitds78s73e9bu50-a.oregon-postgres.render.com/newdb_7uox'
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
migrate = Migrate(app, db)

UPLOAD_FOLDER = 'static/uploads/'  # Adjust the path as needed
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    like_count = db.Column(db.ARRAY(db.Integer), default=list)  # Array for user IDs who liked the product
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Foreign key to User model
    image_file = db.Column(db.String(100), nullable=False)  # Field for storing image filenames

    user = db.relationship('User', backref='products')  # Relationship to User model

    def __repr__(self):
        return f'<Product {self.name}>'

# Create tables
with app.app_context():
    db.create_all()

# Decorators for login and logout requirements
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:  # Check if user is logged in
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:  # Prevent logged-in users from accessing certain routes
            flash("You are already logged in.", "info")
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# Forms for user signup and login
class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class PictureForm(FlaskForm):
    name = StringField('Picture Name', validators=[DataRequired(), Length(min=1, max=100)])
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0)], places=2)
    submit = SubmitField('Add Picture')

class ToggleLikeForm(FlaskForm):
    user_id = HiddenField()

# Route for user signup
@app.route('/signup', methods=['GET', 'POST'])
@logout_required
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)  # Hash password
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()  # Commit to the database
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

# Route for user login
@app.route('/', methods=['GET', 'POST'])
@logout_required
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()  # Get user by username
        if user and check_password_hash(user.password, form.password.data):  # Verify password
            session['user_id'] = user.id  # Store user_id in session
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        flash('Invalid username or password.', 'error')  # Show error for invalid credentials
    return render_template('login.html', form=form)



@app.route('/home')
@login_required
def home():
    current_user_id = session.get('user_id')
    form = ToggleLikeForm()
    # Get the search term from query parameters
    search_term = request.args.get('search', '').strip()

    # Set pagination variables
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of products per page

    # Create a base query for products
    query = Product.query

    # Apply search filter if there is a search term
    if search_term:
        query = query.filter(Product.name.ilike(f'%{search_term}%'))

    # Order by user products first
    query = query.order_by(
        db.case((Product.user_id == current_user_id, 1), else_=0).desc()
    )

    # Paginate results
    products = query.paginate(page=page, per_page=per_page)
    cards = [
        {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "count":len(product.like_count),
            "users_list":product.like_count, 
            "image": product.image_file,
            "user":product.user_id
        } for product in products
    ]
    # Render home template with product cards data
    return render_template('home.html', cards=cards,search_term=search_term, products=products,form=form)

# Route for logging out
@app.route('/logout')
@login_required  # Ensure the user is logged in before logging out
def logout():
    session.pop('user_id', None)  # Remove user_id from session
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Route for adding a product
@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    print("----")
    form = PictureForm()
  
    if form.validate_on_submit():
        # Handle file upload
        if 'image' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)

        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            new_product = Product(
                name=form.name.data,
                price=form.price.data,
                user_id=session['user_id'],
                image_file=filename
            )
            db.session.add(new_product)
            db.session.commit()
            flash('Product added successfully!', 'success')
            return redirect(url_for('home'))  # Redirect to product list
        else:
            flash('Invalid file type. Allowed types are: png, jpg, jpeg, gif', 'error')

    return render_template('product_form.html', form=form)

@app.route('/update_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)  # Get the product by ID
    form = PictureForm()

    if request.method == 'POST':
        # Handle file upload (optional, if user doesn't want to change the image)
        if 'image' in request.files and request.files['image']:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                product.image_file = filename  # Update the image file if a new one is uploaded

        # Update product fields
        product.name = form.name.data
        product.price = form.price.data
        
        db.session.commit()  # Commit changes to the database
        flash('Product updated successfully!', 'success')
        return redirect(url_for('home'))  # Redirect to product list

    # Populate the form with existing product details for updating
    form.name.data = product.name
    form.price.data = product.price

    return render_template('product_form.html', form=form, product=product)



# Route for deleting a product
@app.route('/product_delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/toggle_like/<int:product_id>', methods=['POST'])
@login_required
def toggle_like(product_id):
    form = ToggleLikeForm()

    if form.validate_on_submit():
        user_id = form.user_id.data  # Get the user ID
        product = Product.query.get(product_id)
        print(product.like_count)

        if product is None:
            flash('Product not found', 'error')
            return redirect(url_for('home'))

        if user_id in product.like_count:
            # User already liked, remove from likes
            print("remove--->")
            product.like_count.remove(user_id)
        else:
            # User has not liked, add to likes
            print("add--->")
            product.like_count.append(user_id)

        db.session.commit()
      
        return redirect(url_for('home'))

    flash('Invalid form submission', 'error')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
