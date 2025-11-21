from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import Reservation, Room
from app.extensions import db
from datetime import datetime

reservations_bp = Blueprint('reservations_api', __name__, url_prefix='/api/reservations')

@reservations_bp.route('', methods=['GET'])
@login_required
def get_reservations():
    if current_user.role != 'ADMIN':
        return jsonify({'error': 'Unauthorized'}), 403
        
    status = request.args.get('status')
    query = Reservation.query
    
    if status:
        query = query.filter_by(status=status)
        
    reservations = query.all()
    result = []
    for res in reservations:
        result.append({
            'id': res.id,
            'room_id': res.room_id,
            'guest_name': res.guest_name,
            'guest_email': res.guest_email,
            'check_in_date': res.check_in_date.isoformat(),
            'check_out_date': res.check_out_date.isoformat(),
            'status': res.status,
            'total_amount': float(res.total_amount) if res.total_amount else 0.0
        })
    return jsonify(result), 200

@reservations_bp.route('/<int:id>', methods=['GET'])
def get_reservation(id):
    res = Reservation.query.get_or_404(id)
    # Ideally check permissions here (admin or own reservation)
    return jsonify({
        'id': res.id,
        'room_id': res.room_id,
        'guest_name': res.guest_name,
        'guest_email': res.guest_email,
        'check_in_date': res.check_in_date.isoformat(),
        'check_out_date': res.check_out_date.isoformat(),
        'status': res.status,
        'total_amount': float(res.total_amount) if res.total_amount else 0.0
    }), 200

@reservations_bp.route('', methods=['POST'])
def create_reservation():
    data = request.get_json()
    
    guest_name = data.get('guest_name')
    guest_email = data.get('guest_email')
    room_id = data.get('room_id')
    check_in_str = data.get('check_in_date')
    check_out_str = data.get('check_out_date')
    
    # Validate required fields
    if not room_id or not check_in_str or not check_out_str:
        return jsonify({'error': 'Missing required fields: room_id, check_in_date, check_out_date'}), 400
    
    if not guest_name or not guest_email:
        return jsonify({'error': 'Missing required fields: guest_name, guest_email'}), 400

    # Parse dates
    try:
        check_in_date = datetime.strptime(check_in_str, '%Y-%m-%d').date()
        check_out_date = datetime.strptime(check_out_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format (use YYYY-MM-DD)'}), 400

    # Validate room exists
    room = Room.query.get(room_id)
    if not room:
        return jsonify({'error': 'Invalid room_id'}), 400
    
    # Validate dates
    days = (check_out_date - check_in_date).days
    if days <= 0:
        return jsonify({'error': 'Check-out must be after check-in'}), 400
    
    # Calculate total amount
    total_amount = days * float(room.base_price)

    # Create reservation (created_by will be set if user is logged in)
    new_res = Reservation(
        room_id=room_id,
        created_by=current_user.id if current_user.is_authenticated else None,
        guest_name=guest_name,
        guest_email=guest_email,
        check_in_date=check_in_date,
        check_out_date=check_out_date,
        status='PENDING',
        total_amount=total_amount
    )
    
    db.session.add(new_res)
    db.session.commit()
    
    return jsonify({'message': 'Reservation created', 'id': new_res.id}), 201

@reservations_bp.route('/<int:id>', methods=['PATCH'])
def update_reservation(id):
    # Ideally admin only or specific logic
    res = Reservation.query.get_or_404(id)
    data = request.get_json()
    
    if 'status' in data:
        res.status = data['status']
        
    db.session.commit()
    return jsonify({'message': 'Reservation updated'}), 200
