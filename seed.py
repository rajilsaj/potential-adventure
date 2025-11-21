from app import create_app
from app.extensions import db, bcrypt
from app.models import User, Customer, Room, Reservation
from datetime import date, timedelta
import random

app = create_app()

def seed_data():
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        
        print("Creating all tables...")
        db.create_all()
        
        print("Seeding data...")
        
        # Create Admin User
        hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin = User(username='admin', password_hash=hashed_pw, role='ADMIN')
        db.session.add(admin)
        db.session.commit()
        print("✓ Created admin user (admin/admin123)")
        
        # Create Staff User
        staff_pw = bcrypt.generate_password_hash('staff123').decode('utf-8')
        staff = User(username='staff', password_hash=staff_pw, role='STAFF')
        db.session.add(staff)
        db.session.commit()
        print("✓ Created staff user (staff/staff123)")
        
        # Create Sample Customers
        customer_pw = bcrypt.generate_password_hash('customer123').decode('utf-8')
        customers = [
            Customer(email='john@example.com', password_hash=customer_pw, full_name='John Doe', phone='+1234567890'),
            Customer(email='jane@example.com', password_hash=customer_pw, full_name='Jane Smith', phone='+1234567891'),
            Customer(email='bob@example.com', password_hash=customer_pw, full_name='Bob Johnson', phone='+1234567892'),
        ]
        for customer in customers:
            db.session.add(customer)
        db.session.commit()
        print(f"✓ Created {len(customers)} sample customers (password: customer123)")
        
        # Create 120 Rooms across 12 floors
        room_types = ['SINGLE', 'DOUBLE', 'SUITE']
        room_prices = {
            'SINGLE': (100, 150),
            'DOUBLE': (150, 250),
            'SUITE': (300, 500)
        }
        room_capacities = {
            'SINGLE': 1,
            'DOUBLE': 2,
            'SUITE': 4
        }
        
        rooms_created = 0
        for floor in range(1, 13):  # Floors 1-12
            for room_num in range(1, 11):  # 10 rooms per floor
                room_number = f"{floor}{room_num:02d}"  # e.g., 101, 102, ..., 1210
                
                # Vary room types
                if room_num <= 6:
                    room_type = 'SINGLE'
                elif room_num <= 9:
                    room_type = 'DOUBLE'
                else:
                    room_type = 'SUITE'
                
                # Random price within range
                price_range = room_prices[room_type]
                base_price = random.randint(price_range[0], price_range[1])
                
                # Some rooms out of service
                status = 'OUT_OF_SERVICE' if random.random() < 0.05 else 'AVAILABLE'
                
                room = Room(
                    room_number=room_number,
                    floor=floor,
                    room_type=room_type,
                    capacity=room_capacities[room_type],
                    base_price=base_price,
                    status=status
                )
                db.session.add(room)
                rooms_created += 1
        
        db.session.commit()
        print(f"✓ Created {rooms_created} rooms")
        
        # Create Sample Reservations
        rooms = Room.query.filter_by(status='AVAILABLE').limit(20).all()
        
        guest_names = [
            'John Doe', 'Jane Smith', 'Maria Garcia', 'Ahmed Khan', 'Li Wei',
            'Sarah Johnson', 'Michael Brown', 'Emily Davis', 'David Wilson', 'Anna Martinez'
        ]
        
        statuses = ['PENDING', 'BOOKED', 'CHECKED_IN', 'CHECKED_OUT', 'CANCELLED']
        
        for i, room in enumerate(rooms[:10]):
            guest_name = random.choice(guest_names)
            guest_email = f"{guest_name.lower().replace(' ', '.')}@example.com"
            
            # Random dates
            days_ahead = random.randint(1, 60)
            check_in = date.today() + timedelta(days=days_ahead)
            nights = random.randint(1, 7)
            check_out = check_in + timedelta(days=nights)
            
            total = float(room.base_price) * nights
            status = random.choice(statuses)
            
            reservation = Reservation(
                room_id=room.id,
                created_by=admin.id if i % 2 == 0 else staff.id,
                guest_name=guest_name,
                guest_email=guest_email,
                check_in_date=check_in,
                check_out_date=check_out,
                status=status,
                total_amount=total
            )
            db.session.add(reservation)
        
        db.session.commit()
        print("✓ Created 10 sample reservations")
        
        print("\n✅ Seeding completed successfully!")
        print(f"   - Users: 2 (admin, staff)")
        print(f"   - Rooms: {rooms_created}")
        print(f"   - Reservations: 10")

if __name__ == "__main__":
    seed_data()
