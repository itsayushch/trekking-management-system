from flask import Flask
from models import db

from routes.home import home_bp
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.staff import staff_bp
from routes.trekker import trekker_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trekking.db'
app.secret_key = 'mysecretkey'

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
