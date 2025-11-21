"""
Admin Tools Routes for OOAD Test Cases
Handles: Check-in, Check-out, Availability, Assessment, Verify User
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Reservation, Room, Customer, BaseRate
from app.extensions import db
from datetime import date, timedelta
from sqlalchemy import and_, or_

admin_tools_bp = Blueprint('admin_tools', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin/staff role"""
    from functools import wraps
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        try:
            if not hasattr(current_user, 'role') or current_user.role not in ['ADMIN', 'STAFF']:
                flash('Access denied. Admin privileges required.', 'error')
                return redirect(url_for('frontend.index'))
        except:
            flash('Please login as admin/staff.', 'error')
            return redirect(url_for('frontend.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ============================================================================
# CHECK-IN GUEST
# ============================================================================

@admin_tools_bp.route('/checkin', methods=['GET', 'POST'])
@admin_required
def checkin():
    """Check-in a guest"""
    if request.method == 'POST':
        reservation_id = request.form.get('reservation_id')
        
        if not reservation_id:
            flash('Please enter a reservation ID', 'error')
            return render_template('admin_checkin.html')
        
        reservation = Reservation.query.get(reservation_id)
        
        if not reservation:
            flash(f'Reservation #{reservation_id} not found', 'error')
            return render_template('admin_checkin.html')
        
        # Validate status
        if reservation.reservation_status != 'C':
            status_names = {'P': 'Pending', 'I': 'Already Checked-In', 'O': 'Checked-Out', 'X': 'Canceled', 'N': 'No-Show'}
            flash(f'Cannot check-in: Reservation is {status_names.get(reservation.reservation_status, "in invalid status")}', 'error')
            return render_template('admin_checkin.html', reservation=reservation)
        
        # Check-in the guest
        reservation.reservation_status = 'I'
        reservation.sync_status()
        db.session.commit()
        
        flash(f'Guest {reservation.guest_name} successfully checked in to Room {reservation.room.room_number}', 'success')
        return render_template('admin_checkin.html', reservation=reservation, success=True)
    
    return render_template('admin_checkin.html')

# ============================================================================
# CHECK-OUT GUEST
# ============================================================================

@admin_tools_bp.route('/checkout', methods=['GET', 'POST'])
@admin_required
def checkout():
    """Check-out a guest and generate bill"""
    if request.method == 'POST':
        reservation_id = request.form.get('reservation_id')
        
        if not reservation_id:
            flash('Please enter a reservation ID', 'error')
            return render_template('admin_checkout.html')
        
        reservation = Reservation.query.get(reservation_id)
        
        if not reservation:
            flash(f'Reservation #{reservation_id} not found', 'error')
            return render_template('admin_checkout.html')
        
        # Validate status
        if reservation.reservation_status != 'I':
            status_names = {'P': 'Pending', 'C': 'Confirmed (not checked-in)', 'O': 'Already Checked-Out', 'X': 'Canceled', 'N': 'No-Show'}
            flash(f'Cannot check-out: Reservation is {status_names.get(reservation.reservation_status, "in invalid status")}', 'error')
            return render_template('admin_checkout.html', reservation=reservation)
        
        # Check-out the guest
        reservation.reservation_status = 'O'
        reservation.sync_status()
        db.session.commit()
        
        # Redirect to bill
        return redirect(url_for('reports.accommodation_bill', reservation_id=reservation.id))
    
    return render_template('admin_checkout.html')

# ============================================================================
# ROOM AVAILABILITY
# ============================================================================

@admin_tools_bp.route('/availability', methods=['GET', 'POST'])
@admin_required
def availability():
    """Check room availability for a date range"""
    if request.method == 'POST':
        try:
            arrival_date_str = request.form.get('arrival_date')
            number_of_days = int(request.form.get('number_of_days', 1))
            
            if not arrival_date_str:
                flash('Please enter an arrival date', 'error')
                return render_template('admin_availability.html')
            
            arrival_date = date.fromisoformat(arrival_date_str)
            departure_date = arrival_date + timedelta(days=number_of_days)
            
            # Get total rooms
            total_rooms = Room.query.filter_by(status='AVAILABLE').count()
            
            # Find overlapping reservations
            overlapping = Reservation.query.filter(
                and_(
                    Reservation.reservation_status.in_(['C', 'I']),  # Confirmed or Checked-In
                    or_(
                        and_(
                            Reservation.arrival_date <= arrival_date,
                            Reservation.check_out_date > arrival_date
                        ),
                        and_(
                            Reservation.arrival_date < departure_date,
                            Reservation.check_out_date >= departure_date
                        ),
                        and_(
                            Reservation.arrival_date >= arrival_date,
                            Reservation.check_out_date <= departure_date
                        )
                    )
                )
            ).count()
            
            available_rooms = total_rooms - overlapping
            
            result = {
                'arrival_date': arrival_date,
                'departure_date': departure_date,
                'number_of_days': number_of_days,
                'total_rooms': total_rooms,
                'occupied_rooms': overlapping,
                'available_rooms': max(0, available_rooms)
            }
            
            return render_template('admin_availability.html', result=result)
            
        except ValueError as e:
            flash(f'Invalid input: {str(e)}', 'error')
            return render_template('admin_availability.html')
    
    return render_template('admin_availability.html')

# ============================================================================
# DAILY ASSESSMENT (No-Shows & Auto-Cancel)
# ============================================================================

@admin_tools_bp.route('/assessment', methods=['GET', 'POST'])
@admin_required
def assessment():
    """Run daily assessment: mark no-shows and auto-cancel 60-Days reservations"""
    if request.method == 'POST':
        results = {
            'no_shows': [],
            'auto_canceled': [],
            'errors': []
        }
        
        # 1. Mark No-Shows (arrivals from yesterday that didn't check in)
        yesterday = date.today() - timedelta(days=1)
        no_show_candidates = Reservation.query.filter(
            and_(
                Reservation.arrival_date == yesterday,
                Reservation.reservation_status == 'C'  # Still confirmed, never checked in
            )
        ).all()
        
        for reservation in no_show_candidates:
            try:
                reservation.reservation_status = 'N'
                reservation.no_show_flag = True
                
                # Calculate and apply cancellation charge
                charge = reservation.calculate_cancellation_charge()
                reservation.amount_bill_paid = charge
                reservation.bill_paid_date = date.today()
                
                reservation.sync_status()
                
                results['no_shows'].append({
                    'id': reservation.id,
                    'guest_name': reservation.guest_name,
                    'room': reservation.room.room_number,
                    'charge': float(charge)
                })
            except Exception as e:
                results['errors'].append(f"Error processing reservation #{reservation.id}: {str(e)}")
        
        # 2. Auto-Cancel 60-Days reservations (30 days before arrival, no payment)
        thirty_days_out = date.today() + timedelta(days=30)
        auto_cancel_candidates = Reservation.query.filter(
            and_(
                Reservation.reservation_type == 'D',  # 60-Days type
                Reservation.arrival_date == thirty_days_out,
                Reservation.reservation_status == 'C',  # Still confirmed
                or_(
                    Reservation.amount_bill_paid == 0,
                    Reservation.amount_bill_paid == None
                ),
                or_(
                    Reservation.credit_card_number == None,
                    Reservation.credit_card_number == ''
                )
            )
        ).all()
        
        for reservation in auto_cancel_candidates:
            try:
                reservation.reservation_status = 'X'
                reservation.sync_status()
                
                results['auto_canceled'].append({
                    'id': reservation.id,
                    'guest_name': reservation.guest_name,
                    'room': reservation.room.room_number,
                    'arrival_date': reservation.arrival_date.isoformat()
                })
            except Exception as e:
                results['errors'].append(f"Error canceling reservation #{reservation.id}: {str(e)}")
        
        # Commit all changes
        db.session.commit()
        
        return render_template('admin_assessment.html', results=results, completed=True)
    
    return render_template('admin_assessment.html')

# ============================================================================
# VERIFY USER
# ============================================================================

@admin_tools_bp.route('/verify-user', methods=['GET', 'POST'])
@admin_required
def verify_user():
    """Verify/search for a customer"""
    if request.method == 'POST':
        search_value = request.form.get('search_value', '').strip()
        
        if not search_value:
            flash('No value entered. Please enter a customer ID or email.', 'error')
            return render_template('admin_verify_user.html')
        
        # Try to find by ID first
        customer = None
        if search_value.isdigit():
            customer = Customer.query.get(int(search_value))
        
        # If not found by ID, try email
        if not customer:
            customer = Customer.query.filter_by(email=search_value).first()
        
        if not customer:
            flash(f'User not found: {search_value}', 'error')
            return render_template('admin_verify_user.html')
        
        # Get customer's reservations
        reservations = Reservation.query.filter_by(customer_id=customer.id).order_by(Reservation.created_at.desc()).all()
        
        return render_template('admin_verify_user.html', customer=customer, reservations=reservations, found=True)
    
    return render_template('admin_verify_user.html')
