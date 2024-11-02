from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Product
from utils import login_required
from forms import PictureForm

product_bp = Blueprint('product', __name__)

@product_bp.route('/home')
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

@product_bp.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    form = PictureForm()
    if form.validate_on_submit():
        if 'image' not in request.files or request.files['image'].filename == '':
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
            return redirect(url_for('product.home'))
        else:
            flash('Invalid file type. Allowed types are: png, jpg, jpeg, gif', 'error')

    return render_template('product_form.html', form=form)

@product_bp.route('/update_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = PictureForm()

    if request.method == 'POST':
        if 'image' in request.files and request.files['image']:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                product.image_file = filename

        product.name = form.name.data
        product.price = form.price.data

        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('product.home'))

    form.name.data = product.name
    form.price.data = product.price
    return render_template('product_form.html', form=form, product=product)

@product_bp.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('product.home'))

@product_bp.route('/toggle_like/<int:product_id>', methods=['POST'])
@login_required
def toggle_like(product_id):
    product = Product.query.get_or_404(product_id)
    user_id = session['user_id']

    if user_id in product.like_count:
        product.like_count.remove(user_id)
        flash('You unliked this product.', 'success')
    else:
        product.like_count.append(user_id)
        flash('You liked this product!', 'success')

    db.session.commit()
    return redirect(url_for('product.home'))
