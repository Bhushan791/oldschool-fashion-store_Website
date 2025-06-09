from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename

from app.models import (
    get_all_products, get_product_by_id, add_product, update_product, delete_product,
    create_user, verify_user, find_user_by_email, get_orders_by_user, get_order_items,
    create_order, update_order_status, get_all_orders
)
from app.forms import ProductForm, SignupForm, LoginForm, CheckoutForm

main = Blueprint('main', __name__)
admin = Blueprint('admin', __name__, url_prefix='/adminbhushan')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('main.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# --- Main Customer Routes ---

@main.route('/')
def index():
    products = get_all_products()
    product_list = []
    for p in products:
        product_list.append({
            'id': p['id'],
            'name': p['name'],
            'description': p['description'],
            'price': p['price'],
            'image': p['images'][0] if p['images'] else None
        })
    return render_template('index.html', products=product_list)

@main.route('/product/<int:product_id>')
def product_detail(product_id):
    product = get_product_by_id(product_id)
    if not product:
        return "Product not found", 404
    return render_template('product_detail.html', product=product)

@main.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    quantity = max(1, quantity)
    cart = session.get('cart', {})
    cart[product_id] = cart.get(product_id, 0) + quantity
    session['cart'] = cart
    session.modified = True
    flash('Product added to cart.', 'success')
    return redirect(url_for('main.cart'))

@main.route('/cart')
@login_required
def cart():
    cart = session.get('cart', {})
    products_in_cart = []
    total_price = 0

    for product_id, quantity in cart.items():
        product = get_product_by_id(product_id)
        if product:
            subtotal = product['price'] * quantity
            products_in_cart.append({
                'id': product['id'],
                'name': product['name'],
                'description': product['description'],
                'price': product['price'],
                'images': product['images'],
                'quantity': quantity,
                'subtotal': subtotal
            })
            total_price += subtotal

    return render_template('cart.html', products=products_in_cart, total=total_price)

@main.route('/remove_from_cart/<int:product_id>')
@login_required
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if product_id in cart:
        del cart[product_id]
        session['cart'] = cart
        session.modified = True
        flash('Product removed from cart.', 'info')
    return redirect(url_for('main.cart'))

@main.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    form = CheckoutForm()
    cart = session.get('cart', {})

    if not cart:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('main.index'))

    delivery_fee = 100
    products_in_cart = []
    subtotal = 0

    for product_id, quantity in cart.items():
        product = get_product_by_id(product_id)
        if product:
            product_subtotal = product['price'] * quantity
            subtotal += product_subtotal
            products_in_cart.append({
                'id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'quantity': quantity,
                'subtotal': product_subtotal
            })

    total_price = subtotal + delivery_fee

    if form.validate_on_submit():
        if not form.confirm_order.data:
            flash('Please confirm your order to proceed.', 'warning')
            return redirect(url_for('main.checkout'))

        user_id = session.get('user_id')
        # Defensive check: ensure user exists before placing order
        if not user_id:
            flash("Session invalid. Please log in again.", "danger")
            return redirect(url_for('main.logout'))

        order_id = create_order(
            user_id,
            form.fullname.data,
            form.address.data,
            total_price,
            form.contact.data,
            products_in_cart
        )

        session.pop('cart', None)
        session.modified = True
        flash(f'Order placed successfully! Your order ID is {order_id}. Note: You can only cancel this order within 2 hours of placing it.', 'success')
        return redirect(url_for('main.order_history'))

    return render_template(
        'checkout.html',
        form=form,
        products=products_in_cart,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        total=total_price
    )

# --- Authentication Routes ---

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data
        existing_user = find_user_by_email(email)
        if existing_user:
            flash('Email already exists. Please login', 'warning')
            return render_template('signup.html', form=form, error='email_exists')

        password = form.password.data
        if len(password) < 6:
            flash('Password too short', 'warning')
            return render_template('signup.html', form=form, error='password_too_short')

        if len(password) > 20:
            flash('Password too long', 'warning')
            return render_template('signup.html', form=form, error='password_too_long')

        create_user(email, password)
        flash('Signup Success! Please Login!', 'success')
        return redirect(url_for('main.login'))

    return render_template('signup.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = verify_user(email, password)
        if user:
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            flash('Login success', 'success')
            return redirect(url_for('main.index'))
        flash('Login incorrect', 'warning')
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Logout success', 'success')
    return redirect(url_for('main.index'))

# --- User Profile & Order History ---

@main.route('/profile')
@login_required
def profile():
    user_id = session['user_id']
    user_email = session.get('user_email')
    orders = get_orders_by_user(user_id)
    orders_with_items = []
    for order in orders:
        items = get_order_items(order['id'])
        orders_with_items.append({
            'id': order['id'],
            'name': order['name'],
            'address': order['address'],
            'total_price': order['total_price'],
            'status': order['status'],
            'created_at': order['created_at'],
            # 'items': [{'product_id': item[0], 'quantity': item[1], 'price': item[2]} for item in items]
            'items': [{'product_id': item['product_id'], 'quantity': item['quantity'], 'price': item['price']} for item in items]

        })
    return render_template('profile.html', email=user_email, orders=orders_with_items)

@main.route('/order_history')
@login_required
def order_history():
    user_id = session['user_id']
    orders = get_orders_by_user(user_id)
    orders_with_items = []
    for order in orders:
        items = get_order_items(order['id'])
        orders_with_items.append({
            'id': order['id'],
            'name': order['name'],
            'address': order['address'],
            'total_price': order['total_price'],
            'status': order['status'],
            'created_at': order['created_at'],
            # 'items': [{'product_id': item[0], 'quantity': item[1], 'price': item[2]} for item in items]
            'items': [{'product_id': item['product_id'], 'quantity': item['quantity'], 'price': item['price']} for item in items]

        })
    return render_template('orders.html', orders=orders_with_items)

@main.route('/cancel_order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    user_id = session['user_id']
    orders = get_orders_by_user(user_id)

    order = next((order for order in orders if order['id'] == order_id), None)
    if not order:
        flash('Order not found.', 'warning')
        return redirect(url_for('main.order_history'))

    order_time = order['created_at']
    now = datetime.now()

    if order['status'] != 'Pending':
        flash('Order cannot be cancelled.', 'warning')
        return redirect(url_for('main.order_history'))

    if now - order_time > timedelta(hours=2):
        flash('Cancellation period expired.', 'warning')
        return redirect(url_for('main.order_history'))

    update_order_status(order_id, 'Cancelled')
    flash('Order cancelled successfully.', 'success')
    return redirect(url_for('main.order_history'))

# --- Admin Routes ---

@admin.route('/')
def admin_panel():
    products = get_all_products()
    product_list = []
    for p in products:
        product_list.append({
            'id': p['id'],
            'name': p['name'],
            'description': p['description'],
            'price': p['price'],
            'image': p['images'][0] if p['images'] else None
        })
    return render_template('admin_panel.html', products=product_list)

@admin.route('/add', methods=['GET', 'POST'])
def add():
    form = ProductForm()
    if form.validate_on_submit():
        image_filenames = []
        for image_file in request.files.getlist('images'):
            if image_file and allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                image_path = os.path.join('app', 'static', 'uploads', 'products', filename)
                try:
                    image_file.save(image_path)
                    image_filenames.append(filename)
                except Exception as e:
                    flash(f'Error saving image: {e}', 'danger')
                    return render_template('admin_add_edit.html', form=form, action='Add')

        add_product(
            form.name.data,
            form.description.data,
            float(form.price.data),
            image_filenames
        )
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin.admin_panel'))
    return render_template('admin_add_edit.html', form=form, action='Add')

@admin.route('/edit/<int:product_id>', methods=['GET', 'POST'])
def edit(product_id):
    product = get_product_by_id(product_id)
    if not product:
        flash('Product not found.', 'warning')
        return redirect(url_for('admin.admin_panel'))

    form = ProductForm()
    if request.method == 'GET':
        form.name.data = product['name']
        form.description.data = product['description']
        form.price.data = product['price']

    if form.validate_on_submit():
        image_filenames = []
        for image_file in request.files.getlist('images'):
            if image_file and allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                image_path = os.path.join('app', 'static', 'uploads', 'products', filename)
                try:
                    image_file.save(image_path)
                    image_filenames.append(filename)
                except Exception as e:
                    flash(f'Error saving image: {e}', 'danger')
                    return render_template('admin_add_edit.html', form=form, action='Edit', product=product)
        update_product(
            product_id,
            form.name.data,
            form.description.data,
            float(form.price.data),
            image_filenames
        )
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin.admin_panel'))

    return render_template('admin_add_edit.html', form=form, action='Edit', product=product)

@admin.route('/delete/<int:product_id>')
def delete(product_id):
    delete_product(product_id)
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin.admin_panel'))

@admin.route('/orders')
def admin_orders():
    orders = get_all_orders()
    orders_list = []
    for order in orders:
        orders_list.append({
            'id': order['id'],
            'user_email': order['user_email'],
            'name': order['name'],
            'address': order['address'],
            'contact': order['contact'],
            'total_price': order['total_price'],
            'status': order['status'],
            'created_at': order['created_at']
        })
    return render_template('admin_orders.html', orders=orders_list)

@admin.route('/orders/<int:order_id>/update_status', methods=['POST'])
def update_status(order_id):
    new_status = request.form.get('status')
    if new_status not in ['Pending', 'Cancelled', 'Verified', 'Completed']:
        flash('Invalid status.', 'warning')
        return redirect(url_for('admin.admin_orders'))
    update_order_status(order_id, new_status)
    flash('Order status updated.', 'success')
    return redirect(url_for('admin.admin_orders'))





# Add this to your routes.py for testing
@main.route('/test-db')
def test_db():
    try:
        from app import get_db_connection
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        cursor.close()
        return f"✅ Database connection successful: {result}"
    except Exception as e:
        return f"❌ Database connection failed: {str(e)}"