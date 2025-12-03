import os
import sys

print("🧪 TESTING PROJECT SETUP")
print("="*60)

# Check current directory
print(f"1. Working directory: {os.getcwd()}")

# Check .env file
env_path = '.env'
if os.path.exists(env_path):
    print(f"2. ✅ .env file found")
    with open(env_path, 'r') as f:
        for line in f:
            if 'GOOGLE_CLIENT_ID' in line:
                if '329204650680' in line:
                    print(f"   ✅ Real Client ID in .env: {line.strip()[:60]}...")
                else:
                    print(f"   ❌ Problem: {line.strip()}")
else:
    print(f"2. ❌ .env file NOT found!")

# Check config.py
config_path = 'config.py'
if os.path.exists(config_path):
    print(f"3. ✅ config.py found")
else:
    print(f"3. ❌ config.py NOT found!")

# Check app/__init__.py
init_path = 'app/__init__.py'
if os.path.exists(init_path):
    with open(init_path, 'r') as f:
        content = f.read()
        if 'create_app' in content:
            print(f"4. ✅ create_app function found in app/__init__.py")
        else:
            print(f"4. ❌ create_app NOT found in app/__init__.py")
else:
    print(f"4. ❌ app/__init__.py NOT found!")

print("="*60)
print("📋 To run: python run.py")
