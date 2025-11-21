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

@frontend_bp.route('/room/<int:room_id>', methods=['GET', 'POST'])
def room_checkout(room_id):
    from app.models import Customer
    room = Room.query.get_or_404(room_id)
    
    if request.method == 'POST':
        # Handle booking form submission
        from datetime import datetime
        from app.extensions import db
        
        # Get form data
        guest_name = request.form.get('guest_name')
        guest_email = request.form.get('guest_email')
        guest_phone = request.form.get('guest_phone')
        check_in_str = request.form.get('check_in_date')
        check_out_str = request.form.get('check_out_date')
        num_guests = request.form.get('num_guests', 1, type=int)
        
        # Validate
        if not all([guest_name, guest_email, check_in_str, check_out_str]):
            return render_template('room_checkout.html', room=room, error="All fields are required")
        
        try:
            check_in_date = datetime.strptime(check_in_str, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out_str, '%Y-%m-%d').date()
        except ValueError:
            return render_template('room_checkout.html', room=room, error="Invalid date format")
        
        # Calculate total
        days = (check_out_date - check_in_date).days
        if days <= 0:
            return render_template('room_checkout.html', room=room, error="Check-out must be after check-in")
        
        total_amount = days * float(room.base_price)
        
        # Determine customer_id and creator_id
        customer_id = None
        creator_id = None
        
        try:
            if current_user.is_authenticated:
                # Check if logged in as customer
                if isinstance(current_user._get_current_object(), Customer):
                    customer_id = current_user.id
                # Check if logged in as admin/staff
                else:
                    creator_id = current_user.id
        except:
            pass
        
        # Create reservation
        new_reservation = Reservation(
            room_id=room.id,
            created_by=creator_id,
            customer_id=customer_id,
            guest_name=guest_name,
            guest_email=guest_email,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            status='PENDING',
            total_amount=total_amount
        )
        
        db.session.add(new_reservation)
        db.session.commit()
        
        # Redirect to success page with booking ID
        from flask import redirect, url_for, session
        session['booking_id'] = new_reservation.id
        session['booking_email'] = guest_email
        return redirect(url_for('frontend.booking_success'))
    
    # GET request - pre-fill form if customer is logged in
    customer_data = None
    try:
        if current_user.is_authenticated and isinstance(current_user._get_current_object(), Customer):
            customer_data = {
                'full_name': current_user.full_name,
                'email': current_user.email,
                'phone': current_user.phone or ''
            }
    except:
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
