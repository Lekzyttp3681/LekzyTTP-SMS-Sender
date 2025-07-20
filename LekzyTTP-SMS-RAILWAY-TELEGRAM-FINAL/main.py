#!/usr/bin/env python3
"""
Alternative entry point for Lekzy-TTP SMS Sender
This file ensures compatibility with different deployment systems
"""

# Import the Flask application
from app import app

if __name__ == '__main__':
    import os
    
    # Get configuration from environment
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Configure for production
    app.config['ENV'] = 'production' if not debug else 'development'
    
    print(f"Lekzy-TTP SMS Sender starting on {host}:{port}")
    app.run(host=host, port=port, debug=debug)