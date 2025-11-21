from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models import Room, Reservation

frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/')
def index():
    return render_template('index.html')

@frontend_bp.route('/rooms')
def rooms():
    rooms = Room.query.filter_by(status='AVAILABLE').all()
    return render_template('rooms.html', rooms=rooms)

@frontend_bp.route('/room/<int:room_id>')
def room_checkout(room_id):
    room = Room.query.get_or_404(room_id)
    return render_template('room_checkout.html', room=room)

@frontend_bp.route('/booking-success')
def booking_success():
    return render_template('booking_success.html')

@frontend_bp.route('/admin/login')
def admin_login():
    return render_template('admin_login.html')

@frontend_bp.route('/admin/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@frontend_bp.route('/admin/rooms')
def manage_rooms():
    return render_template('manage_rooms.html')

@frontend_bp.route('/my-bookings')
@login_required
def my_bookings():
    # Fetch reservations for the current user
    # Assuming guest_email matches the user's email/username for now
    reservations = Reservation.query.filter_by(guest_email=current_user.username).all()
    return render_template('my_bookings.html', reservations=reservations)
