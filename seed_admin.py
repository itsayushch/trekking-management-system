import os
from werkzeug.security import generate_password_hash
from app import app
from models import db, User

ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@gmail.com')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123') 

with app.app_context():
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        new_admin = User(name='Admin', email=ADMIN_EMAIL, password=generate_password_hash(ADMIN_PASSWORD), role='admin')
        db.session.add(new_admin)
        db.session.commit()
        print("Admin created")
    else:
        print("Admin already exists")