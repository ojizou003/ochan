import os
from dotenv import load_dotenv

load_dotenv()

ANON_NAME_MAX_LENGTH = 50
EMAIL_MAX_LENGTH = 255

BOARD_NAME_MAX_LENGTH = 30
BOARD_CATEGORY_NAME_MAX_LENGTH = 30
THREAD_NAME_MAX_LENGTH = 100
BODY_MAX_LENGTH = 1000

class Config:
    DB_HOST = os.getenv('DB_HOST')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASS = os.getenv('DB_PASS')
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')

    @staticmethod
    def get_database_url():
        return f"mysql+mysqldb://{Config.DB_USER}:{Config.DB_PASS}@{Config.DB_HOST}/{Config.DB_NAME}"