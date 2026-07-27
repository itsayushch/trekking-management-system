from app import app
from models import db, User

with app.app_context():
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        new_admin = User(name='Admin', email='admin@gmail.com', password='admin123', role='admin') # type: ignore
        db.session.add(new_admin)
        db.session.commit()
        print("Admin created")
    else:
        print("Admin already exists")