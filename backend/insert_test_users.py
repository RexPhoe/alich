#!/usr/bin/env python3

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError

# Add the current directory to the path so we can import our models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
load_dotenv()

# Create a Flask app instance
app = Flask(__name__)

# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import models after app is created
from models import db

# Initialize the database
db.init_app(app)

# Import models after db is initialized to avoid circular imports
from models.user import User
from models.employee import Employee

# Test users data
users_data = [
    {
        'username': 'admin',
        'password': 'admin123',
        'role': 'admin',
        'first_name': 'Admin',
        'last_name': 'User',
        'email': 'admin@alich.com',
        'department': 'IT',
        'position': 'System Administrator',
        'phone': '555-1234'
    },
    {
        'username': 'supervisor',
        'password': 'super123',
        'role': 'admin',
        'first_name': 'Super',
        'last_name': 'Visor',
        'email': 'supervisor@alich.com',
        'department': 'Management',
        'position': 'Department Supervisor',
        'phone': '555-2345'
    },
    {
        'username': 'employee1',
        'password': 'emp123',
        'role': 'employee',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@alich.com',
        'department': 'Sales',
        'position': 'Sales Representative',
        'phone': '555-3456'
    },
    {
        'username': 'employee2',
        'password': 'emp123',
        'role': 'employee',
        'first_name': 'Jane',
        'last_name': 'Smith',
        'email': 'jane.smith@alich.com',
        'department': 'Marketing',
        'position': 'Marketing Specialist',
        'phone': '555-4567'
    },
    {
        'username': 'employee3',
        'password': 'emp123',
        'role': 'employee',
        'first_name': 'Carlos',
        'last_name': 'Perez',
        'email': 'carlos.perez@alich.com',
        'department': 'Engineering',
        'position': 'Software Developer',
        'phone': '555-5678'
    }
]

def insert_test_users():
    """Insert test users into the database"""
    print("Starting to insert test users...")
    
    with app.app_context():
        # First check if we can connect to the database
        try:
            db.engine.connect()
            print(f"✅ Connected to database: {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}")
        except Exception as e:
            print(f"❌ Database connection failed: {str(e)}")
            return False
        
        # Insert each user
        users_created = 0
        for user_data in users_data:
            try:
                # Check if user already exists
                existing_user = User.query.filter_by(username=user_data['username']).first()
                if existing_user:
                    print(f"⚠️ User '{user_data['username']}' already exists, skipping...")
                    continue
                
                # Create user
                # Create user with hashed password
                user = User(
                    username=user_data['username'],
                    password=user_data['password'],  # Password will be hashed in User model
                    role=user_data['role']
                )
                db.session.add(user)
                db.session.flush()  # Flush to get the user ID
                
                # Create employee record
                employee = Employee(
                    user_id=user.id,
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    email=user_data['email'],
                    phone=user_data.get('phone'),
                    department=user_data.get('department'),
                    position=user_data.get('position'),
                    hire_date=datetime.now().date()
                )
                db.session.add(employee)
                db.session.commit()
                
                print(f"✅ Created user: {user_data['username']} ({user_data['role']})")
                users_created += 1
                
            except IntegrityError as e:
                db.session.rollback()
                print(f"❌ Error creating user '{user_data['username']}': {str(e)}")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Unexpected error creating user '{user_data['username']}': {str(e)}")
        
        print(f"\n✅ Successfully created {users_created} out of {len(users_data)} users")
        return True

if __name__ == '__main__':
    insert_test_users()