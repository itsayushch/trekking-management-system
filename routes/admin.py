from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from datetime import datetime
from models import db, User, StaffProfile, Trek, Booking
from constants import TREK_STATUSES, DIFFICULTY_LEVELS

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role='trekker').count()
    total_staff = User.query.filter_by(role='staff').count()
    total_bookings = Booking.query.count()

    return render_template('admin/admin_dashboard.html', total_treks=total_treks, total_users=total_users, total_staff=total_staff, total_bookings=total_bookings)

@admin_bp.route('/admin/staff')
def manage_staff():
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    staff_list = User.query.filter_by(role='staff').all()
    return render_template('admin/manage_staff.html', staff_list=staff_list)


@admin_bp.route('/admin/staff/approve/<int:id>')
def approve_staff(id):
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    staff_user = User.query.get(id)

    if staff_user and staff_user.staff_profile:
        staff_user.staff_profile.is_approved = True
        db.session.commit()

    return redirect(url_for('admin.manage_staff'))


@admin_bp.route('/admin/staff/remove/<int:id>')
def remove_staff(id):
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    staff_user = User.query.get(id)
    if staff_user:
        if staff_user.staff_profile:
            db.session.delete(staff_user.staff_profile)
        db.session.delete(staff_user)
        db.session.commit()

    return redirect(url_for('admin.manage_staff'))


@admin_bp.route('/admin/blacklist/<int:id>')
def toggle_blacklist(id):
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    person = User.query.get(id)

    if not person:
        flash('No such user')
        return redirect(request.referrer or url_for('admin.admin_dashboard'))

    if person.role == 'admin':
        flash('Admin cannot be blacklisted!')
        return redirect(request.referrer or url_for('admin.admin_dashboard'))

    if person.is_blacklisted:
        person.is_blacklisted = False
    else:
        person.is_blacklisted = True

    db.session.commit()

    if (person.role == 'staff'):
        return redirect(url_for('admin.manage_staff'))
    else:
        return redirect(url_for('admin.manage_users'))

@admin_bp.route('/admin/users')
def manage_users():
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    trekker_list = User.query.filter_by(role='trekker').all()
    return render_template('admin/manage_users.html', trekker_list=trekker_list)


@admin_bp.route('/admin/treks')
def manage_treks():
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    trek_list = Trek.query.all()
    return render_template('admin/manage_treks.html', trek_list=trek_list)


@admin_bp.route('/admin/treks/create', methods=['GET', 'POST'])
def create_trek():
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    approved_staff = User.query.join(StaffProfile).filter(User.role == 'staff', StaffProfile.is_approved == True).all()

    if request.method == 'GET':
        return render_template('admin/create_trek.html', staff_options=approved_staff)

    name = request.form['name'].strip()
    location = request.form['location'].strip()
    difficulty = request.form['difficulty']

    if not name or not location:
        flash('Trek name and location are required')
        return redirect(url_for('admin.create_trek'))

    if difficulty not in DIFFICULTY_LEVELS:
        flash('Invalid difficulty')
        return redirect(url_for('admin.create_trek'))

    try:
        duration_days = int(request.form['duration_days'])
        available_slots = int(request.form['available_slots'])
    except ValueError:
        flash('Duration and slots must be numbers')
        return redirect(url_for('admin.create_trek'))

    if duration_days < 1:
        flash('Duration must be at least 1 day')
        return redirect(url_for('admin.create_trek'))

    if available_slots < 0:
        flash('Available slots cannot be negative')
        return redirect(url_for('admin.create_trek'))

    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    if start_date and end_date and end_date < start_date:
        flash('End date cannot be before start date')
        return redirect(url_for('admin.create_trek'))

    new_trek = Trek(name=name, location=location, difficulty=difficulty, duration_days=duration_days, available_slots=available_slots, status='Pending') # type: ignore

    staff_choice = request.form.get('assigned_staff_id')
    if staff_choice:
        new_trek.assigned_staff_id = int(staff_choice)

    if start_date:
        new_trek.start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date:
        new_trek.end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    db.session.add(new_trek)
    db.session.commit()

    return redirect(url_for('admin.manage_treks'))


@admin_bp.route('/admin/treks/<int:id>/edit', methods=['GET', 'POST'])
def edit_trek(id):
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    trek = Trek.query.get(id)

    if not trek:
        flash('Trek not found')
        return redirect(url_for('admin.manage_treks'))

    if request.method == 'GET':
        approved_staff = User.query.join(StaffProfile).filter(User.role == 'staff', StaffProfile.is_approved == True).all()
        return render_template('admin/edit_trek.html', trek=trek, staff_options=approved_staff)

    name = request.form['name'].strip()
    location = request.form['location'].strip()
    difficulty = request.form['difficulty']

    if not name or not location:
        flash('Trek name and location are required')
        return redirect(url_for('admin.edit_trek', id=id))

    if difficulty not in DIFFICULTY_LEVELS:
        flash('Invalid difficulty')
        return redirect(url_for('admin.edit_trek', id=id))

    try:
        duration_days = int(request.form['duration_days'])
        available_slots = int(request.form['available_slots'])
    except ValueError:
        flash('Duration and slots must be numbers')
        return redirect(url_for('admin.edit_trek', id=id))

    if duration_days < 1:
        flash('Duration must be at least 1 day')
        return redirect(url_for('admin.edit_trek', id=id))

    if available_slots < 0:
        flash('Available slots cannot be negative')
        return redirect(url_for('admin.edit_trek', id=id))

    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    if start_date and end_date and end_date < start_date:
        flash('End date cannot be before start date')
        return redirect(url_for('admin.edit_trek', id=id))

    trek.name = name
    trek.location = location
    trek.difficulty = difficulty
    trek.duration_days = duration_days
    trek.available_slots = available_slots

    new_status = request.form.get('status')
    if new_status:
        if new_status not in TREK_STATUSES:
            flash('Invalid status')
            return redirect(url_for('admin.edit_trek', id=id))
        trek.status = new_status

    staff_choice = request.form.get('assigned_staff_id')
    if staff_choice:
        trek.assigned_staff_id = int(staff_choice)
    else:
        trek.assigned_staff_id = None

    if start_date:
        trek.start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date:
        trek.end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    db.session.commit()

    return redirect(url_for('admin.manage_treks'))


@admin_bp.route('/admin/treks/<int:id>/delete')
def delete_trek(id):
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    trek = Trek.query.get(id)

    if not trek:
        return redirect(url_for('admin.manage_treks'))

    old_bookings = Booking.query.filter_by(trek_id=trek.id).count()
    if old_bookings > 0:
        flash('This trek has booking history, cannot be deleted')
        return redirect(url_for('admin.manage_treks'))

    db.session.delete(trek)
    db.session.commit()

    return redirect(url_for('admin.manage_treks'))


@admin_bp.route('/admin/treks/<int:id>/assign', methods=['GET', 'POST'])
def assign_trek_staff(id):
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    trek = Trek.query.get(id)

    if not trek:
        flash('Trek not found')
        return redirect(url_for('admin.manage_treks'))

    approved_staff = User.query.join(StaffProfile).filter(User.role == 'staff', StaffProfile.is_approved == True).all()

    if request.method == 'GET':
        return render_template('admin/assign_staff.html', trek=trek, staff_options=approved_staff)

    staff_id = request.form.get('staff_id')

    if not staff_id:
        flash('Please select a staff member')
        return redirect(url_for('admin.assign_trek_staff', id=id))

    picked_staff = User.query.get(int(staff_id))

    if not picked_staff or picked_staff.role != 'staff':
        flash('That staff member does not exist')
        return redirect(url_for('admin.assign_trek_staff', id=id))

    if not picked_staff.staff_profile or not picked_staff.staff_profile.is_approved:
        flash('That staff member is not approved yet')
        return redirect(url_for('admin.assign_trek_staff', id=id))

    trek.assigned_staff_id = picked_staff.id
    db.session.commit()

    return redirect(url_for('admin.manage_treks'))


@admin_bp.route('/admin/search')
def admin_search():
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    keyword = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'trek')
    results = []

    if keyword != '':
        if search_type == 'trek':
            if keyword.isdigit():
                results = Trek.query.filter(Trek.id == int(keyword)).all()
            else:
                results = Trek.query.filter(Trek.name.ilike('%' + keyword + '%')).all()

        elif search_type == 'staff':
            if keyword.isdigit():
                results = User.query.filter(User.role == 'staff', User.id == int(keyword)).all()
            else:
                results = User.query.filter(User.role == 'staff', User.name.ilike('%' + keyword + '%')).all()

        elif search_type == 'user':
            if keyword.isdigit():
                results = User.query.filter(User.role == 'trekker', User.id == int(keyword)).all()
            else:
                results = User.query.filter(User.role == 'trekker', User.name.ilike('%' + keyword + '%')).all()

    return render_template('admin/search_results.html', results=results, keyword=keyword, search_type=search_type)


@admin_bp.route('/admin/bookings')
def admin_bookings():
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    booking_list = Booking.query.order_by(Booking.booking_date.desc()).all()
    return render_template('admin/bookings.html', booking_list=booking_list)


@admin_bp.route('/admin/users/<int:id>/history')
def admin_user_history(id):
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))

    person = User.query.get(id)

    if not person:
        flash('User not found')
        return redirect(url_for('admin.manage_users'))

    history = Booking.query.filter_by(user_id=id).order_by(Booking.booking_date.desc()).all()
    return render_template('admin/user_history.html', person=person, history=history)
