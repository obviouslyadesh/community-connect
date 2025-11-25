# from app import create_app, db
# from app.models import User, Event, EventVolunteer
# from datetime import datetime, timedelta

# def reset_database():
#     app = create_app()
    
#     with app.app_context():
#         print("🗑️  Resetting database...")
        
#         # Drop all tables and recreate
#         db.drop_all()
#         db.create_all()
        
#         print("✅ Database tables created")
        
#         # Create demo users
#         print("👥 Creating demo users...")
        
#         # Organization user
#         org = User(
#             username='sample_org', 
#             email='org@example.com', 
#             user_type='organization'
#         )
#         org.set_password('password123')
#         db.session.add(org)
        
#         # Volunteer user  
#         volunteer = User(
#             username='sample_volunteer',
#             email='volunteer@example.com',
#             user_type='volunteer'
#         )
#         volunteer.set_password('password123')
#         db.session.add(volunteer)
        
#         # Create some sample events
#         print("📅 Creating sample events...")
        
#         event1 = Event(
#             title="Community Park Cleanup",
#             description="Join us for a community park cleanup day! We'll be picking up trash, planting flowers, and making our park beautiful. Gloves and bags provided.",
#             date=datetime.utcnow() + timedelta(days=7),
#             address="123 Main Street",
#             city="Springfield",
#             state="IL",
#             zip_code="62701",
#             max_volunteers=15,
#             organizer_id=1  # sample_org will have ID 1
#         )
#         db.session.add(event1)
        
#         event2 = Event(
#             title="Food Bank Volunteer Day",
#             description="Help sort and package food donations for local families in need. No experience necessary - training provided!",
#             date=datetime.utcnow() + timedelta(days=14),
#             address="456 Oak Avenue",
#             city="Springfield", 
#             state="IL",
#             zip_code="62702",
#             max_volunteers=10,
#             organizer_id=1
#         )
#         db.session.add(event2)
        
#         event3 = Event(
#             title="Animal Shelter Assistance",
#             description="Help walk dogs, socialize cats, and clean kennels at our local animal shelter. Perfect for animal lovers!",
#             date=datetime.utcnow() + timedelta(days=3),
#             address="789 Pet Lane",
#             city="Springfield",
#             state="IL", 
#             zip_code="62703",
#             max_volunteers=8,
#             organizer_id=1
#         )
#         db.session.add(event3)
        
#         # Commit everything
#         db.session.commit()
        
#         print("✅ Demo data created successfully!")
        
#         # Show what we created
#         users = User.query.all()
#         events = Event.query.all()
        
#         print(f"\n📊 Database Summary:")
#         print(f"👥 Users: {len(users)}")
#         for user in users:
#             print(f"   - {user.username} ({user.user_type})")
        
#         print(f"📅 Events: {len(events)}")
#         for event in events:
#             print(f"   - {event.title} (by {event.organizer.username})")
#             print(f"     📍 {event.city}, {event.state} - 🗓️  {event.date.strftime('%b %d, %Y')}")
        
#         print(f"\n🔑 Demo Login Credentials:")
#         print("   Organization: sample_org / password123")
#         print("   Volunteer: sample_volunteer / password123")
#         print("\n🚀 You can now run: python run.py")

# if __name__ == '__main__':
#     reset_database()