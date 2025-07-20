#!/usr/bin/env python3
"""
Ultra simple working Telegram bot - no imports, no complexity
"""

import requests
import time
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UltraSimpleBot:
    def __init__(self):
        self.token = '7356697443:AAERgF724RHu8Ec7BTlPgewp5hM-yoYOM2A'
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.admin_id = 1241344415
        self.last_update_id = 0
        
        logger.info(f"Ultra simple bot initialized for admin {self.admin_id}")
    
    def send_message(self, chat_id, text):
        """Send message"""
        try:
            data = {'chat_id': chat_id, 'text': text}
            response = requests.post(f"{self.base_url}/sendMessage", json=data, timeout=10)
            result = response.json()
            if result.get('ok'):
                logger.info(f"✅ Message sent to {chat_id}")
                return True
            else:
                logger.error(f"❌ Send failed: {result}")
                return False
        except Exception as e:
            logger.error(f"❌ Send error: {e}")
            return False
    
    def get_updates(self):
        """Get updates"""
        try:
            params = {
                'offset': self.last_update_id + 1,
                'timeout': 3,
                'limit': 10
            }
            response = requests.get(f"{self.base_url}/getUpdates", params=params, timeout=5)
            return response.json()
        except Exception as e:
            logger.error(f"❌ Get updates error: {e}")
            return {'ok': False, 'result': []}
    
    def handle_message(self, message):
        """Handle incoming message"""
        try:
            chat_id = message['chat']['id']
            user_id = message['from']['id']
            text = message.get('text', '').strip()
            
            logger.info(f"📨 Message: '{text}' from user {user_id}")
            
            if not text.startswith('/'):
                return
            
            # Simple command responses
            if text == '/start':
                if user_id == self.admin_id:
                    msg = """🚀 ULTRA SIMPLE BOT - ADMIN

Commands:
/start - This message
/test - Test response
/help - Help message

👑 You are admin: """ + str(user_id)
                else:
                    msg = "🚀 ULTRA SIMPLE BOT\n\nYou are not admin."
                self.send_message(chat_id, msg)
                
            elif text == '/test':
                msg = f"✅ TEST SUCCESSFUL!\nUser ID: {user_id}\nAdmin: {user_id == self.admin_id}"
                self.send_message(chat_id, msg)
                
            elif text == '/help':
                msg = "📚 ULTRA SIMPLE BOT HELP\n\n/start - Welcome\n/test - Test\n/help - This help"
                self.send_message(chat_id, msg)
                
            elif text.startswith('/genkey'):
                if user_id == self.admin_id:
                    parts = text.split()
                    if len(parts) >= 3:
                        username = parts[1]
                        days = parts[2]
                        key = f"Lekzy-TTP-{int(time.time()) % 999999}"
                        msg = f"✅ KEY GENERATED!\n\n🔑 Key: {key}\n👤 User: {username}\n📅 Days: {days}"
                    else:
                        msg = "❌ Usage: /genkey username days"
                else:
                    msg = "❌ Admin only"
                self.send_message(chat_id, msg)
                
            else:
                if user_id == self.admin_id:
                    msg = f"❓ Unknown command: {text}\nTry /help"
                    self.send_message(chat_id, msg)
                
        except Exception as e:
            logger.error(f"❌ Handle message error: {e}")
    
    def run(self):
        """Main bot loop"""
        logger.info("🤖 Ultra Simple Bot starting...")
        
        # Test connection
        try:
            response = requests.get(f"{self.base_url}/getMe", timeout=10)
            result = response.json()
            if result.get('ok'):
                logger.info(f"✅ Connected as @{result['result']['username']}")
            else:
                logger.error(f"❌ Connection failed: {result}")
                return
        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            return
        
        # Send startup message to admin
        startup_msg = "🚀 ULTRA SIMPLE BOT STARTED!\n\nSend /start to test commands."
        self.send_message(self.admin_id, startup_msg)
        
        # Main loop
        while True:
            try:
                updates = self.get_updates()
                
                if updates.get('ok') and updates.get('result'):
                    for update in updates['result']:
                        self.last_update_id = update['update_id']
                        
                        if 'message' in update:
                            self.handle_message(update['message'])
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("🛑 Bot stopped")
                break
            except Exception as e:
                logger.error(f"❌ Main loop error: {e}")
                time.sleep(5)

def main():
    bot = UltraSimpleBot()
    bot.run()

if __name__ == "__main__":
    main()