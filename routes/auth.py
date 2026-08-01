from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, StaffProfile

auth_bp = Blueprint('auth', __name__)



@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        if (session.get('user_id')):
            role = session.get('role')
            if role == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            elif role == 'staff':
                return redirect(url_for('staff.staff_dashboard'))
            else:
                return redirect(url_for('trekker.trekker_dashboard'))
        return render_template('signup.html')

    name = request.form['name'].strip()
    email = request.form['email'].strip()
    password = request.form['password']
    role = request.form['role']

    if role != 'trekker' and role != 'staff':
        flash('Invalid role')
        return redirect(url_for('auth.signup'))

    if len(name) < 2:
        flash('Name is too short')
        return redirect(url_for('auth.signup'))

    if '@' not in email or '.' not in email.split('@')[-1]:
        flash('Enter a valid email address')
        return redirect(url_for('auth.signup'))

    if len(password) < 6:
        flash('Password must be at least 6 characters')
        return redirect(url_for('auth.signup'))

    user = User.query.filter_by(email=email).first()

    if user:
        flash('Account already exists')
        return redirect(url_for('auth.signup'))

    new_user = User(name=name, email=email, password=generate_password_hash(password), role=role)
    db.session.add(new_user)
    db.session.commit()

    if role == 'staff':
        new_profile = StaffProfile(user_id=new_user.id)  
        db.session.add(new_profile)
        db.session.commit()

        flash('Registered successfully! Please wait for Admin approval before logging in.')
        return redirect(url_for('auth.login'))

    flash('Registered successfully! You can log in now.')
    return redirect(url_for('auth.login'))



@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if (session.get('user_id')):           
            role = session.get('role')
            if role == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            elif role == 'staff':
                return redirect(url_for('staff.staff_dashboard'))
            else:
                return redirect(url_for('trekker.trekker_dashboard'))

        return render_template('login.html')

    email = request.form['email']
    password = request.form['password']

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash('Incorrect Email or Password')
        return redirect(url_for('auth.login'))

    if user.is_blacklisted:
        flash('Your account has been blacklisted!')
        return redirect(url_for('auth.login'))

    if user.role == 'staff':
        if not user.staff_profile or not user.staff_profile.is_approved:
            flash('Your staff account is pending Admin approval')
            return redirect(url_for('auth.login'))

    session['user_id'] = user.id
    session['role'] = user.role

    if (user.role == 'admin'):
        return redirect(url_for('admin.admin_dashboard'))
    elif (user.role == 'staff'):
        return redirect(url_for('staff.staff_dashboard'))
    else:
        return redirect(url_for('trekker.trekker_dashboard'))


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home.home'))
