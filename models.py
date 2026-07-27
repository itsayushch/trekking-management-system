from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(20))  # admin, staff, trekker
    is_blacklisted = db.Column(db.Boolean, default=False)

class StaffProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    contact_details = db.Column(db.String(120))
    status = db.Column(db.String(20), default="Active")
    
    # Relationships
    user = db.relationship('User', backref='staff_profile', uselist=False)

class Trek(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    location = db.Column(db.String(120))
    difficulty = db.Column(db.String(20))
    duration_days = db.Column(db.Integer)
    available_slots = db.Column(db.Integer)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default="Pending")
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    
    # Relationships
    assigned_staff = db.relationship('User', backref='treks_assigned')

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    trek_id = db.Column(db.Integer, db.ForeignKey('trek.id'))
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="Booked")
    payment_status = db.Column(db.String(20), default="Pending")
    
    # Relationships
    user = db.relationship('User', backref='bookings')
    trek = db.relationship('Trek', backref='bookings')