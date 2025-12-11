import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 CHECKING .env LOADING")
print(f"Working directory: {os.getcwd()}")
print(f".env exists: {os.path.exists('.env')}")

if os.path.exists('.env'):
    with open('.env', 'r') as f:
        lines = f.readlines()
        print("📄 .env contents (Google related):")
        for line in lines:
            if 'GOOGLE' in line and '#' not in line[:1]:
                print(f"   {line.strip()[:60]}...")

print("\n" + "="*60)

# Import and create app
from app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"🚀 Starting Flask server on http://localhost:{port}")
    print("📢 Press CTRL+C to stop\n")
    app.run(host='0.0.0.0', port=port, debug=True)