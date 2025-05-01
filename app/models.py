from werkzeug.security import generate_password_hash, check_password_hash
from app import mysql
def get_all_products():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, description, price, image FROM products")
    products = cur.fetchall()
    cur.close()
    return products

def get_product_by_id(product_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, description, price, image FROM products WHERE id = %s", (product_id,))
    product = cur.fetchone()
    cur.close()
    return product

def add_product(name, description, price, image):
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO products (name, description, price, image) VALUES (%s, %s, %s, %s)",
        (name, description, price, image)
    )
    mysql.connection.commit()
    cur.close()

def update_product(product_id, name, description, price, image):
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE products SET name=%s, description=%s, price=%s, image=%s WHERE id=%s",
        (name, description, price, image, product_id)
    )
    mysql.connection.commit()
    cur.close()

def delete_product(product_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM products WHERE id=%s", (product_id,))
    mysql.connection.commit()
    cur.close()





def create_user(email, password):
    hashed_pw = generate_password_hash(password)
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_pw))
    mysql.connection.commit()
    cur.close()

def find_user_by_email(email):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, email, password FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    return user  # tuple (id, email, password) or None

def verify_user(email, password):
    user = find_user_by_email(email)
    if user and check_password_hash(user[2], password):
        return user
    return None





def create_order(user_id, name, address, total_price, cart_items):
    cur = mysql.connection.cursor()
    # Insert order
    cur.execute(
        "INSERT INTO orders (user_id, name, address, total_price) VALUES (%s, %s, %s, %s)",
        (user_id, name, address, total_price)
    )
    order_id = cur.lastrowid

    # Insert order items
    for item in cart_items:
        cur.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
            (order_id, item['id'], item['quantity'], item['price'])
        )

    mysql.connection.commit()
    cur.close()
    return order_id

def get_orders_by_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT id, name, address, total_price, status, created_at FROM orders WHERE user_id=%s ORDER BY created_at DESC",
        (user_id,)
    )
    orders = cur.fetchall()
    cur.close()
    return orders

def get_order_items(order_id):
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT product_id, quantity, price FROM order_items WHERE order_id=%s",
        (order_id,)
    )
    items = cur.fetchall()
    cur.close()
    return items

def get_all_orders():
    cur = mysql.connection.cursor()
    cur.execute(
        """
        SELECT o.id, u.email, o.name, o.address, o.total_price, o.status, o.created_at
        FROM orders o
        JOIN users u ON o.user_id = u.id
        ORDER BY o.created_at DESC
        """
    )
    orders = cur.fetchall()
    cur.close()
    return orders

def update_order_status(order_id, status):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE orders SET status=%s WHERE id=%s", (status, order_id))
    mysql.connection.commit()
    cur.close()
