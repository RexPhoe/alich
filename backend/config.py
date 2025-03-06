import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Application settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DEBUG = os.environ.get('FLASK_DEBUG', True)

    # Database settings
    # Construct MySQL connection string if individual variables are provided
    if all([os.environ.get('DB_USER'), os.environ.get('DB_PASSWORD'), 
            os.environ.get('DB_HOST'), os.environ.get('DB_PORT'), 
            os.environ.get('DB_NAME')]):
        db_user = os.environ.get('DB_USER')
        db_password = os.environ.get('DB_PASSWORD')
        db_host = os.environ.get('DB_HOST')
        db_port = os.environ.get('DB_PORT')
        db_name = os.environ.get('DB_NAME')
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    else:
        # Fallback to DATABASE_URL or SQLite
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'sqlite:///alich.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour

    # CORS settings
    CORS_HEADERS = 'Content-Type'

    # Pagination settings
    ITEMS_PER_PAGE = 10