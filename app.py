import os
from flask import Flask
from models import db

from routes import home_bp, auth_bp, admin_bp, staff_bp, trekker_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trekking.db'
app.secret_key = os.environ.get('SECRET_KEY', 'mysecretkey')

db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(home_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(trekker_bp)

if __name__ == '__main__':
    app.run(debug=True)
