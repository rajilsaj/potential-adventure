#!/usr/bin/env python3
"""
Initialize the database for the Hotel Reservation System.
Run this script once before starting the application.
"""

from app import create_app
from app.extensions import db

def init_db():
    """Create all database tables"""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully!")
        print(f"✓ Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print("\nYou can now run: python flask_app.py")

if __name__ == "__main__":
    init_db()
