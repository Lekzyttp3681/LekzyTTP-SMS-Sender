#!/usr/bin/env python3
"""
Run both SMS app and Telegram bot in same process for Railway
"""
import os
import threading
import logging
from app import app
from telegram_bot_fixed import LekzyTTPBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_telegram_bot():
    """Start simple Telegram bot in background thread"""
    try:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            logger.error("TELEGRAM_BOT_TOKEN not set - skipping bot")
            return
        
        logger.info("Starting FIXED Lekzy-TTP Telegram Bot on Railway...")
        bot = LekzyTTPBot(bot_token)
        bot.run()
        
    except Exception as e:
        logger.error(f"Bot startup failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

def main():
    """Start both SMS app and Telegram bot"""
    # Start Telegram bot in background thread
    bot_thread = threading.Thread(target=start_telegram_bot, daemon=True)
    bot_thread.start()
    logger.info("Telegram bot thread started")
    
    # Start Flask app
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting SMS app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    main()