from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

def test_database_connection():
    # Load environment variables
    load_dotenv()
    
    # Create a test Flask application
    app = Flask(__name__)
    
    # Configure the database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize SQLAlchemy
    db = SQLAlchemy(app)
    
    try:
        # Attempt to connect to the database
        with app.app_context():
            db.engine.connect()
        print("✅ Database connection successful!")
        print(f"Connected to: {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}")
        print(f"Database name: {os.getenv('DB_NAME')}")
        return True
    except Exception as e:
        print("❌ Database connection failed!")
        print(f"Error: {str(e)}")
        return False

if __name__ == '__main__':
    test_database_connection()