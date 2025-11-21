"""
Database Migration Script for OOAD Test Cases
Adds BaseRate table and extends Reservation table
Run this ONCE after updating models.py
"""

from app import create_app
from app.extensions import db
from app.models import BaseRate, Reservation, Room
from datetime import date, timedelta
from decimal import Decimal

app = create_app()

def migrate_database():
    with app.app_context():
        print("=" * 60)
        print("DATABASE MIGRATION FOR OOAD TEST CASES")
        print("=" * 60)
        
        # Create all new tables and columns
        print("\n1. Creating new tables and columns...")
        db.create_all()
        print("   ✓ Tables created/updated")
        
        # Add default base rates
        print("\n2. Adding default base rates...")
        add_default_base_rates()
        
        # Migrate existing reservations
        print("\n3. Migrating existing reservations...")
        migrate_existing_reservations()
        
        print("\n" + "=" * 60)
        print("MIGRATION COMPLETE!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Restart your Flask app")
        print("2. Test the new features")
        print("3. Run seed_ooad.py to add test data")

def add_default_base_rates():
    """Add base rates for the next 365 days"""
    # Check if rates already exist
    existing_count = BaseRate.query.count()
    if existing_count > 0:
        print(f"   ℹ Base rates already exist ({existing_count} rates)")
        return
    
    # Add rates for next year
    start_date = date.today()
    rates_added = 0
    
    for i in range(365):
        current_date = start_date + timedelta(days=i)
        
        # Vary rates by day of week (higher on weekends)
        base_rate = 100.00
        if current_date.weekday() >= 5:  # Saturday or Sunday
            base_rate = 150.00
        
        # Holiday rates (example: Christmas, New Year)
        if current_date.month == 12 and current_date.day >= 20:
            base_rate = 200.00
        
        rate = BaseRate(
            effective_date=current_date,
            rate_amount=Decimal(str(base_rate))
        )
        db.session.add(rate)
        rates_added += 1
        
        if rates_added % 50 == 0:
            db.session.commit()
            print(f"   Added {rates_added} rates...")
    
    db.session.commit()
    print(f"   ✓ Added {rates_added} base rates")

def migrate_existing_reservations():
    """Update existing reservations with new OOAD fields"""
    reservations = Reservation.query.all()
    
    if not reservations:
        print("   ℹ No existing reservations to migrate")
        return
    
    updated = 0
    for reservation in reservations:
        # Set arrival_date from check_in_date
        if not reservation.arrival_date:
            reservation.arrival_date = reservation.check_in_date
        
        # Calculate number_of_days
        if not reservation.number_of_days and reservation.check_in_date and reservation.check_out_date:
            delta = reservation.check_out_date - reservation.check_in_date
            reservation.number_of_days = delta.days
        
        # Set default reservation_type
        if not reservation.reservation_type:
            reservation.reservation_type = 'C'  # Conventional
        
        # Set reservation_status from legacy status
        if not reservation.reservation_status:
            status_map = {
                'PENDING': 'P',
                'BOOKED': 'C',
                'CHECKED_IN': 'I',
                'CHECKED_OUT': 'O',
                'CANCELLED': 'X'
            }
            reservation.reservation_status = status_map.get(reservation.status, 'P')
        
        # Calculate total_amount if not set
        if not reservation.total_amount:
            reservation.total_amount = Decimal(str(reservation.calculate_total_amount()))
        
        # Set default amount_bill_paid
        if reservation.amount_bill_paid is None:
            reservation.amount_bill_paid = Decimal('0.00')
        
        updated += 1
    
    db.session.commit()
    print(f"   ✓ Updated {updated} existing reservations")

if __name__ == '__main__':
    migrate_database()
