# update_db_schema.py - Create in root directory
from app import create_app, db
from app.models import User

def update_database_schema():
    print("🚀 Starting database schema update...")
    
    app = create_app()
    
    with app.app_context():
        try:
            print("📊 Current tables in database:")
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            for table in tables:
                print(f"  - {table}")
                columns = inspector.get_columns(table)
                for column in columns:
                    print(f"    - {column['name']} ({column['type']})")
            
            print("\n🔄 Updating schema...")
            
            # Drop and recreate all tables (WARNING: This will delete data!)
            # For production with existing data, use Alembic migrations instead
            db.drop_all()
            print("✅ Dropped all tables")
            
            db.create_all()
            print("✅ Created all tables with new schema")
            
            # Create admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                user_type='volunteer',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            print("✅ Created admin user: admin / admin123")
            
            db.session.commit()
            print("\n🎉 Database schema updated successfully!")
            
            # Verify the schema
            print("\n📋 Verifying new schema...")
            inspector = db.inspect(db.engine)
            users_columns = inspector.get_columns('users')
            print("Columns in 'users' table:")
            for col in users_columns:
                print(f"  - {col['name']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

if __name__ == '__main__':
    update_database_schema()