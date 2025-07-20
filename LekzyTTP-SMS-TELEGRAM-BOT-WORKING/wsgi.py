"""
WSGI entry point for Lekzy-TTP SMS Sender
Used for production deployment with WSGI servers
"""

import os
from app import app

# Set environment variables for production
if not os.getenv('SECRET_KEY'):
    os.environ['SECRET_KEY'] = os.urandom(32).hex()

if not os.getenv('ADMIN_PASSWORD'):
    os.environ['ADMIN_PASSWORD'] = 'LekzyTTP@2025'

if not os.getenv('DEFAULT_API_KEY'):
    os.environ['DEFAULT_API_KEY'] = 'lekzy-ttp-default-2025'

# WSGI application object
application = app

if __name__ == "__main__":
    app.run()