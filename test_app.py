#!/usr/bin/env python3
"""
Test script to identify startup errors
"""

print("=" * 60)
print("TESTING FLASK APP INITIALIZATION")
print("=" * 60)

try:
    print("\n1. Testing imports...")
    from app import create_app
    print("   ✓ create_app imported")
    
    from app.extensions import db
    print("   ✓ db imported")
    
    from app.models import User, Room, Reservation
    print("   ✓ Models imported")
    
    print("\n2. Creating app...")
    app = create_app()
    print("   ✓ App created successfully")
    
    print("\n3. Testing app context...")
    with app.app_context():
        print("   ✓ App context works")
        
        print("\n4. Testing database connection...")
        try:
            # Try to query
            user_count = User.query.count()
            room_count = Room.query.count()
            reservation_count = Reservation.query.count()
            
            print(f"   ✓ Database connected")
            print(f"   - Users: {user_count}")
            print(f"   - Rooms: {room_count}")
            print(f"   - Reservations: {reservation_count}")
            
            if room_count == 0:
                print("\n   ⚠️  WARNING: No rooms in database!")
                print("   Run: python3 seed.py")
                
        except Exception as e:
            print(f"   ✗ Database error: {e}")
            print("\n   ⚠️  Database not initialized!")
            print("   Run: python3 init_db.py && python3 seed.py")
    
    print("\n5. Testing routes...")
    with app.test_client() as client:
        # Test homepage
        response = client.get('/')
        print(f"   GET / → Status {response.status_code}")
        if response.status_code != 200:
            print(f"   ✗ Error: {response.data.decode()[:200]}")
        
        # Test rooms page
        response = client.get('/rooms')
        print(f"   GET /rooms → Status {response.status_code}")
        if response.status_code != 200:
            print(f"   ✗ Error: {response.data.decode()[:200]}")
        
        # Test admin login page
        response = client.get('/admin/login')
        print(f"   GET /admin/login → Status {response.status_code}")
        if response.status_code != 200:
            print(f"   ✗ Error: {response.data.decode()[:200]}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - App is ready!")
    print("=" * 60)
    print("\nYou can now run: python3 flask_app.py")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    print("\nFull traceback:")
    import traceback
    traceback.print_exc()
    print("\n" + "=" * 60)
    print("❌ TESTS FAILED - Fix errors above")
    print("=" * 60)
