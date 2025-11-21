from app import create_app
from app.extensions import db, bcrypt
from app.models import User, Room, Customer, Reservation
from datetime import date, timedelta

app = create_app()

def seed_data():
    with app.app_context():
        print("Seeding data...")
        
        # Create Admin
        if not User.query.filter_by(username='admin').first():
            hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = User(username='admin', password_hash=hashed_pw, role='ADMIN')
            db.session.add(admin)
            print("Created admin user (admin/admin123)")
        
        # Create Rooms
        rooms_data = [
            ('101', 1, 'SINGLE', 1, 100.00),
            ('102', 1, 'DOUBLE', 2, 150.00),
            ('103', 1, 'SUITE', 4, 300.00),
            ('201', 2, 'SINGLE', 1, 110.00),
            ('202', 2, 'DOUBLE', 2, 160.00),
            ('301', 3, 'SINGLE', 1, 120.00),
            ('302', 3, 'DOUBLE', 2, 170.00),
            ('303', 3, 'SUITE', 4, 320.00),
            ('401', 4, 'SINGLE', 1, 130.00),
            ('402', 4, 'DOUBLE', 2, 180.00),
        ]
        
        rooms_map = {} # room_number -> room object
        
        for r_num, floor, r_type, cap, price in rooms_data:
            if not Room.query.filter_by(room_number=r_num).first():
                room = Room(room_number=r_num, floor=floor, room_type=r_type, capacity=cap, base_price=price)
                db.session.add(room)
                rooms_map[r_num] = room
        
        db.session.commit()
        
        # Re-query rooms to get IDs
        rooms = Room.query.all()
        rooms_dict = {r.room_number: r for r in rooms}

        # Create Customers
        customers_data = [
            ('John Doe', 'john.doe@example.com', '555-0101'),
            ('Maria Santos', 'm.santos@example.com', '555-0102'),
            ('Ahmed Khan', 'ahmed.khan@example.com', '555-0103'),
            ('Linda Johnson', 'linda.j@example.com', '555-0104'),
            ('Emily Chen', 'e.chen@example.com', '555-0105'),
        ]
        
        customers_map = {}
        
        for name, email, phone in customers_data:
            cust = Customer.query.filter_by(email=email).first()
            if not cust:
                cust = Customer(full_name=name, email=email, phone=phone)
                db.session.add(cust)
            customers_map[email] = cust
            
        db.session.commit()
        
        # Refresh customers to get IDs
        for email in customers_map:
            customers_map[email] = Customer.query.filter_by(email=email).first()

        # Create Reservations (matching the SQL provided in Step 0 roughly)
        # (1, 101, 'John Doe', 'john.doe@example.com', '2025-01-10', '2025-01-12', 'BOOKED', 170.00)
        # Note: I'm using the room objects I created, so IDs might differ from SQL but logic holds.
        
        reservations_list = [
            ('john.doe@example.com', '101', '2025-01-10', '2025-01-12', 'BOOKED'),
            ('m.santos@example.com', '102', '2025-02-05', '2025-02-10', 'PENDING'),
            ('ahmed.khan@example.com', '103', '2025-03-01', '2025-03-03', 'CANCELLED'),
            ('linda.j@example.com', '201', '2025-04-15', '2025-04-18', 'BOOKED'),
            ('e.chen@example.com', '302', '2025-05-20', '2025-05-25', 'CHECKED_IN'),
        ]
        
        for email, r_num, start, end, status in reservations_list:
            cust = customers_map.get(email)
            room = rooms_dict.get(r_num)
            
            if cust and room:
                # Check if reservation already exists (simple check)
                exists = Reservation.query.filter_by(
                    customer_id=cust.id, 
                    room_id=room.id, 
                    check_in_date=start
                ).first()
                
                if not exists:
                    # Calculate total
                    d1 = date.fromisoformat(start)
                    d2 = date.fromisoformat(end)
                    days = (d2 - d1).days
                    total = days * float(room.base_price)
                    
                    res = Reservation(
                        customer_id=cust.id,
                        room_id=room.id,
                        guest_name=cust.full_name,
                        guest_email=cust.email,
                        check_in_date=d1,
                        check_out_date=d2,
                        status=status,
                        total_amount=total
                    )
                    db.session.add(res)
        
        db.session.commit()
        print("Seeding completed.")

if __name__ == "__main__":
    seed_data()
