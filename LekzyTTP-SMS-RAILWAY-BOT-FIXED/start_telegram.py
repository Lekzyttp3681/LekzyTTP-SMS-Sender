#!/usr/bin/env python3
"""
Standalone Telegram bot starter for Railway
"""
import os
import logging
from telegram_bot import SimpleLekzyBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not set")
        return
    
    logger.info("Starting Lekzy-TTP Telegram Bot on Railway...")
    bot = SimpleLekzyBot(bot_token)
    bot.run()

if __name__ == "__main__":
    main()