from datetime import datetime
from . import db

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    check_in = db.Column(db.DateTime)
    check_out = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='present')
    notes = db.Column(db.Text)
    
    def __init__(self, employee_id, check_in=None, check_out=None, status='present', notes=None):
        self.employee_id = employee_id
        self.check_in = check_in or datetime.utcnow()
        self.check_out = check_out
        self.status = status
        self.notes = notes
    
    @property
    def duration(self):
        if self.check_in and self.check_out:
            return self.check_out - self.check_in
        return None
    
    def is_checked_out(self):
        return self.check_out is not None
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'check_in': self.check_in.isoformat() if self.check_in else None,
            'check_out': self.check_out.isoformat() if self.check_out else None,
            'status': self.status,
            'notes': self.notes,
            'duration': str(self.duration) if self.duration else None
        }