from flask import Flask
from sqlalchemy import text
from models import db

from routes import home_bp, auth_bp, admin_bp, staff_bp, trekker_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trekking.db'
app.secret_key = 'mysecretkey'

db.init_app(app)

with app.app_context():
    db.create_all()

    # added progress_status to the trek table after the db already existed,
    # so this just patches old databases instead of wiping existing data
    existing_columns = [row[1] for row in db.session.execute(text("PRAGMA table_info(trek)"))]
    if 'progress_status' not in existing_columns:
        db.session.execute(text("ALTER TABLE trek ADD COLUMN progress_status VARCHAR(20) DEFAULT 'Not Started'"))
        db.session.commit()

app.register_blueprint(home_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(trekker_bp)

if __name__ == '__main__':
    app.run(debug=True)
