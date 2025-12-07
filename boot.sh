# boot.sh - Startup script for Render
#!/bin/bash
echo "🚀 Starting Community Connect on Render..."
echo "📊 Memory check:"
free -m
echo "🔄 Starting Gunicorn with optimized settings..."

# Start Gunicorn with minimal memory footprint
exec gunicorn -c gunicorn_config.py run:app