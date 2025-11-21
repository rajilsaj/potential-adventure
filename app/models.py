from datetime import datetime
from app.extensions import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID - checks both User (admin/staff) and Customer tables"""
    # Try to load as admin/staff user first
    if user_id.startswith('user_'):
        actual_id = int(user_id.replace('user_', ''))
        return User.query.get(actual_id)
    # Otherwise load as customer
    elif user_id.startswith('customer_'):
        actual_id = int(user_id.replace('customer_', ''))
        return Customer.query.get(actual_id)
    # Fallback for old sessions
    user = User.query.get(int(user_id))
    if user:
        return user
    return Customer.query.get(int(user_id))

class User(db.Model, UserMixin):
    """Admin and Staff users"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('ADMIN', 'STAFF'), nullable=False, default='ADMIN')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to reservations created by this user
    created_reservations = db.relationship('Reservation', backref='creator', lazy=True, foreign_keys='Reservation.created_by')

    def get_id(self):
        return f'user_{self.id}'

class Customer(db.Model, UserMixin):
    """Customer accounts for booking"""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to reservations made by this customer
    reservations = db.relationship('Reservation', backref='customer', lazy=True, foreign_keys='Reservation.customer_id')
    
    def get_id(self):
        return f'customer_{self.id}'
    
    @property
    def username(self):
        """For compatibility with templates that expect username"""
        return self.email

class Room(db.Model):
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_number = db.Column(db.String(20), unique=True, nullable=False)
    floor = db.Column(db.Integer, nullable=True)
    room_type = db.Column(db.Enum('SINGLE', 'DOUBLE', 'SUITE'), nullable=False, default='SINGLE')
    capacity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum('AVAILABLE', 'OUT_OF_SERVICE'), nullable=False, default='AVAILABLE')
    base_price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to reservations
    reservations = db.relationship('Reservation', backref='room', lazy=True)

class Reservation(db.Model):
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL', onupdate='CASCADE'), nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='SET NULL', onupdate='CASCADE'), nullable=True)
    guest_name = db.Column(db.String(100), nullable=False)
    guest_email = db.Column(db.String(120), nullable=False)
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('PENDING', 'BOOKED', 'CHECKED_IN', 'CHECKED_OUT', 'CANCELLED'), nullable=False, default='PENDING')
    total_amount = db.Column(db.Numeric(10, 2), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
