from flask import Blueprint, jsonify
from flask_login import login_required
from app.models import Reservation, Room, User
from app.extensions import db
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard_api', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/summary', methods=['GET'])
@login_required
def get_summary():
    """Get dashboard summary statistics"""
    
    # Count users by role
    total_users = User.query.count()
    admin_count = User.query.filter_by(role='ADMIN').count()
    staff_count = User.query.filter_by(role='STAFF').count()
    
    # Count rooms by status
    total_rooms = Room.query.count()
    available_rooms = Room.query.filter_by(status='AVAILABLE').count()
    out_of_service_rooms = Room.query.filter_by(status='OUT_OF_SERVICE').count()
    
    # Count reservations by status
    total_reservations = Reservation.query.count()
    pending_reservations = Reservation.query.filter_by(status='PENDING').count()
    booked_reservations = Reservation.query.filter_by(status='BOOKED').count()
    checked_in_reservations = Reservation.query.filter_by(status='CHECKED_IN').count()
    checked_out_reservations = Reservation.query.filter_by(status='CHECKED_OUT').count()
    cancelled_reservations = Reservation.query.filter_by(status='CANCELLED').count()
    
    # Count currently booked rooms (active reservations)
    active_statuses = ['PENDING', 'BOOKED', 'CHECKED_IN']
    booked_rooms_count = db.session.query(func.count(func.distinct(Reservation.room_id)))\
        .filter(Reservation.status.in_(active_statuses)).scalar()
    
    # Get unique guest emails (customers)
    unique_customers = db.session.query(func.count(func.distinct(Reservation.guest_email))).scalar()
    
    return jsonify({
        # Users
        'total_users': total_users,
        'admin_count': admin_count,
        'staff_count': staff_count,
        
        # Rooms
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'booked_rooms': booked_rooms_count,
        'out_of_service_rooms': out_of_service_rooms,
        
        # Reservations
        'total_reservations': total_reservations,
        'pending_reservations': pending_reservations,
        'booked_reservations': booked_reservations,
        'checked_in_reservations': checked_in_reservations,
        'checked_out_reservations': checked_out_reservations,
        'cancelled_reservations': cancelled_reservations,
        
        # Customers
        'total_customers': unique_customers,
        
        # Legacy format for compatibility
        'PENDING': pending_reservations,
        'BOOKED': booked_reservations,
        'CHECKED_IN': checked_in_reservations,
        'CHECKED_OUT': checked_out_reservations,
        'CANCELLED': cancelled_reservations,
        'confirmed_reservations': booked_reservations + checked_in_reservations
    }), 200
