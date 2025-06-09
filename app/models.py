# from werkzeug.security import generate_password_hash, check_password_hash
# from app import mysql

# # ===== Product Models =====

# def get_all_products():
#     cur = mysql.connection.cursor()
#     cur.execute("""
#         SELECT p.id, p.name, p.description, p.price, 
#                GROUP_CONCAT(pi.image_path) AS images 
#         FROM products p
#         LEFT JOIN product_images pi ON p.id = pi.product_id
#         GROUP BY p.id
#     """)
#     products = []
#     for p in cur.fetchall():
#         products.append({
#             'id': p[0],
#             'name': p[1],
#             'description': p[2],
#             'price': float(p[3]),
#             'images': p[4].split(',') if p[4] else []
#         })
#     cur.close()
#     return products

# def get_product_by_id(product_id):
#     cur = mysql.connection.cursor()
#     cur.execute("""
#         SELECT p.id, p.name, p.description, p.price, 
#                GROUP_CONCAT(pi.image_path) AS images 
#         FROM products p
#         LEFT JOIN product_images pi ON p.id = pi.product_id
#         WHERE p.id = %s
#         GROUP BY p.id
#     """, (product_id,))
#     result = cur.fetchone()
#     if not result:
#         cur.close()
#         return None
#     product = {
#         'id': result[0],
#         'name': result[1],
#         'description': result[2],
#         'price': float(result[3]),
#         'images': result[4].split(',') if result[4] else []
#     }
#     cur.close()
#     return product

# def add_product(name, description, price, images):
#     cur = mysql.connection.cursor()
#     cur.execute(
#         "INSERT INTO products (name, description, price) VALUES (%s, %s, %s)",
#         (name, description, price)
#     )
#     product_id = cur.lastrowid
#     # Insert each image for the product
#     for image in images:
#         cur.execute(
#             "INSERT INTO product_images (product_id, image_path) VALUES (%s, %s)",
#             (product_id, image)
#         )
#     mysql.connection.commit()
#     cur.close()

# def update_product(product_id, name, description, price, images):
#     cur = mysql.connection.cursor()
#     cur.execute(
#         "UPDATE products SET name=%s, description=%s, price=%s WHERE id=%s",
#         (name, description, price, product_id)
#     )
#     cur.execute("DELETE FROM product_images WHERE product_id=%s", (product_id,))
#     for image in images:
#         cur.execute(
#             "INSERT INTO product_images (product_id, image_path) VALUES (%s, %s)",
#             (product_id, image)
#         )
#     mysql.connection.commit()
#     cur.close()

# def delete_product(product_id):
#     cur = mysql.connection.cursor()
#     cur.execute("DELETE FROM products WHERE id=%s", (product_id,))
#     mysql.connection.commit()
#     cur.close()

# # ===== User Models =====

# def create_user(email, password):
#     hashed_pw = generate_password_hash(password)
#     cur = mysql.connection.cursor()
#     cur.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_pw))
#     mysql.connection.commit()
#     cur.close()

# def find_user_by_email(email):
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT id, email, password FROM users WHERE email = %s", (email,))
#     user = cur.fetchone()
#     cur.close()
#     return user

# def verify_user(email, password):
#     user = find_user_by_email(email)
#     if user and check_password_hash(user[2], password):
#         return user
#     return None

# # ===== Order Models =====

# def create_order(user_id, name, address, total_price, contact, cart_items):
#     cur = mysql.connection.cursor()
#     cur.execute(
#         "INSERT INTO orders (user_id, name, address, total_price, contact) VALUES (%s, %s, %s, %s, %s)",
#         (user_id, name, address, total_price, contact)
#     )
#     order_id = cur.lastrowid
#     for item in cart_items:
#         cur.execute(
#             "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
#             (order_id, item['id'], item['quantity'], item['price'])
#         )
#     mysql.connection.commit()
#     cur.close()
#     return order_id

# def get_orders_by_user(user_id):
#     cur = mysql.connection.cursor()
#     cur.execute(
#         "SELECT id, name, address, total_price, status, created_at, contact FROM orders WHERE user_id=%s ORDER BY created_at DESC",
#         (user_id,)
#     )
#     orders = []
#     for row in cur.fetchall():
#         orders.append({
#             'id': row[0],
#             'name': row[1],
#             'address': row[2],
#             'total_price': float(row[3]),
#             'status': row[4],
#             'created_at': row[5],
#             'contact': row[6]
#         })
#     cur.close()
#     return orders

# def get_order_items(order_id):
#     cur = mysql.connection.cursor()
#     cur.execute(
#         "SELECT product_id, quantity, price FROM order_items WHERE order_id=%s",
#         (order_id,)
#     )
#     items = cur.fetchall()
#     cur.close()
#     return items

# def get_all_orders():
#     cur = mysql.connection.cursor()
#     cur.execute(
#         """
#         SELECT o.id, u.email, o.name, o.address, o.total_price, o.status, o.created_at, o.contact
#         FROM orders o
#         JOIN users u ON o.user_id = u.id
#         ORDER BY o.created_at DESC
#         """
#     )
#     orders = []
#     for row in cur.fetchall():
#         orders.append({
#             'id': row[0],
#             'user_email': row[1],
#             'name': row[2],
#             'address': row[3],
#             'total_price': float(row[4]),
#             'status': row[5],
#             'created_at': row[6],
#             'contact': row[7]
#         })
#     cur.close()
#     return orders

# def update_order_status(order_id, status):
#     cur = mysql.connection.cursor()
#     cur.execute("UPDATE orders SET status=%s WHERE id=%s", (status, order_id))
#     mysql.connection.commit()
#     cur.close()

# def update_order_contact(order_id, contact):
#     cur = mysql.connection.cursor()
#     cur.execute("UPDATE orders SET contact=%s WHERE id=%s", (contact, order_id))
#     mysql.connection.commit()
#     cur.close()










from werkzeug.security import generate_password_hash, check_password_hash
from app import get_db_connection

# ===== Product Models =====

def get_all_products():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT p.id, p.name, p.description, p.price, 
               GROUP_CONCAT(pi.image_path) AS images 
        FROM products p
        LEFT JOIN product_images pi ON p.id = pi.product_id
        GROUP BY p.id
    """)
    results = cursor.fetchall()
    products = []
    for p in results:
        products.append({
            'id': p['id'],
            'name': p['name'],
            'description': p['description'],
            'price': float(p['price']),
            'images': p['images'].split(',') if p['images'] else []
        })
    cursor.close()
    return products

def get_product_by_id(product_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT p.id, p.name, p.description, p.price, 
               GROUP_CONCAT(pi.image_path) AS images 
        FROM products p
        LEFT JOIN product_images pi ON p.id = pi.product_id
        WHERE p.id = %s
        GROUP BY p.id
    """, (product_id,))
    result = cursor.fetchone()
    cursor.close()
    
    if not result:
        return None
        
    product = {
        'id': result['id'],
        'name': result['name'],
        'description': result['description'],
        'price': float(result['price']),
        'images': result['images'].split(',') if result['images'] else []
    }
    return product

def add_product(name, description, price, images):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO products (name, description, price) VALUES (%s, %s, %s)",
        (name, description, price)
    )
    product_id = cursor.lastrowid
    
    # Insert each image for the product
    for image in images:
        cursor.execute(
            "INSERT INTO product_images (product_id, image_path) VALUES (%s, %s)",
            (product_id, image)
        )
    connection.commit()
    cursor.close()

def update_product(product_id, name, description, price, images):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE products SET name=%s, description=%s, price=%s WHERE id=%s",
        (name, description, price, product_id)
    )
    cursor.execute("DELETE FROM product_images WHERE product_id=%s", (product_id,))
    for image in images:
        cursor.execute(
            "INSERT INTO product_images (product_id, image_path) VALUES (%s, %s)",
            (product_id, image)
        )
    connection.commit()
    cursor.close()

def delete_product(product_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
    connection.commit()
    cursor.close()

# ===== User Models =====

def create_user(email, password):
    hashed_pw = generate_password_hash(password)
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_pw))
    connection.commit()
    cursor.close()

def find_user_by_email(email):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, email, password FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    return user

def verify_user(email, password):
    user = find_user_by_email(email)
    if user and check_password_hash(user['password'], password):
        return user
    return None

# ===== Order Models =====

def create_order(user_id, name, address, total_price, contact, cart_items):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO orders (user_id, name, address, total_price, contact) VALUES (%s, %s, %s, %s, %s)",
        (user_id, name, address, total_price, contact)
    )
    order_id = cursor.lastrowid
    
    for item in cart_items:
        cursor.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
            (order_id, item['id'], item['quantity'], item['price'])
        )
    connection.commit()
    cursor.close()
    return order_id

def get_orders_by_user(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT id, name, address, total_price, status, created_at, contact FROM orders WHERE user_id=%s ORDER BY created_at DESC",
        (user_id,)
    )
    results = cursor.fetchall()
    orders = []
    for row in results:
        orders.append({
            'id': row['id'],
            'name': row['name'],
            'address': row['address'],
            'total_price': float(row['total_price']),
            'status': row['status'],
            'created_at': row['created_at'],
            'contact': row['contact']
        })
    cursor.close()
    return orders

def get_order_items(order_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT product_id, quantity, price FROM order_items WHERE order_id=%s",
        (order_id,)
    )
    items = cursor.fetchall()
    cursor.close()
    return items

def get_all_orders():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT o.id, u.email, o.name, o.address, o.total_price, o.status, o.created_at, o.contact
        FROM orders o
        JOIN users u ON o.user_id = u.id
        ORDER BY o.created_at DESC
        """
    )
    results = cursor.fetchall()
    orders = []
    for row in results:
        orders.append({
            'id': row['id'],
            'user_email': row['email'],
            'name': row['name'],
            'address': row['address'],
            'total_price': float(row['total_price']),
            'status': row['status'],
            'created_at': row['created_at'],
            'contact': row['contact']
        })
    cursor.close()
    return orders

def update_order_status(order_id, status):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE orders SET status=%s WHERE id=%s", (status, order_id))
    connection.commit()
    cursor.close()

def update_order_contact(order_id, contact):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE orders SET contact=%s WHERE id=%s", (contact, order_id))
    connection.commit()
    cursor.close()