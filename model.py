from datetime import datetime, time
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'mentor', 'mentee'
    name = db.Column(db.String(100))
    bio = db.Column(db.Text)
    goals = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    skills = db.relationship('UserSkill', backref='user', lazy=True, cascade='all, delete-orphan')
    mentor_availability = db.relationship('MentorAvailability', backref='mentor', lazy=True, cascade='all, delete-orphan')
    sent_requests = db.relationship('MentorshipRequest', foreign_keys='MentorshipRequest.mentee_id', backref='mentee', lazy=True)
    received_requests = db.relationship('MentorshipRequest', foreign_keys='MentorshipRequest.mentor_id', backref='mentor', lazy=True)
    mentor_sessions = db.relationship('MentorshipSession', foreign_keys='MentorshipSession.mentor_id', backref='session_mentor', lazy=True)
    mentee_sessions = db.relationship('MentorshipSession', foreign_keys='MentorshipSession.mentee_id', backref='session_mentee', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_mentor(self):
        return self.role == 'mentor'
    
    def is_mentee(self):
        return self.role == 'mentee'

class Skill(db.Model):
    __tablename__ = 'skills'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return self.name

class UserSkill(db.Model):
    __tablename__ = 'user_skills'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    skill = db.relationship('Skill', backref='user_skills')

class MentorAvailability(db.Model):
    __tablename__ = 'mentor_availability'
    
    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    
    def __repr__(self):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return f"{days[self.day_of_week]} {self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"

class MentorshipRequest(db.Model):
    __tablename__ = 'mentorship_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    mentee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'accepted', 'rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

class MentorshipSession(db.Model):
    __tablename__ = 'mentorship_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mentee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('mentorship_requests.id'))
    scheduled_time = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    status = db.Column(db.String(20), default='scheduled')  # 'scheduled', 'completed', 'cancelled'
    mentee_feedback = db.Column(db.Text)
    mentee_rating = db.Column(db.Integer)
    mentor_feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    request = db.relationship('MentorshipRequest', backref='sessions')