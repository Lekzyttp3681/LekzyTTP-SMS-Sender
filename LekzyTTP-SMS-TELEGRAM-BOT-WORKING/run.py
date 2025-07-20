#!/usr/bin/env python3
"""
Lekzy-TTP SMS Sender Application Entry Point
This script ensures proper application startup for deployment
"""

import os
import sys
from app import app

# Ensure environment variables are set with defaults
if not os.getenv('SECRET_KEY'):
    os.environ['SECRET_KEY'] = os.urandom(32).hex()

if not os.getenv('ADMIN_PASSWORD'):
    os.environ['ADMIN_PASSWORD'] = 'LekzyTTP@2025'

if not os.getenv('DEFAULT_API_KEY'):
    os.environ['DEFAULT_API_KEY'] = 'lekzy-ttp-default-2025'

def main():
    """Main application entry point"""
    try:
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', '0.0.0.0')
        
        # Set production mode unless explicitly set to debug
        debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        
        print(f"Starting Lekzy-TTP SMS Sender on {host}:{port}")
        print(f"Debug mode: {debug_mode}")
        print(f"Environment: {'Development' if debug_mode else 'Production'}")
        
        # Ensure the app can handle deployment environments
        app.config['ENV'] = 'development' if debug_mode else 'production'
        app.config['TESTING'] = False
        
        app.run(host=host, port=port, debug=debug_mode, threaded=True)
        
    except Exception as e:
        print(f"Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()