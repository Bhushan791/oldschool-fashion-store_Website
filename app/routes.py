from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from . import mysql

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/ping')
def ping_db():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT 1")
        return jsonify({'status': 'Database connected ✅'})
    except Exception as e:
        return jsonify({'status': 'DB Error ❌', 'error': str(e)})
