import os

ANON_NAME_MAX_LENGTH = 50
EMAIL_MAX_LENGTH = 255

BOARD_NAME_MAX_LENGTH = 30
BOARD_CATEGORY_NAME_MAX_LENGTH = 30
THREAD_NAME_MAX_LENGTH = 100
BODY_MAX_LENGTH = 1000

class Config:
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_NAME = os.environ.get('DB_NAME', 'default_db_name')
    DB_USER = os.environ.get('DB_USER', 'default_user')
    DB_PASS = os.environ.get('DB_PASS', 'default_password')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')

    @staticmethod
    def get_database_url():
        return f"mysql+mysqldb://{Config.DB_USER}:{Config.DB_PASS}@{Config.DB_HOST}/{Config.DB_NAME}"