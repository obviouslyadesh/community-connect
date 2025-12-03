import os
import sys

# THIS LINE ADDS THE CURRENT DIRECTORY TO PYTHON'S IMPORT PATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User

print("🚀 Starting fresh database setup...")

# Create app
app = create_app()

with app.app_context():
    # Drop all tables (if any)
    db.drop_all()
    
    # Create all tables
    db.create_all()
    print("✅ Database tables created")
    
    # Create admin user
    admin = User(
        username='admin',
        email='admin@example.com',
        user_type='volunteer',
        is_admin=True
    )
    admin.set_password('admin123')
    
    # Create sample users
    org = User(
        username='sample_org',
        email='org@example.com',
        user_type='organization'
    )
    org.set_password('password123')
    
    volunteer = User(
        username='sample_volunteer',
        email='volunteer@example.com',
        user_type='volunteer'
    )
    volunteer.set_password('password123')
    
    db.session.add(admin)
    db.session.add(org)
    db.session.add(volunteer)
    
    try:
        db.session.commit()
        print("✅ Sample users created:")
        print("   Admin: admin / admin123")
        print("   Organization: sample_org / password123")
        print("   Volunteer: sample_volunteer / password123")
    except Exception as e:
        db.session.rollback()
        print(f"⚠️  Note: {e}")

print("🎉 Fresh setup complete!")