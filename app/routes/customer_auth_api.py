from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models import Customer
from app.extensions import db, bcrypt

customer_auth_bp = Blueprint('customer_auth', __name__, url_prefix='/api/customer')

@customer_auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new customer account"""
    data = request.get_json()
    
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    phone = data.get('phone')
    
    # Validate
    if not email or not password or not full_name:
        return jsonify({'error': 'Email, password, and full name are required'}), 400
    
    # Check if customer already exists
    if Customer.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create customer
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_customer = Customer(
        email=email,
        password_hash=hashed_password,
        full_name=full_name,
        phone=phone
    )
    
    db.session.add(new_customer)
    db.session.commit()
    
    # Auto-login after registration
    login_user(new_customer)
    
    return jsonify({
        'message': 'Registration successful',
        'customer': {
            'id': new_customer.id,
            'email': new_customer.email,
            'full_name': new_customer.full_name
        }
    }), 201

@customer_auth_bp.route('/login', methods=['POST'])
def login():
    """Customer login"""
    data = request.get_json()
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    customer = Customer.query.filter_by(email=email).first()
    
    if customer and bcrypt.check_password_hash(customer.password_hash, password):
        login_user(customer)
        return jsonify({
            'message': 'Login successful',
            'customer': {
                'id': customer.id,
                'email': customer.email,
                'full_name': customer.full_name
            }
        }), 200
    
    return jsonify({'error': 'Invalid email or password'}), 401

@customer_auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Customer logout"""
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@customer_auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_customer():
    """Get current logged-in customer info"""
    if isinstance(current_user._get_current_object(), Customer):
        return jsonify({
            'id': current_user.id,
            'email': current_user.email,
            'full_name': current_user.full_name,
            'phone': current_user.phone
        }), 200
    return jsonify({'error': 'Not logged in as customer'}), 403
