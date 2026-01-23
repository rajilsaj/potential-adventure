#!/usr/bin/env python3
"""
Quick fix script - Run this to fix common issues
"""

from app import create_app
from app.extensions import db
from app.models import User, Room, Reservation
from datetime import date, timedelta
import random

app = create_app()

def quick_fix():
    with app.app_context():
        print("Checking database...")
        
        # Check if tables exist
        try:
            user_count = User.query.count()
            room_count = Room.query.count()
            print(f"✓ Database exists: {user_count} users, {room_count} rooms")
            
            if room_count == 0:
                print("\n⚠️  No rooms found. Creating sample rooms...")
                create_sample_rooms()
                
            if user_count == 0:
                print("\n⚠️  No users found. Creating admin user...")
                create_admin_user()
                
        except Exception as e:
            print(f"✗ Database error: {e}")
            print("\nCreating database tables...")
            db.create_all()
            print("✓ Tables created")
            
            print("\nCreating admin user...")
            create_admin_user()
            
            print("\nCreating sample rooms...")
            create_sample_rooms()
        
        print("\n✅ Database is ready!")

def create_admin_user():
    from app.extensions import bcrypt
    
    hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
    admin = User(username='admin', password_hash=hashed_pw, role='ADMIN')
    db.session.add(admin)
    db.session.commit()
    print("✓ Created admin user (admin/admin123)")

def create_sample_rooms():
    # Create 20 sample rooms
    room_types = ['SINGLE', 'DOUBLE', 'SUITE']
    
    for i in range(1, 21):
        room_type = room_types[i % 3]
        capacity = {'SINGLE': 1, 'DOUBLE': 2, 'SUITE': 4}[room_type]
        base_price = {'SINGLE': 100, 'DOUBLE': 150, 'SUITE': 300}[room_type]
        
        room = Room(
            room_number=f"{i:03d}",
            floor=(i // 10) + 1,
            room_type=room_type,
            capacity=capacity,
            base_price=base_price + random.randint(0, 50),
            status='AVAILABLE'
        )
        db.session.add(room)
    
    db.session.commit()
    print(f"✓ Created 20 sample rooms")

if __name__ == "__main__":
    quick_fix()
