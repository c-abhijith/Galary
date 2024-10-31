from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from models import db, User, Product
from forms import SignupForm, LoginForm, PictureForm, ToggleLikeForm

# Decorators for login and logout requirements
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            flash("You are already logged in.", "info")
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# Route for user signup
@app.route('/signup', methods=['GET', 'POST'])
@logout_required
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

# Route for user login
@app.route('/', methods=['GET', 'POST'])
@logout_required
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        flash('Invalid username or password.', 'error')
    return render_template('login.html', form=form)

@app.route('/home')
@login_required
def home():
    current_user_id = session.get('user_id')
    form = ToggleLikeForm()
    search_term = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 8

    query = Product.query
    if search_term:
        query = query.filter(Product.name.ilike(f'%{search_term}%'))
    
    query = query.order_by(
        db.case((Product.user_id == current_user_id, 1), else_=0).desc()
    )
    products = query.paginate(page=page, per_page=per_page)
    
    cards = [
        {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "count": len(product.like_count),
            "users_list": product.like_count,
            "image": product.image_file,
            "user": product.user_id
        } for product in products
    ]
    return render_template('home.html', cards=cards, search_term=search_term, products=products, form=form)

# Route for logging out
@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Route for adding a product
@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    form = PictureForm()
    if form.validate_on_submit():
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
            return redirect(url_for('home'))
        else:
            flash('Invalid file type. Allowed types are: png, jpg, jpeg, gif', 'error')

    return render_template('product_form.html', form=form)

@app.route('/update_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = PictureForm()

    if request.method == 'POST':
        if 'image' in request.files and request.files['image']:
            file = request.files['image']
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                product.image_file = filename

        product.name = form.name.data
        product.price = form.price.data
        db.session.commit()
        return redirect(url_for('home'))

    form.name.data = product.name
    form.price.data = product.price
    return render_template('product_form.html', form=form)

@app.route('/toggle_like/<int:product_id>', methods=['POST'])
@login_required
def toggle_like(product_id):
    product = Product.query.get(product_id)
    if product:
        current_user_id = session['user_id']
        if current_user_id in product.like_count:
            product.like_count.remove(current_user_id)
            flash("You unliked this product.", "info")
        else:
            product.like_count.append(current_user_id)
            flash("You liked this product.", "success")

        db.session.commit()
    return redirect(url_for('home'))
