from flask import Flask, render_template, request, redirect, session, url_for
from models import db, User, StaffProfile, Trek, Booking
from datetime import datetime

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

    if role != 'trekker' and role != 'staff':
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

# -------- Admin ------------
@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role='trekker').count()
    total_staff = User.query.filter_by(role='staff').count()
    total_bookings = Booking.query.count()

    return render_template('admin/admin_dashboard.html', total_treks=total_treks, total_users=total_users, total_staff=total_staff, total_bookings=total_bookings)

@app.route('/admin/staff')
def manage_staff():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    staff_list = User.query.filter_by(role='staff').all()
    return render_template('admin/manage_staff.html', staff_list=staff_list)


@app.route('/admin/staff/approve/<int:id>')
def approve_staff(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    staff_user = User.query.get(id)

    if staff_user and staff_user.staff_profile:
        staff_user.staff_profile.is_approved = True
        db.session.commit()

    return redirect(url_for('manage_staff'))


@app.route('/admin/staff/remove/<int:id>')
def remove_staff(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    staff_user = User.query.get(id)
    if staff_user:
        if staff_user.staff_profile:
            db.session.delete(staff_user.staff_profile)
        db.session.delete(staff_user)
        db.session.commit()

    return redirect(url_for('manage_staff'))


@app.route('/admin/blacklist/<int:id>')
def toggle_blacklist(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    person = User.query.get(id)
    if person is None:
        return 'No such user'

    if person.role == 'admin':
        return 'Admin cannot be blacklisted'

    if person.is_blacklisted:
        person.is_blacklisted = False
    else:
        person.is_blacklisted = True
    db.session.commit()

    if person.role == 'staff':
        return redirect(url_for('manage_staff'))
    else:
        return redirect(url_for('manage_users'))


@app.route('/admin/users')
def manage_users():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    trekker_list = User.query.filter_by(role='trekker').all()
    return render_template('admin/manage_users.html', trekker_list=trekker_list)


@app.route('/admin/treks')
def manage_treks():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    trek_list = Trek.query.all()
    return render_template('admin/manage_treks.html', trek_list=trek_list)


@app.route('/admin/treks/create', methods=['GET', 'POST'])
def create_trek():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    approved_staff = User.query.join(StaffProfile).filter(User.role == 'staff', StaffProfile.is_approved == True).all()

    if request.method == 'GET':
        return render_template('admin/create_trek.html', staff_options=approved_staff)

    trek_name = request.form['name']
    location = request.form['location']
    difficulty = request.form['difficulty']

    try:
        duration_days = int(request.form['duration_days'])
        available_slots = int(request.form['available_slots'])
    except ValueError:
        return 'Duration and slots must be numbers'

    staff_choice = request.form.get('assigned_staff_id')

    t = Trek(name=trek_name, location=location, difficulty=difficulty, duration_days=duration_days, available_slots=available_slots, status='Pending') # type: ignore 

    if staff_choice:
        t.assigned_staff_id = int(staff_choice)

    start_str = request.form.get('start_date')
    end_str = request.form.get('end_date')
    if start_str:
        t.start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
    if end_str:
        t.end_date = datetime.strptime(end_str, '%Y-%m-%d').date()

    db.session.add(t)
    db.session.commit()

    return redirect(url_for('manage_treks'))


@app.route('/admin/treks/<int:id>/edit', methods=['GET', 'POST'])
def edit_trek(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    trek = Trek.query.get(id)
    if not trek:
        return 'Trek not found'

    if request.method == 'GET':
        approved_staff = User.query.join(StaffProfile).filter(User.role == 'staff', StaffProfile.is_approved == True).all()
        return render_template('admin/edit_trek.html', trek=trek, staff_options=approved_staff)

    trek.name = request.form['name']
    trek.location = request.form['location']
    trek.difficulty = request.form['difficulty']
    trek.duration_days = int(request.form['duration_days'])
    trek.available_slots = int(request.form['available_slots'])

    new_status = request.form.get('status')
    if new_status:
        trek.status = new_status

    staff_choice = request.form.get('assigned_staff_id')
    trek.assigned_staff_id = int(staff_choice) if staff_choice else None

    start_str = request.form.get('start_date')
    end_str = request.form.get('end_date')
    if start_str:
        trek.start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
    if end_str:
        trek.end_date = datetime.strptime(end_str, '%Y-%m-%d').date()

    db.session.commit()
    return redirect(url_for('manage_treks'))


@app.route('/admin/treks/<int:id>/delete')
def delete_trek(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    trek = Trek.query.get(id)
    if trek:
        Booking.query.filter_by(trek_id=trek.id).delete()
        db.session.delete(trek)
        db.session.commit()

    return redirect(url_for('manage_treks'))


@app.route('/admin/treks/<int:id>/assign', methods=['GET', 'POST'])
def assign_trek_staff(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    trek = Trek.query.get(id)
    if not trek:
        return 'Trek not found'

    approved_staff = User.query.join(StaffProfile).filter(User.role == 'staff', StaffProfile.is_approved == True).all()

    if request.method == 'GET':
        return render_template('admin/assign_staff.html', trek=trek, staff_options=approved_staff)

    chosen_id = request.form.get('staff_id')
    if not chosen_id:
        return 'Pick a staff member first'

    trek.assigned_staff_id = int(chosen_id)
    db.session.commit()

    return redirect(url_for('manage_treks'))


@app.route('/admin/search')
def admin_search():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    keyword = request.args.get('q', '').strip()
    search_in = request.args.get('type', 'trek')
    found = []

    if keyword != '':
        is_num = keyword.isdigit()

        if search_in == 'trek':
            if is_num:
                found = Trek.query.filter(Trek.id == int(keyword)).all()
            else:
                found = Trek.query.filter(Trek.name.ilike('%' + keyword + '%')).all()

        elif search_in == 'staff':
            if is_num:
                found = User.query.filter(User.role == 'staff', User.id == int(keyword)).all()
            else:
                found = User.query.filter(User.role == 'staff', User.name.ilike('%' + keyword + '%')).all()

        elif search_in == 'user':
            if is_num:
                found = User.query.filter(User.role == 'trekker', User.id == int(keyword)).all()
            else:
                found = User.query.filter(User.role == 'trekker', User.name.ilike('%' + keyword + '%')).all()

    return render_template('admin/search_results.html', results=found, keyword=keyword, search_in=search_in)


@app.route('/admin/bookings')
def admin_bookings():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    booking_list = Booking.query.order_by(Booking.booking_date.desc()).all()
    return render_template('admin/bookings.html', booking_list=booking_list)


# ------- Staff --------
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