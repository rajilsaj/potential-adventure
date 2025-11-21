from flask import Blueprint, request, jsonify
from app.models import Customer, Reservation
from app.extensions import db

customers_bp = Blueprint('customers_api', __name__, url_prefix='/api/customers')

@customers_bp.route('', methods=['POST'])
def create_customer():
    data = request.get_json()
    
    if Customer.query.filter_by(email=data.get('email')).first():
        return jsonify({'error': 'Email already exists'}), 400
        
    new_customer = Customer(
        full_name=data.get('full_name'),
        email=data.get('email'),
        phone=data.get('phone')
    )
    
    db.session.add(new_customer)
    db.session.commit()
    
    return jsonify({'message': 'Customer created', 'id': new_customer.id}), 201

@customers_bp.route('/<int:id>', methods=['GET'])
def get_customer(id):
    customer = Customer.query.get_or_404(id)
    return jsonify({
        'id': customer.id,
        'full_name': customer.full_name,
        'email': customer.email,
        'phone': customer.phone
    }), 200

@customers_bp.route('/<int:id>/reservations', methods=['GET'])
def get_customer_reservations(id):
    customer = Customer.query.get_or_404(id)
    reservations = []
    for res in customer.reservations:
        reservations.append({
            'id': res.id,
            'room_id': res.room_id,
            'check_in_date': res.check_in_date.isoformat(),
            'check_out_date': res.check_out_date.isoformat(),
            'status': res.status
        })
    return jsonify(reservations), 200
