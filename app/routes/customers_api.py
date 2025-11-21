from flask import Blueprint, request, jsonify
from app.models import Reservation
from app.extensions import db
from sqlalchemy import func

customers_bp = Blueprint('customers_api', __name__, url_prefix='/api/customers')

@customers_bp.route('', methods=['POST'])
def create_customer():
    """
    Create a customer by creating a reservation with guest details.
    Since we removed the Customer model, we work directly with guest_email.
    """
    data = request.get_json()
    
    # Validate required fields
    if not data.get('email'):
        return jsonify({'error': 'Email is required'}), 400
    
    # Return success - in the new model, customers are tracked via reservations
    return jsonify({
        'message': 'Customer info recorded',
        'email': data.get('email')
    }), 201

@customers_bp.route('/<email>', methods=['GET'])
def get_customer(email):
    """Get customer info based on their email from reservations"""
    # Find any reservation with this email
    reservation = Reservation.query.filter_by(guest_email=email).first()
    
    if not reservation:
        return jsonify({'error': 'Customer not found'}), 404
    
    return jsonify({
        'email': reservation.guest_email,
        'name': reservation.guest_name
    }), 200

@customers_bp.route('/<email>/reservations', methods=['GET'])
def get_customer_reservations(email):
    """Get all reservations for a customer by email"""
    reservations = Reservation.query.filter_by(guest_email=email).all()
    
    result = []
    for res in reservations:
        result.append({
            'id': res.id,
            'room_id': res.room_id,
            'guest_name': res.guest_name,
            'check_in_date': res.check_in_date.isoformat(),
            'check_out_date': res.check_out_date.isoformat(),
            'status': res.status,
            'total_amount': float(res.total_amount) if res.total_amount else None
        })
    
    return jsonify(result), 200

@customers_bp.route('/count', methods=['GET'])
def get_customer_count():
    """Get count of unique customers (unique emails)"""
    count = db.session.query(func.count(func.distinct(Reservation.guest_email))).scalar()
    return jsonify({'count': count or 0}), 200
