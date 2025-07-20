#!/usr/bin/env python3
"""
Simple Railway deployment - Just run Flask app
Telegram bot runs separately as worker
"""
import os
import logging
from app import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    logger.info(f"Starting SMS Sender on Railway port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)