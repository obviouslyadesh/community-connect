# init_production_db.py - UPDATED VERSION
from app import create_app, db
from app.models import User
from sqlalchemy import inspect

def init_production_db():
    print("🚀 Production Database Initialization Starting...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Check what tables already exist
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            print(f"📊 Existing tables: {existing_tables}")
            
            # Only create tables if they don't exist
            if not existing_tables:
                print("🔄 Creating all tables...")
                db.create_all()
                print("✅ Database tables created")
            else:
                print("✅ Tables already exist, skipping creation")
            
            # Check if admin user exists
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
            
            # Check if Google OAuth columns exist
            if 'users' in existing_tables:
                columns = [col['name'] for col in inspector.get_columns('users')]
                print(f"\n📋 Users table columns: {columns}")
                
                # Check for required Google columns
                required_columns = ['google_id', 'picture', 'given_name', 'family_name']
                missing = [col for col in required_columns if col not in columns]
                
                if missing:
                    print(f"⚠️  Missing Google OAuth columns: {missing}")
                    print("   These will be added when models are updated")
                else:
                    print("✅ All Google OAuth columns present")
            
            print("🎉 Database initialization complete!")
            
        except Exception as e:
            print(f"❌ Initialization error: {e}")
            import traceback
            traceback.print_exc()
            # Don't crash the build - just log the error
            print("⚠️  Continuing despite error...")

if __name__ == '__main__':
    init_production_db()