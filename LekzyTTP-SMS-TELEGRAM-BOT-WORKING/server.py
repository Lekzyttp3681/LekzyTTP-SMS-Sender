#!/usr/bin/env python3
"""
Universal Server Entry Point for Lekzy-TTP SMS Sender
This file provides maximum compatibility with deployment systems
"""

import os
import sys

# Ensure environment variables are set
os.environ.setdefault('SECRET_KEY', os.urandom(32).hex())
os.environ.setdefault('ADMIN_PASSWORD', 'LekzyTTP@2025')
os.environ.setdefault('DEFAULT_API_KEY', 'lekzy-ttp-default-2025')
os.environ.setdefault('PORT', '5000')
os.environ.setdefault('HOST', '0.0.0.0')

# Import the Flask application
from app import app

def start_server():
    """Start the server with proper configuration"""
    try:
        port = int(os.environ.get('PORT', 5000))
        host = '0.0.0.0'  # Force host for deployment
        
        print(f"Starting Lekzy-TTP SMS Sender")
        print(f"Server: {host}:{port}")
        print(f"Mode: Production")
        print(f"Ready for deployment")
        
        # Ensure Flask is properly configured for deployment
        app.config.update(
            ENV='production',
            TESTING=False,
            DEBUG=False,
            SECRET_KEY=os.environ.get('SECRET_KEY', os.urandom(32).hex())
        )
        
        app.run(
            host=host,
            port=port,
            debug=False,
            threaded=True,
            use_reloader=False,
            processes=1
        )
    except Exception as e:
        print(f"Server startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    start_server()

# Also make the app directly available for WSGI
application = app