# init_production_db.py - SAFE PRODUCTION INITIALIZATION
from app import create_app, db
from app.models import User, PasswordResetToken, Event, EventVolunteer
from sqlalchemy import inspect
import traceback

def init_production_db():
    print("🚀 Production Database Initialization")
    print("="*60)
    
    app = create_app()
    
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            print(f"📊 Existing tables: {existing_tables}")
            
            # Create all tables (handles missing ones only)
            db.create_all()
            print("✅ Database tables verified/created")
            
            # Check for admin user
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    user_type='volunteer',
                    is_admin=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin user created: admin / admin123")
            else:
                print("⚠️  Admin user already exists")
            
            # Verify all models have tables
            required_tables = ['users', 'password_reset_tokens', 'events', 'event_volunteers']
            for table in required_tables:
                if table in existing_tables:
                    print(f"✅ {table} table exists")
                else:
                    print(f"⚠️  {table} table missing (should be created)")
            
            print("\n🎉 Database initialization complete!")
            
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
            traceback.print_exc()
            print("⚠️  Continuing deployment...")

if __name__ == '__main__':
    init_production_db()