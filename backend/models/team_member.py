from datetime import datetime
from . import db

class TeamMember(db.Model):
    __tablename__ = 'team_members'
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    role = db.Column(db.String(50), default='member')  # e.g., 'leader', 'member'
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with Employee
    employee = db.relationship('Employee', backref=db.backref('team_memberships', lazy=True))
    
    def __init__(self, team_id, employee_id, role='member'):
        self.team_id = team_id
        self.employee_id = employee_id
        self.role = role
    
    def to_dict(self):
        return {
            'id': self.id,
            'team_id': self.team_id,
            'employee_id': self.employee_id,
            'role': self.role,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None
        }