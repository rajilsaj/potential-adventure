from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import Room
from app.extensions import db

rooms_bp = Blueprint('rooms_api', __name__, url_prefix='/api/rooms')

@rooms_bp.route('', methods=['GET'])
def get_rooms():
    rooms = Room.query.all()
    result = []
    for room in rooms:
        result.append({
            'id': room.id,
            'room_number': room.room_number,
            'floor': room.floor,
            'room_type': room.room_type,
            'capacity': room.capacity,
            'status': room.status,
            'base_price': float(room.base_price)
        })
    return jsonify(result), 200

@rooms_bp.route('/<int:id>', methods=['GET'])
def get_room(id):
    room = Room.query.get_or_404(id)
    return jsonify({
        'id': room.id,
        'room_number': room.room_number,
        'floor': room.floor,
        'room_type': room.room_type,
        'capacity': room.capacity,
        'status': room.status,
        'base_price': float(room.base_price)
    }), 200

@rooms_bp.route('', methods=['POST'])
@login_required
def create_room():
    if current_user.role != 'ADMIN':
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    
    new_room = Room(
        room_number=data.get('room_number'),
        floor=data.get('floor'),
        room_type=data.get('room_type'),
        capacity=data.get('capacity'),
        status=data.get('status', 'AVAILABLE'),
        base_price=data.get('base_price')
    )
    
    db.session.add(new_room)
    db.session.commit()
    
    return jsonify({'message': 'Room created', 'id': new_room.id}), 201

@rooms_bp.route('/<int:id>', methods=['PATCH'])
@login_required
def update_room(id):
    if current_user.role != 'ADMIN':
        return jsonify({'error': 'Unauthorized'}), 403
        
    room = Room.query.get_or_404(id)
    data = request.get_json()
    
    if 'room_number' in data: room.room_number = data['room_number']
    if 'floor' in data: room.floor = data['floor']
    if 'room_type' in data: room.room_type = data['room_type']
    if 'capacity' in data: room.capacity = data['capacity']
    if 'status' in data: room.status = data['status']
    if 'base_price' in data: room.base_price = data['base_price']
    
    db.session.commit()
    
    return jsonify({'message': 'Room updated'}), 200
