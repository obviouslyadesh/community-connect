from app import create_app, db
from app.models import User

def init_production_db():
    print("🚀 Production Database Initialization Starting...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables if they don't exist
            db.create_all()
            print("✅ Database tables created/verified")
            
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
            
            print("🎉 Database initialization complete!")
            
        except Exception as e:
            print(f"❌ Initialization error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    init_production_db()