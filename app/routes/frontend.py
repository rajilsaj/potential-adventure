from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models import Room, Reservation

frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/')
def index():
    return render_template('index.html')

@frontend_bp.route('/rooms')
def rooms():
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    room_type = request.args.get('room_type', '', type=str)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    # Build query
    query = Room.query.filter_by(status='AVAILABLE')
    
    # Apply filters
    if search:
        query = query.filter(Room.room_number.like(f'%{search}%'))
    
    if room_type:
        query = query.filter_by(room_type=room_type)
    
    if min_price is not None:
        query = query.filter(Room.base_price >= min_price)
    
    if max_price is not None:
        query = query.filter(Room.base_price <= max_price)
    
    # Paginate results - 10 per page
    pagination = query.order_by(Room.room_number).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('rooms.html', 
                         rooms=pagination.items,
                         pagination=pagination,
                         search=search,
                         room_type=room_type,
                         min_price=min_price,
                         max_price=max_price)

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
def my_bookings():
    # Public booking tracker - guests can check their bookings by email
    email = request.args.get('email', '')
    
    if email:
        reservations = Reservation.query.filter_by(guest_email=email).order_by(Reservation.created_at.desc()).all()
    else:
        reservations = []
    
    return render_template('my_bookings.html', reservations=reservations, email=email)
