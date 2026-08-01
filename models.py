from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(255))  # stores a hashed password, not plain text
    role = db.Column(db.String(20))  # admin, staff, trekker
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class StaffProfile(db.Model):
    __tablename__ = 'staff_profile'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    contact_details = db.Column(db.String(120))
    status = db.Column(db.String(20), default="Active")
    is_approved = db.Column(db.Boolean, default=False) 
    
    # Relationships
    user = db.relationship('User', backref=db.backref('staff_profile', uselist=False))

class Trek(db.Model):
    __tablename__ = 'trek'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    location = db.Column(db.String(120))
    difficulty = db.Column(db.String(20))
    duration_days = db.Column(db.Integer)
    available_slots = db.Column(db.Integer)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default="Pending")
    progress_status = db.Column(db.String(20), default="Not Started")
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    
    # Relationships
    assigned_staff = db.relationship('User', backref='treks_assigned')

class Booking(db.Model):
    __tablename__ = 'booking'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    trek_id = db.Column(db.Integer, db.ForeignKey('trek.id'))
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="Booked")
    payment_status = db.Column(db.String(20), default="Pending")
    
    # Relationships
    user = db.relationship('User', backref='bookings')
    trek = db.relationship('Trek', backref='bookings')