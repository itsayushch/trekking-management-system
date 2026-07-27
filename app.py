from flask import Flask, render_template, request, redirect, session, url_for
from models import db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trekking.db'
app.secret_key = 'mysecretkey'

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "Hello World"

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')

    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']

    if role != 'trekker' or role != 'staff':
        return "Invalid role"

    user = User.query.filter_by(email=email).first()

    if user:
        return 'Account already exists'

    new_user = User(name=name, email=email, password=password, role=role) # type: ignore
    db.session.add(new_user)
    db.session.commit()

    if role == 'staff':
        new_profile = StaffProfile(user_id=new_user.id)  # type: ignore
        db.session.add(new_profile)
        db.session.commit()

        return "Registered Successfully! Please wait for Admin approval before logging in."

    return redirect(url_for('login'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email=email, password=password).first()

    if not user:
        return 'Incorrect Email or Password'

    if user.is_blacklisted:
        return 'Your account has been blacklisted!'

    if user.role == 'staff':
        if not user.staff_profile or not user.staff_profile.is_approved:
            return "Your staff account is pending Admin approval"

    session['user_id'] = user.id
    session['role'] = user.role

    if (user.role == 'admin'):
        return redirect(url_for('admin_dashboard'))
    elif (user.role == 'staff'):
        return redirect(url_for('staff_dashboard'))
    else:
        return redirect(url_for('trekker_dashboard'))


@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    return render_template('admin/admin_dashboard.html')

@app.route('/staff/dashboard')
def staff_dashboard():
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
    return render_template('staff/staff_dashboard.html')

@app.route('/trekker/dashboard')
def trekker_dashboard():
    if session.get('role') != 'trekker':
        return redirect(url_for('login'))
    return render_template('trekker/trekker_dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)