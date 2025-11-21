from flask import Blueprint, render_template

frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/')
def index():
    return render_template('index.html')

@frontend_bp.route('/admin/login')
def admin_login():
    return render_template('admin_login.html')

@frontend_bp.route('/admin/dashboard')
def dashboard():
    return render_template('dashboard.html')

@frontend_bp.route('/admin/rooms')
def manage_rooms():
    return render_template('manage_rooms.html')

@frontend_bp.route('/admin/reservations')
def manage_reservations():
    return render_template('manage_reservations.html')

@frontend_bp.route('/my-bookings')
def my_bookings():
    return render_template('my_bookings.html')
