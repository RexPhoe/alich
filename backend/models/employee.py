from datetime import datetime
from . import db

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    department = db.Column(db.String(50))
    position = db.Column(db.String(50))
    hire_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='active')
    
    # Temporarily comment out relationships to avoid circular imports for the insert script
    # These will be handled by the main application
    # attendance_records = db.relationship('Attendance', backref='employee', lazy=True)
    # work_schedules = db.relationship('WorkSchedule', backref='employee', lazy=True)
    # absences = db.relationship('Absence', backref='employee', lazy=True)
    
    def __init__(self, user_id, first_name, last_name, email, phone=None,
                 department=None, position=None, hire_date=None):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.department = department
        self.position = position
        self.hire_date = hire_date or datetime.utcnow().date()
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def is_active(self):
        return self.status == 'active'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'department': self.department,
            'position': self.position,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'status': self.status
        }