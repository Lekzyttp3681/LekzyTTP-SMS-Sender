#!/usr/bin/env python3
"""
Railway deployment script to run both Flask app and Telegram bot
"""

import os
import sys
import subprocess
import threading
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_flask_app():
    """Run the Flask SMS application"""
    try:
        logger.info("Starting Flask SMS application...")
        port = os.getenv('PORT', '5000')
        
        # Use gunicorn for production
        cmd = [
            'gunicorn', 
            'app:app',
            '--bind', f'0.0.0.0:{port}',
            '--workers', '2',
            '--timeout', '120',
            '--access-logfile', '-',
            '--error-logfile', '-'
        ]
        
        subprocess.run(cmd, check=True)
        
    except Exception as e:
        logger.error(f"Flask app error: {e}")
        sys.exit(1)

def run_telegram_bot():
    """Run the Telegram bot"""
    try:
        # Wait a bit for the main app to start
        time.sleep(5)
        logger.info("Starting Telegram bot...")
        
        # Check if bot token is available
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            logger.warning("TELEGRAM_BOT_TOKEN not set - bot will not start")
            return
        
        # Import and run the bot
        from telegram_bot import LekzyTTPBot
        
        bot = LekzyTTPBot(bot_token)
        bot.run()
        
    except Exception as e:
        logger.error(f"Telegram bot error: {e}")
        # Don't exit - let the main app continue running

def main():
    """Main function to run both services"""
    logger.info("Starting Lekzy-TTP SMS services on Railway...")
    
    # Start Telegram bot in background thread
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()
    
    # Run Flask app in main thread
    run_flask_app()

if __name__ == "__main__":
    main()