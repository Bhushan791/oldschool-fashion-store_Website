from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from functools import wraps
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename

# Import models and forms
from app.models import (
    get_all_products, get_product_by_id, add_product, update_product, delete_product,
    create_user, verify_user, find_user_by_email, get_orders_by_user, get_order_items,
    create_order, update_order_status, get_all_orders
)
from app.forms import ProductForm, SignupForm, LoginForm

main = Blueprint('main', __name__)
admin = Blueprint('admin', __name__, url_prefix='/adminbhushan')

# --- Helper Decorators ---

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.')
            return redirect(url_for('main.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# --- Main Customer Routes ---

@main.route('/')
def index():
    products = get_all_products()
    product_list = [{
        'id': p[0],
        'name': p[1],
        'description': p[2],
        'price': p[3],
        'image': p[4]
    } for p in products]
    return render_template('index.html', products=product_list)

@main.route('/product/<int:product_id>')
def product_detail(product_id):
    p = get_product_by_id(product_id)
    if not p:
        return "Product not found", 404
    product = {
        'id': p[0],
        'name': p[1],
        'description': p[2],
        'price': p[3],
        'image': p[4]
    }
    return render_template('product_detail.html', product=product)

@main.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    cart = session.get('cart', {})
    if str(product_id) in cart:
        cart[str(product_id)] += quantity
    else:
        cart[str(product_id)] = quantity
    session['cart'] = cart
    session.modified = True
    flash('Product added to cart.')
    return redirect(url_for('main.cart'))

@main.route('/cart')
@login_required
def cart():
    cart = session.get('cart', {})
    products_in_cart = []
    total_price = 0
    for product_id, quantity in cart.items():
        product = get_product_by_id(int(product_id))
        if product:
            product_dict = {
                'id': product[0],
                'name': product[1],
                'description': product[2],
                'price': product[3],
                'image': product[4],
                'quantity': quantity,
                'subtotal': product[3] * quantity
            }
            total_price += product_dict['subtotal']
            products_in_cart.append(product_dict)
    return render_template('cart.html', products=products_in_cart, total=total_price)

@main.route('/remove_from_cart/<int:product_id>')
@login_required
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    cart.pop(str(product_id), None)
    session['cart'] = cart
    session.modified = True
    flash('Product removed from cart.')
    return redirect(url_for('main.cart'))

class CheckoutForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    submit = SubmitField('Place Order')

@main.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    form = CheckoutForm()
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.')
        return redirect(url_for('main.index'))

    products_in_cart = []
    total_price = 0
    for product_id, quantity in cart.items():
        product = get_product_by_id(int(product_id))
        if product:
            products_in_cart.append({
                'id': product[0],
                'name': product[1],
                'price': product[3],
                'quantity': quantity
            })
            total_price += product[3] * quantity

    if form.validate_on_submit():
        user_id = session['user_id']
        order_id = create_order(user_id, form.name.data, form.address.data, total_price, products_in_cart)
        session.pop('cart', None)
        session.modified = True
        flash(f'Order placed successfully! Your order ID is {order_id}.')
        return redirect(url_for('main.order_history'))

    return render_template('checkout.html', form=form)

# --- Authentication Routes with Enhanced Error Handling ---

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    error = request.args.get('error')
    if form.validate_on_submit():
        existing_user = find_user_by_email(form.email.data)
        if existing_user:
            return redirect(url_for('main.signup', error='email_exists'))
        if len(form.password.data) < 6:
            return redirect(url_for('main.signup', error='password_too_short'))
        if len(form.password.data) > 20:
            return redirect(url_for('main.signup', error='password_too_long'))
        create_user(form.email.data, form.password.data)
        return redirect(url_for('main.login', signup='success'))
    return render_template('signup.html', form=form, error=error)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = request.args.get('error')
    if form.validate_on_submit():
        user = find_user_by_email(form.email.data)
        if not user:
            return redirect(url_for('main.login', error='not_found'))
        elif not verify_user(form.email.data, form.password.data):
            return redirect(url_for('main.login', error='invalid_credentials'))
        # If you have account locking logic, add here:
        # elif user_is_locked(user):
        #     return redirect(url_for('main.login', error='locked'))
        else:
            session.clear()
            session['user_id'] = user[0]
            session['user_email'] = user[1]
            session.modified = True
            next_url = request.args.get('next')
            if next_url:
                return redirect(next_url)
            return redirect(url_for('main.index', login='success'))
    return render_template('login.html', form=form, error=error)

@main.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('main.index', logout='success'))

# --- User Profile & Order History ---

@main.route('/profile')
@login_required
def profile():
    user_id = session['user_id']
    user_email = session.get('user_email')
    orders = get_orders_by_user(user_id)
    orders_with_items = []
    for o in orders:
        items = get_order_items(o[0])
        orders_with_items.append({
            'id': o[0],
            'name': o[1],
            'address': o[2],
            'total_price': o[3],
            'status': o[4],
            'created_at': o[5],
            'items': [{'product_id': i[0], 'quantity': i[1], 'price': i[2]} for i in items]
        })
    return render_template('profile.html', email=user_email, orders=orders_with_items)

@main.route('/order_history')
@login_required
def order_history():
    user_id = session['user_id']
    orders = get_orders_by_user(user_id)
    orders_with_items = []
    for o in orders:
        items = get_order_items(o[0])
        orders_with_items.append({
            'id': o[0],
            'name': o[1],
            'address': o[2],
            'total_price': o[3],
            'status': o[4],
            'created_at': o[5],
            'items': [{'product_id': i[0], 'quantity': i[1], 'price': i[2]} for i in items]
        })
    return render_template('orders.html', orders=orders_with_items)

@main.route('/cancel_order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    user_id = session['user_id']
    orders = get_orders_by_user(user_id)
    order = next((o for o in orders if o[0] == order_id), None)
    if not order:
        flash('Order not found.')
        return redirect(url_for('main.order_history'))

    order_time = order[5]
    now = datetime.now()
    if order[4] != 'Pending':
        flash('Order cannot be cancelled.')
        return redirect(url_for('main.order_history'))

    if now - order_time > timedelta(hours=2):
        flash('Cancellation period expired.')
        return redirect(url_for('main.order_history'))

    update_order_status(order_id, 'Cancelled')
    flash('Order cancelled successfully.')
    return redirect(url_for('main.order_history'))

# --- Admin Routes ---

@admin.route('/')
def admin_panel():
    products = get_all_products()
    product_list = [{
        'id': p[0],
        'name': p[1],
        'description': p[2],
        'price': p[3],
        'image': p[4]
    } for p in products]
    return render_template('admin_panel.html', products=product_list)

@admin.route('/add', methods=['GET', 'POST'])
def add():
    form = ProductForm()
    if form.validate_on_submit():
        image_filename = None
        if form.image.data:
            image_file = form.image.data
            filename = secure_filename(image_file.filename)
            image_path = os.path.join('app', 'static', 'uploads', 'products', filename)
            image_file.save(image_path)
            image_filename = filename
        add_product(
            form.name.data,
            form.description.data,
            float(form.price.data),
            image_filename
        )
        flash('Product added successfully!')
        return redirect(url_for('admin.admin_panel'))
    return render_template('admin_add_edit.html', form=form, action='Add')

@admin.route('/edit/<int:product_id>', methods=['GET', 'POST'])
def edit(product_id):
    product = get_product_by_id(product_id)
    if not product:
        flash('Product not found.')
        return redirect(url_for('admin.admin_panel'))

    form = ProductForm()
    if request.method == 'GET':
        form.name.data = product[1]
        form.description.data = product[2]
        form.price.data = product[3]

    if form.validate_on_submit():
        image_filename = product[4]
        if form.image.data:
            image_file = form.image.data
            filename = secure_filename(image_file.filename)
            image_path = os.path.join('app', 'static', 'uploads', 'products', filename)
            image_file.save(image_path)
            image_filename = filename

        update_product(
            product_id,
            form.name.data,
            form.description.data,
            float(form.price.data),
            image_filename
        )
        flash('Product updated successfully!')
        return redirect(url_for('admin.admin_panel'))

    return render_template('admin_add_edit.html', form=form, action='Edit')

@admin.route('/delete/<int:product_id>')
def delete(product_id):
    delete_product(product_id)
    flash('Product deleted successfully!')
    return redirect(url_for('admin.admin_panel'))

@admin.route('/orders')
def admin_orders():
    orders = get_all_orders()
    orders_list = [{
        'id': o[0],
        'user_email': o[1],
        'name': o[2],
        'address': o[3],
        'total_price': o[4],
        'status': o[5],
        'created_at': o[6]
    } for o in orders]
    return render_template('admin_orders.html', orders=orders_list)

@admin.route('/orders/<int:order_id>/update_status', methods=['POST'])
def update_status(order_id):
    new_status = request.form.get('status')
    if new_status not in ['Pending', 'Cancelled', 'Verified', 'Completed']:
        flash('Invalid status.')
        return redirect(url_for('admin.admin_orders'))
    update_order_status(order_id, new_status)
    flash('Order status updated.')
    return redirect(url_for('admin.admin_orders'))
