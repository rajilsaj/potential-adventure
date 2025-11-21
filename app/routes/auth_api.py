from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app.extensions import db, bcrypt

auth_bp = Blueprint('auth_api', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400
        
    user = User.query.filter_by(username=username).first()
    
    if user and bcrypt.check_password_hash(user.password_hash, password):
        login_user(user)
        return jsonify({'message': 'logged in', 'role': user.role}), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'logged out'}), 200

@auth_bp.route('/register-admin', methods=['POST'])
def register_admin():
    # Optional: Check if any admin exists, if so, require auth
    if User.query.filter_by(role='ADMIN').first():
         return jsonify({'error': 'Admin already exists, cannot register via public endpoint'}), 403

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400
        
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password_hash=hashed_password, role='ADMIN')
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'Admin registered successfully'}), 201
