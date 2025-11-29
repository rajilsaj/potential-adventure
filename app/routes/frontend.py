from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_login import login_required, current_user
from app.models import Room, Reservation
from datetime import datetime

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
    
    # Calculate pagination display values
    start = (pagination.page - 1) * pagination.per_page + 1 if pagination.total > 0 else 0
    end = min(pagination.page * pagination.per_page, pagination.total)
    
    return render_template('rooms.html', 
                         rooms=pagination.items,
                         pagination=pagination,
                         search=search,
                         room_type=room_type,
                         min_price=min_price,
                         max_price=max_price,
                         start=start,
                         end=end)

def validate_step1_dates(check_in_str, check_out_str, reservation_type='C'):
    """
    Validate Step 1 booking dates with field-level error messages.
    
    Returns:
        tuple: (is_valid, errors_dict, nights)
        - is_valid: bool indicating if validation passed
        - errors_dict: dict with field names as keys and error messages as values
        - nights: int number of nights (0 if invalid)
    """
    import re
    from datetime import datetime, date
    
    errors = {}
    nights = 0
    
    # Strip whitespace
    check_in_str = check_in_str.strip() if check_in_str else ''
    check_out_str = check_out_str.strip() if check_out_str else ''
    
    # Check if dates are empty (including whitespace-only)
    if not check_in_str:
        errors['check_in'] = 'Check-in date is required'
    if not check_out_str:
        errors['check_out'] = 'Check-out date is required'
    
    # If either is empty, return early
    if errors:
        return False, errors, 0
    
    # Validate date format (YYYY-MM-DD)
    date_regex = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    
    if not date_regex.match(check_in_str):
        errors['check_in'] = 'Check-in date must be in format YYYY-MM-DD'
    if not date_regex.match(check_out_str):
        errors['check_out'] = 'Check-out date must be in format YYYY-MM-DD'
    
    # If format is invalid, return early
    if errors:
        return False, errors, 0
    
    # Try to parse dates
    try:
        check_in_date = datetime.strptime(check_in_str, '%Y-%m-%d').date()
    except ValueError:
        errors['check_in'] = 'Check-in date is not a valid date'
    
    try:
        check_out_date = datetime.strptime(check_out_str, '%Y-%m-%d').date()
    except ValueError:
        errors['check_out'] = 'Check-out date is not a valid date'
    
    # If parsing failed, return early
    if errors:
        return False, errors, 0
    
    # Validate check-in is not in the past
    today = date.today()
    if check_in_date < today:
        errors['check_in'] = 'Check-in date cannot be in the past'
    
    # Validate check-out is after check-in
    if check_out_date <= check_in_date:
        errors['check_out'] = 'Check-out date must be after check-in date'
    
    # If date logic is invalid, return early
    if errors:
        return False, errors, 0
    
    # Calculate nights
    nights = (check_out_date - check_in_date).days
    
    # Validate 60-Days-in-Advance requirement
    if reservation_type == 'D':
        days_until_checkin = (check_in_date - today).days
        if days_until_checkin < 60:
            errors['check_in'] = f'60-Days-in-Advance reservations must be made at least 60 days before arrival. You are booking {days_until_checkin} days in advance.'
    
    # Final validation
    is_valid = len(errors) == 0
    return is_valid, errors, nights


@frontend_bp.route('/room/<int:room_id>', methods=['GET', 'POST'])
def room_checkout(room_id):
    from app.models import Customer
    from app.extensions import db
    
    room = Room.query.get_or_404(room_id)
    
    if request.method == 'POST':
        # This is the API endpoint - it's handled by JavaScript
        # The actual form submission happens via AJAX in the template
        pass
    
    # GET request - pre-fill form if customer is logged in
    customer_data = None
    try:
        from flask_login import current_user as cu
        if cu.is_authenticated and isinstance(cu._get_current_object(), Customer):
            customer_data = {
                'full_name': cu.full_name,
                'email': cu.email,
                'phone': cu.phone or ''
            }
    except Exception:
        # If current_user not available, just show empty form
        pass
    
    return render_template('room_checkout.html', room=room, customer_data=customer_data)

@frontend_bp.route('/booking-success')
def booking_success():
    from flask import session
    booking_id = session.get('booking_id')
    booking_email = session.get('booking_email')
    return render_template('booking_success.html', booking_id=booking_id, booking_email=booking_email)

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
