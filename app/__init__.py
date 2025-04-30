from flask import Flask
from flask_mysql_connector import MySQL
from flask_cors import CORS

mysql = MySQL()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    # Load config
    app.config.from_pyfile('config.py')
    
    # Init plugins
    mysql.init_app(app)
    CORS(app)

    # Import routes
    from .routes import main
    app.register_blueprint(main)

    return app
