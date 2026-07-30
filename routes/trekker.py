from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from models import db, User, Trek, Booking

trekker_bp = Blueprint('trekker', __name__)


@trekker_bp.route('/trekker/dashboard')
def trekker_dashboard():
    if session.get('role') != 'trekker':
        return redirect(url_for('auth.login'))

    open_treks = Trek.query.filter_by(status='Open').count()
    total_bookings = Booking.query.filter_by(user_id=session['user_id']).count()

    return render_template('trekker/trekker_dashboard.html', open_treks=open_treks, total_bookings=total_bookings)


@trekker_bp.route('/trekker/profile', methods=['GET', 'POST'])
def trekker_profile():
    if session.get('role') != 'trekker':
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    if not user:
        return redirect(url_for('auth.login'))

    if request.method == 'GET':
        return render_template('trekker/profile.html', user=user)

    new_name = request.form['name'].strip()
    if len(new_name) < 2:
        flash('Name is too short')
        return redirect(url_for('trekker.trekker_profile'))
    user.name = new_name

    password = request.form.get('password')
    if password:
        if len(password) < 6:
            flash('Password must be at least 6 characters')
            return redirect(url_for('trekker.trekker_profile'))
        user.password = password

    db.session.commit()

    flash('Profile updated')
    return redirect(url_for('trekker.trekker_profile'))


@trekker_bp.route('/trekker/treks')
def browse_treks():
    if session.get('role') != 'trekker':
        return redirect(url_for('auth.login'))

    difficulty = request.args.get('difficulty')
    location = request.args.get('location')

    treks = Trek.query.filter_by(status='Open')

    if difficulty:
        treks = treks.filter(Trek.difficulty == difficulty)
    if location:
        treks = treks.filter(Trek.location.ilike('%' + location + '%'))

    trek_list = treks.all()

    return render_template('trekker/browse_treks.html', trek_list=trek_list, difficulty=difficulty, location=location)


@trekker_bp.route('/trekker/treks/<int:id>/book', methods=['POST'])
def book_trek(id):
    if session.get('role') != 'trekker':
        return redirect(url_for('auth.login'))

    trek = Trek.query.get(id)

    if not trek:
        flash('Trek not found')
        return redirect(url_for('trekker.browse_treks'))

    old_booking = Booking.query.filter_by(user_id=session['user_id'], trek_id=id, status='Booked').first()

    if old_booking:
        flash('You have already booked this trek')
        return redirect(url_for('trekker.browse_treks'))

    if trek.status != 'Open':
        flash('This trek is not open for booking')
        return redirect(url_for('trekker.browse_treks'))

    if trek.available_slots <= 0:
        flash('No slots left for this trek')
        return redirect(url_for('trekker.browse_treks'))

    new_booking = Booking(user_id=session['user_id'], trek_id=id, status='Booked')
    trek.available_slots = trek.available_slots - 1

    db.session.add(new_booking)
    db.session.commit()

    flash('Trek booked successfully!')
    return redirect(url_for('trekker.my_bookings'))


@trekker_bp.route('/trekker/bookings')
def my_bookings():
    if session.get('role') != 'trekker':
        return redirect(url_for('auth.login'))

    booking_list = Booking.query.filter_by(user_id=session['user_id']).order_by(Booking.booking_date.desc()).all()
    return render_template('trekker/my_bookings.html', booking_list=booking_list)
