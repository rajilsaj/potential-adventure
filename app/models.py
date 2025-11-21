from datetime import datetime, date
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

class BaseRate(db.Model):
    """Base rates for pricing by date"""
    __tablename__ = 'base_rates'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    effective_date = db.Column(db.Date, unique=True, nullable=False, index=True)
    rate_amount = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def get_rate_for_date(target_date):
        """Get base rate for a specific date, fallback to previous rate or default"""
        # Try exact match first
        rate = BaseRate.query.filter_by(effective_date=target_date).first()
        if rate:
            return float(rate.rate_amount)
        
        # Try most recent rate before this date
        rate = BaseRate.query.filter(BaseRate.effective_date < target_date)\
            .order_by(BaseRate.effective_date.desc()).first()
        if rate:
            return float(rate.rate_amount)
        
        # Default fallback rate
        return 100.00

class Reservation(db.Model):
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Room and User relationships
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL', onupdate='CASCADE'), nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='SET NULL', onupdate='CASCADE'), nullable=True)
    
    # Guest Information (OOAD Extended)
    guest_name = db.Column(db.String(100), nullable=False)
    guest_email = db.Column(db.String(120), nullable=False)
    guest_phone = db.Column(db.String(20), nullable=True)
    guest_address = db.Column(db.String(255), nullable=True)
    comments = db.Column(db.Text, nullable=True)
    
    # Dates (keeping both old and new for compatibility)
    check_in_date = db.Column(db.Date, nullable=False)  # Kept for backward compatibility
    check_out_date = db.Column(db.Date, nullable=False)  # Kept for backward compatibility
    arrival_date = db.Column(db.Date, nullable=False)  # OOAD: same as check_in_date
    number_of_days = db.Column(db.Integer, nullable=False)  # OOAD: calculated from dates
    
    # Reservation Type (OOAD)
    # D = 60-Days-in-Advance
    # C = Conventional
    # I = Incentive
    # P = Prepaid
    reservation_type = db.Column(db.String(1), nullable=False, default='C')
    
    # Status (OOAD Extended)
    # P = Pending
    # C = Confirmed
    # I = Checked-In
    # O = Checked-Out
    # X = Canceled
    # N = No-Show
    reservation_status = db.Column(db.String(1), nullable=False, default='P')
    
    # Legacy status field (kept for compatibility)
    status = db.Column(db.Enum('PENDING', 'BOOKED', 'CHECKED_IN', 'CHECKED_OUT', 'CANCELLED'), nullable=False, default='PENDING')
    
    # Billing & Payment (OOAD)
    total_amount = db.Column(db.Numeric(10, 2), nullable=True)
    amount_bill_paid = db.Column(db.Numeric(10, 2), default=0.00)
    bill_paid_date = db.Column(db.Date, nullable=True)
    
    # Credit Card Information (OOAD)
    credit_card_number = db.Column(db.String(20), nullable=True)  # Last 4 digits only for security
    credit_card_expiry = db.Column(db.String(7), nullable=True)  # MM/YYYY
    credit_card_type = db.Column(db.String(20), nullable=True)  # Visa, MasterCard, Amex, etc.
    
    # Flags (OOAD)
    no_show_flag = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def calculate_total_amount(self):
        """Calculate total amount based on base rates and reservation type"""
        if not self.arrival_date or not self.number_of_days:
            return 0.00
        
        total = 0.00
        current_date = self.arrival_date
        
        for day in range(self.number_of_days):
            daily_rate = BaseRate.get_rate_for_date(current_date)
            
            # Apply discount for Incentive reservations
            if self.reservation_type == 'I':
                daily_rate *= 0.80  # 20% discount
            
            total += daily_rate
            current_date = date.fromordinal(current_date.toordinal() + 1)
        
        return round(total, 2)
    
    def calculate_cancellation_charge(self):
        """Calculate cancellation charge based on reservation type and timing"""
        if not self.arrival_date:
            return 0.00
        
        days_until_arrival = (self.arrival_date - date.today()).days
        
        # Prepaid: full amount
        if self.reservation_type == 'P':
            return float(self.total_amount or 0.00)
        
        # 60-Days: full amount if canceled within 30 days or if has credit card
        if self.reservation_type == 'D':
            if days_until_arrival < 30:
                return float(self.total_amount or 0.00)
            elif self.credit_card_number:
                return float(self.total_amount or 0.00)
            else:
                return 0.00
        
        # Conventional and Incentive: first day's charge
        if self.reservation_type in ['C', 'I']:
            first_day_rate = BaseRate.get_rate_for_date(self.arrival_date)
            if self.reservation_type == 'I':
                first_day_rate *= 0.80  # 20% discount
            return round(first_day_rate, 2)
        
        return 0.00
    
    def sync_dates(self):
        """Sync arrival_date with check_in_date and calculate number_of_days"""
        if self.check_in_date and self.check_out_date:
            self.arrival_date = self.check_in_date
            delta = self.check_out_date - self.check_in_date
            self.number_of_days = delta.days
    
    def sync_status(self):
        """Sync reservation_status with legacy status field"""
        status_map = {
            'P': 'PENDING',
            'C': 'BOOKED',
            'I': 'CHECKED_IN',
            'O': 'CHECKED_OUT',
            'X': 'CANCELLED',
            'N': 'CANCELLED'
        }
        if self.reservation_status in status_map:
            self.status = status_map[self.reservation_status]
