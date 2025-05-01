from flask import Flask
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import os

mysql = MySQL()
csrf = CSRFProtect()

def create_app():
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)

    # 🔐 Load secret key from .env or use default (for CSRF and session security)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'devkey')

    # 📦 Load additional config from instance/config.py
    app.config.from_object('instance.config.Config')

    # 🔌 Initialize extensions
    mysql.init_app(app)
    csrf.init_app(app)

    # 📚 Register Blueprints
    from .routes import main as main_blueprint, admin as admin_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(admin_blueprint)

    return app
