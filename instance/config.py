import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'devkey')
    MYSQL_HOST = os.getenv('MYSQL_HOST')
    MYSQL_USER = os.getenv('MYSQL_USER')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
    MYSQL_DB = os.getenv('MYSQL_DB')
    WTF_CSRF_ENABLED = False
