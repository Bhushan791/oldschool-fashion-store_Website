# from flask import Flask
# from flask_mysqldb import MySQL
# from flask_wtf.csrf import CSRFProtect
# from dotenv import load_dotenv
# import os

# mysql = MySQL()
# csrf = CSRFProtect()

# def create_app():
#     load_dotenv()
#     app = Flask(__name__, instance_relative_config=True)

#     # 🔐 Load secret key from .env or use default (for CSRF and session security)
#     app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'devkey')

#     # 📦 Load additional config from instance/config.py
#     app.config.from_object('instance.config.Config')

#     # Debug: Print config to see if it's loaded
#     print("MySQL Config:")
#     print(f"HOST: {app.config.get('MYSQL_HOST')}")
#     print(f"USER: {app.config.get('MYSQL_USER')}")
#     print(f"DB: {app.config.get('MYSQL_DB')}")
#     print(f"PASSWORD: {'*' * len(app.config.get('MYSQL_PASSWORD', ''))}")

#     # 🔌 Initialize extensions
#     try:
#         mysql.init_app(app)
#         print("MySQL initialized successfully")
#     except Exception as e:
#         print(f"MySQL initialization failed: {e}")
    
#     csrf.init_app(app)

#     # Test connection
#     with app.app_context():
#         try:
#             cur = mysql.connection.cursor()
#             cur.execute("SELECT 1")
#             result = cur.fetchone()
#             cur.close()
#             print("Database connection test successful!")
#         except Exception as e:
#             print(f"Database connection test failed: {e}")

#     # 📚 Register Blueprints
#     from .routes import main as main_blueprint, admin as admin_blueprint
#     app.register_blueprint(main_blueprint)
#     app.register_blueprint(admin_blueprint)

#     return app





from flask import Flask
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import os
import pymysql

# Global database connection
db_connection = None
csrf = CSRFProtect()

def get_db_connection():
    """Get database connection"""
    global db_connection
    if db_connection is None or not db_connection.open:
        try:
            db_connection = pymysql.connect(
                host=os.getenv('MYSQL_HOST', 'localhost'),
                user=os.getenv('MYSQL_USER', 'root'),
                password=os.getenv('MYSQL_PASSWORD', ''),
                database=os.getenv('MYSQL_DB'),
                port=int(os.getenv('MYSQL_PORT', 3306)),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
            print("✅ Database connection established successfully!")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise e
    return db_connection

def create_app():
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)

    # 🔐 Load secret key from .env or use default (for CSRF and session security)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'devkey')

    # 📦 Load additional config from instance/config.py
    app.config.from_object('instance.config.Config')

    # Debug: Print config to see if it's loaded
    print("📊 MySQL Config:")
    print(f"HOST: {app.config.get('MYSQL_HOST')}")
    print(f"USER: {app.config.get('MYSQL_USER')}")
    print(f"DB: {app.config.get('MYSQL_DB')}")
    print(f"PORT: {app.config.get('MYSQL_PORT', 3306)}")
    print(f"PASSWORD: {'*' * len(app.config.get('MYSQL_PASSWORD', ''))}")

    # 🔌 Initialize extensions
    csrf.init_app(app)

    # Test database connection
    with app.app_context():
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            cursor.close()
            print(f"🎉 Database connection test successful: {result}")
        except Exception as e:
            print(f"💥 Database connection test failed: {e}")
            # Don't raise the error here, let the app start but log the issue

    # 📚 Register Blueprints
    from .routes import main as main_blueprint, admin as admin_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(admin_blueprint)

    return app