# gunicorn_config.py - MINIMAL CONFIG FOR FREE TIER
# Worker Processes
workers = 1  # ONLY 1 worker for free tier (default is 2-4)
worker_class = 'sync'  # Use sync workers (less memory)
threads = 1  # Single-threaded
worker_connections = 1000

# Timeouts
timeout = 30  # 30 seconds max per request
graceful_timeout = 30
keepalive = 2

# Server Mechanics
max_requests = 1000  # Restart worker after 1000 requests
max_requests_jitter = 50  # Randomize restart
preload_app = True  # Load app before forking (saves memory)

# Server Socket
bind = '0.0.0.0:10000'

# Logging
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stdout
loglevel = 'warning'  # Less verbose than 'info'

# Process Name
proc_name = 'community_connect'