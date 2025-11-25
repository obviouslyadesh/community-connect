# make_admin.py
from app import create_app, db
from app.models import User

def make_first_user_admin():
    app = create_app()
    
    with app.app_context():
        first_user = User.query.order_by(User.id.asc()).first()
        if first_user:
            first_user.is_admin = True
            db.session.commit()
            print(f"✅ Made {first_user.username} an admin")
        else:
            print("❌ No users found")

if __name__ == '__main__':
    make_first_user_admin()