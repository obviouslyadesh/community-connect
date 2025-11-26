from app import create_app, db
from app.models import User, Event
from datetime import datetime, timedelta
import os
from sqlalchemy import text  # Add this import

def initialize_production():
    app = create_app()
    
    with app.app_context():
        print("🚀 Production Database Initialization Starting...")
        
        try:
            # Test database connection - FIXED
            db.session.execute(text('SELECT 1'))
            print("✅ Database connection successful")
            
            # Create all tables
            db.create_all()
            print("✅ Database tables created/verified")
            
            # Create essential users if they don't exist
            users_created = 0
            
            # Admin User
            if not User.query.filter_by(username='admin').first():
                admin = User(
                    username='admin',
                    email='admin@community.com',
                    user_type='organization',
                    is_admin=True
                )
                admin.set_password('Admin123!')
                db.session.add(admin)
                users_created += 1
                print("✅ Created admin: admin / Admin123!")
            
            # Organization User
            if not User.query.filter_by(username='organization').first():
                org = User(
                    username='organization',
                    email='org@community.com',
                    user_type='organization',
                    is_admin=False
                )
                org.set_password('Org123!')
                db.session.add(org)
                users_created += 1
                print("✅ Created organization: organization / Org123!")
            
            # Volunteer User
            if not User.query.filter_by(username='volunteer').first():
                volunteer = User(
                    username='volunteer',
                    email='volunteer@community.com',
                    user_type='volunteer'
                )
                volunteer.set_password('Volunteer123!')
                db.session.add(volunteer)
                users_created += 1
                print("✅ Created volunteer: volunteer / Volunteer123!")
            
            db.session.commit()
            
            # Final report
            total_users = User.query.count()
            total_events = Event.query.count()
            
            print(f"\n🎉 Production Initialization Complete!")
            print(f"📊 Database Status:")
            print(f"   👥 Total Users: {total_users}")
            print(f"   📅 Total Events: {total_events}")
            print(f"   ✅ Users Created: {users_created}")
            
            print(f"\n🔑 Login Credentials:")
            print("   Admin: admin / Admin123!")
            print("   Organization: organization / Org123!") 
            print("   Volunteer: volunteer / Volunteer123!")
            
        except Exception as e:
            print(f"❌ Initialization error: {e}")
            print("⚠️  Continuing with application startup...")

if __name__ == '__main__':
    initialize_production()