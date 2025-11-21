import pytest
from app import create_app
from app.extensions import db
from app.models import User, Room, Customer, Reservation
from datetime import date

@pytest.fixture
def app():
    # Configure app for testing with in-memory SQLite
    class TestConfig:
        TESTING = True
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SECRET_KEY = 'test-key'
        WTF_CSRF_ENABLED = False

    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def admin_user(app):
    user = User(username='admin', password_hash='hash', role='ADMIN')
    db.session.add(user)
    db.session.commit()
    return user

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Hotel Reservation System' in response.data

def test_create_room_requires_admin(client):
    response = client.post('/api/rooms', json={
        'room_number': '101',
        'floor': 1,
        'room_type': 'SINGLE',
        'capacity': 1,
        'base_price': 100.0
    })
    # Should fail without login
    assert response.status_code == 401

def test_create_room_admin(client, admin_user):
    # Mock login (using Flask-Login's test_client helper or just manual session if needed, 
    # but since we use an API login endpoint, let's use that)
    
    # First we need to actually hash the password to login properly or mock login_user.
    # Let's use the login endpoint.
    from app.extensions import bcrypt
    hashed = bcrypt.generate_password_hash('password').decode('utf-8')
    admin_user.password_hash = hashed
    db.session.commit()

    login_resp = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'password'
    })
    assert login_resp.status_code == 200

    # Now create room
    response = client.post('/api/rooms', json={
        'room_number': '101',
        'floor': 1,
        'room_type': 'SINGLE',
        'capacity': 1,
        'base_price': 100.0
    })
    assert response.status_code == 201
    assert Room.query.count() == 1

def test_create_reservation(client, app):
    # Setup data
    with app.app_context():
        room = Room(room_number='101', floor=1, room_type='SINGLE', capacity=1, base_price=100.0)
        db.session.add(room)
        db.session.commit()
        room_id = room.id

    # Create reservation
    data = {
        'guest_name': 'Test Guest',
        'guest_email': 'test@example.com',
        'room_id': room_id,
        'check_in_date': '2025-01-01',
        'check_out_date': '2025-01-03'
    }
    
    response = client.post('/api/reservations', json=data)
    assert response.status_code == 201
    
    with app.app_context():
        res = Reservation.query.first()
        assert res.guest_name == 'Test Guest'
        assert res.total_amount == 200.0 # 2 days * 100
