from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from models import db, User, Trek, Booking
from constants import TREK_PROGRESS_STATUSES

staff_bp = Blueprint('staff', __name__)


@staff_bp.route('/staff/dashboard')
def staff_dashboard():
    if session.get('role') != 'staff':
        return redirect(url_for('auth.login'))

    my_treks = Trek.query.filter_by(assigned_staff_id=session['user_id']).all()

    trek_data = []
    for trek in my_treks:
        total = Booking.query.filter_by(trek_id=trek.id, status='Booked').count()
        trek_data.append((trek, total))

    return render_template('staff/staff_dashboard.html', trek_data=trek_data)


@staff_bp.route('/staff/profile', methods=['GET', 'POST'])
def staff_profile():
    if session.get('role') != 'staff':
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    if not user:
        return redirect(url_for('auth.login'))

    if request.method == 'GET':
        return render_template('staff/profile.html', user=user)

    new_name = request.form['name'].strip()
    if len(new_name) < 2:
        flash('Name is too short')
        return redirect(url_for('staff.staff_profile'))
    user.name = new_name

    if user.staff_profile:
        user.staff_profile.contact_details = request.form.get('contact_details')

    password = request.form.get('password')
    if password:
        if len(password) < 6:
            flash('Password must be at least 6 characters')
            return redirect(url_for('staff.staff_profile'))
        user.password = password

    db.session.commit()

    flash('Profile updated')
    return redirect(url_for('staff.staff_profile'))


@staff_bp.route('/staff/treks/<int:id>')
def staff_view_trek(id):
    if session.get('role') != 'staff':
        return redirect(url_for('auth.login'))

    trek = Trek.query.get(id)

    if not trek:
        flash('Trek not found')
        return redirect(url_for('staff.staff_dashboard'))

    if trek.assigned_staff_id != session['user_id']:
        flash('This trek is not assigned to you')
        return redirect(url_for('staff.staff_dashboard'))

    participants = Booking.query.filter_by(trek_id=trek.id).all()
    return render_template('staff/trek_detail.html', trek=trek, participants=participants)


@staff_bp.route('/staff/treks/<int:id>/update', methods=['POST'])
def staff_update_trek(id):
    if session.get('role') != 'staff':
        return redirect(url_for('auth.login'))

    trek = Trek.query.get(id)

    if not trek:
        flash('Trek not found')
        return redirect(url_for('staff.staff_dashboard'))

    if trek.assigned_staff_id != session['user_id']:
        flash('This trek is not assigned to you')
        return redirect(url_for('staff.staff_dashboard'))

    slots = request.form.get('available_slots')
    if slots:
        try:
            new_slots = int(slots)
        except ValueError:
            flash('Slots must be a number')
            return redirect(url_for('staff.staff_view_trek', id=id))

        if new_slots < 0:
            flash('Slots cannot be negative')
            return redirect(url_for('staff.staff_view_trek', id=id))

        trek.available_slots = new_slots

    new_status = request.form.get('status')

    if new_status in ['Open', 'Closed', 'Completed']:
        trek.status = new_status

        if new_status == 'Completed':
            running = Booking.query.filter_by(trek_id=trek.id, status='Booked').all()
            for booking in running:
                booking.status = 'Completed'

    new_progress = request.form.get('progress_status')

    if new_progress in TREK_PROGRESS_STATUSES:
        trek.progress_status = new_progress

    db.session.commit()

    return redirect(url_for('staff.staff_view_trek', id=trek.id))


@staff_bp.route('/staff/treks/<int:trek_id>/participant/<int:booking_id>', methods=['POST'])
def staff_update_participant(trek_id, booking_id):
    if session.get('role') != 'staff':
        return redirect(url_for('auth.login'))

    trek = Trek.query.get(trek_id)

    if not trek or trek.assigned_staff_id != session['user_id']:
        flash('This trek is not assigned to you')
        return redirect(url_for('staff.staff_dashboard'))

    booking = Booking.query.get(booking_id)

    if not booking or booking.trek_id != trek_id:
        flash('Booking not found')
        return redirect(url_for('staff.staff_view_trek', id=trek_id))

    new_status = request.form.get('status')

    if new_status not in ['Booked', 'Cancelled', 'Completed']:
        return redirect(url_for('staff.staff_view_trek', id=trek_id))

    old_status = booking.status

    if old_status == 'Booked' and new_status == 'Cancelled':
        trek.available_slots = trek.available_slots + 1
    elif old_status == 'Cancelled' and new_status == 'Booked':
        if trek.available_slots <= 0:
            flash('No slots left to reinstate this booking')
            return redirect(url_for('staff.staff_view_trek', id=trek_id))
        trek.available_slots = trek.available_slots - 1

    booking.status = new_status
    db.session.commit()

    return redirect(url_for('staff.staff_view_trek', id=trek_id))
