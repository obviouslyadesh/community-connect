#!/usr/bin/env python3
"""
Script to initialize production database with sample data
"""

from app import create_app, db
from app.models import User, Event, EventVolunteer
from datetime import datetime, timedelta

def init_production_data():
    app = create_app()
    
    with app.app_context():
        print("🚀 Initializing production database...")
        
        # Check if users already exist
        if User.query.count() == 0:
            print("👥 Creating sample users...")
            
            # Admin organization
            org = User(
                username='sample_org',
                email='org@example.com', 
                user_type='organization',
                is_admin=True
            )
            org.set_password('password123')
            db.session.add(org)
            
            # Volunteer
            volunteer = User(
                username='sample_volunteer',
                email='volunteer@example.com',
                user_type='volunteer'
            )
            volunteer.set_password('password123')
            db.session.add(volunteer)
            
            db.session.commit()
            print("✅ Sample users created")
            
            # Create sample events
            print("📅 Creating sample events...")
            
            event1 = Event(
                title="Community Park Cleanup",
                description="Join us for a community park cleanup day! We'll be picking up trash, planting flowers, and making our park beautiful.",
                date=datetime.utcnow() + timedelta(days=7),
                address="123 Main Street",
                city="Springfield",
                state="IL", 
                zip_code="62701",
                max_volunteers=15,
                organizer_id=1
            )
            db.session.add(event1)
            
            event2 = Event(
                title="Food Bank Volunteer Day", 
                description="Help sort and package food donations for local families in need. No experience necessary!",
                date=datetime.utcnow() + timedelta(days=14),
                address="456 Oak Avenue",
                city="Springfield",
                state="IL",
                zip_code="62702", 
                max_volunteers=10,
                organizer_id=1
            )
            db.session.add(event2)
            
            db.session.commit()
            print("✅ Sample events created")
            
        else:
            print("ℹ️  Database already has data, skipping sample data creation")
        
        # Show final counts
        users = User.query.count()
        events = Event.query.count()
        print(f"\n📊 Production Database Ready:")
        print(f"   👥 Users: {users}")
        print(f"   📅 Events: {events}")
        print(f"\n🔑 Demo Accounts:")
        print(f"   Admin: sample_org / password123")
        print(f"   Volunteer: sample_volunteer / password123")

if __name__ == '__main__':
    init_production_data()