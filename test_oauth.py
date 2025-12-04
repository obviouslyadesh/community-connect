# test_user_model.py - Create in root directory
from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    print("\n" + "="*60)
    print("🧪 TESTING USER MODEL")
    print("="*60)
    
    # Test 1: Check if User class exists and has methods
    print("\n📋 User class methods:")
    methods = [m for m in dir(User) if not m.startswith('_')]
    for method in methods:
        print(f"  - {method}")
    
    # Test 2: Check if get_or_create_google_user exists
    if hasattr(User, 'get_or_create_google_user'):
        print(f"\n✅ User.get_or_create_google_user exists!")
    else:
        print(f"\n❌ ERROR: User.get_or_create_google_user NOT FOUND!")
    
    # Test 3: Try to create a test Google user
    print("\n🧪 Testing get_or_create_google_user with sample data:")
    test_data = {
        'sub': 'test_google_id_123',
        'email': 'test_google_user@example.com',
        'name': 'Test Google User',
        'given_name': 'Test',
        'family_name': 'User',
        'picture': 'https://example.com/photo.jpg'
    }
    
    try:
        user = User.get_or_create_google_user(test_data)
        print(f"✅ Test successful! User created/retrieved:")
        print(f"   ID: {user.id}")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Google ID: {user.google_id}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Count users
    user_count = User.query.count()
    print(f"\n📊 Total users in database: {user_count}")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)