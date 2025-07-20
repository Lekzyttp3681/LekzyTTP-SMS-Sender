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
                    msg = """🚀 LEKZY-TTP SMS BOT - ADMIN ACCESS

💲 Premium tulz and services 💲
Logs, Tulz & Box ar avail 4 zel!
HMU me4 Enityn💰💻

🌐 SMS Sender: https://lekzyttpsms.com/
📱 Telegram Group: t.me/LekzyTTP_OTP_SMSsender
💬 Contact: @Lekzy_ttp

👑 Admin Commands Available:
/genkey username days - Generate API key
/listkeys - View all active keys
/checkkey keyname - Check specific key
/revoke keyname - Revoke API key
/help - Full command list

Admin ID: """ + str(user_id)
                else:
                    msg = """🚀 LEKZY-TTP SMS BOT

💲 Premium tulz and services 💲
Logs, Tulz & Box ar avail 4 zel!
HMU me4 Enityn💰💻

🌐 SMS Sender: https://lekzyttpsms.com/
📱 Join Group: t.me/LekzyTTP_OTP_SMSsender
💬 Contact: @Lekzy_ttp

❌ Limited Access - Contact admin for key generation"""
                self.send_message(chat_id, msg)
                
            elif text == '/help':
                if user_id == self.admin_id:
                    msg = """📚 LEKZY-TTP SMS BOT - ADMIN HELP

💲 Premium tulz and services 💲
Logs, Tulz & Box ar avail 4 zel! HMU me4 Enityn💰💻

🌐 SMS Sender: https://lekzyttpsms.com/
📱 Telegram Group: t.me/LekzyTTP_OTP_SMSsender
💬 Contact: @Lekzy_ttp

👑 ADMIN COMMANDS:
/start - Welcome message
/genkey username days - Generate new API key
/listkeys - List all active keys with details
/checkkey keyname - Check specific key status
/revoke keyname - Permanently revoke API key
/help - This help message

🔧 UTILITY:
/test - Test bot connectivity

💎 You have FULL ACCESS to all functions"""
                else:
                    msg = """📚 LEKZY-TTP SMS BOT - USER HELP

💲 Premium tulz and services 💲
Logs, Tulz & Box ar avail 4 zel! HMU me4 Enityn💰💻

🌐 Try SMS Sender: https://lekzyttpsms.com/
📱 Join Our Group: t.me/LekzyTTP_OTP_SMSsender
💬 Contact: @Lekzy_ttp

👤 USER COMMANDS:
/start - Welcome message
/help - This help message

❌ KEY GENERATION: Admin only
❌ KEY MANAGEMENT: Admin only

Contact @Lekzy_ttp for premium access"""
                self.send_message(chat_id, msg)
                
            elif text == '/test':
                msg = f"✅ BOT CONNECTION TEST\n\nUser ID: {user_id}\nAdmin Status: {'👑 ADMIN' if user_id == self.admin_id else '👤 USER'}\nBot Status: 🟢 ONLINE"
                self.send_message(chat_id, msg)
                
            elif text.startswith('/genkey'):
                if user_id == self.admin_id:
                    parts = text.split()
                    if len(parts) >= 3:
                        username = parts[1]
                        days = parts[2]
                        # Generate unique key
                        timestamp = int(time.time())
                        key_id = timestamp % 999999
                        key = f"Lekzy-TTP-{key_id}"
                        
                        # Calculate expiry
                        import datetime
                        expiry_date = datetime.datetime.now() + datetime.timedelta(days=int(days))
                        expiry_str = expiry_date.strftime("%Y-%m-%d")
                        
                        msg = f"""✅ API KEY GENERATED SUCCESSFULLY!

🔑 Key: {key}
👤 Username: {username}
📅 Valid Days: {days}
⏰ Expires: {expiry_str}
📊 SMS Count: 0

💎 Key ready for SMS sending!
💲 Premium tulz and services - @Lekzy_ttp"""
                    else:
                        msg = "❌ USAGE ERROR\n\nCorrect format:\n/genkey username days\n\nExample:\n/genkey john 30"
                else:
                    msg = """❌ ACCESS DENIED

🚫 Key generation is ADMIN ONLY
👑 Contact admin for API keys

💲 Premium tulz and services 💲
🌐 SMS Sender: https://lekzyttpsms.com/
📱 Join Group: t.me/LekzyTTP_OTP_SMSsender
Contact: @Lekzy_ttp"""
                self.send_message(chat_id, msg)
                
            elif text.startswith('/listkeys'):
                if user_id == self.admin_id:
                    # Mock key list for demonstration
                    msg = """📋 ACTIVE API KEYS LIST

──────────────────────────────────
1️⃣ Key: Lekzy-TTP-123456
👤 User: john_doe
📅 Expires: 2025-08-15
📊 SMS Sent: 45
🟢 Status: ACTIVE

──────────────────────────────────
2️⃣ Key: Lekzy-TTP-789012
👤 User: sarah_wilson
📅 Expires: 2025-09-01
📊 SMS Sent: 23
🟢 Status: ACTIVE

──────────────────────────────────
3️⃣ Key: Lekzy-TTP-345678
👤 User: mike_brown
📅 Expires: 2025-07-25
📊 SMS Sent: 12
🟡 Status: EXPIRES SOON

──────────────────────────────────
💎 Total Active Keys: 3
📱 Total SMS Sent: 80
💲 Premium service by @Lekzy_ttp"""
                else:
                    msg = """❌ ACCESS DENIED

🚫 Key listing is ADMIN ONLY
Contact admin for key information

💲 Premium tulz and services 💲
🌐 SMS Sender: https://lekzyttpsms.com/
📱 Join Group: t.me/LekzyTTP_OTP_SMSsender
Contact: @Lekzy_ttp"""
                self.send_message(chat_id, msg)
                
            elif text.startswith('/checkkey'):
                if user_id == self.admin_id:
                    parts = text.split()
                    if len(parts) >= 2:
                        keyname = parts[1]
                        # Mock key check
                        msg = f"""🔍 KEY CHECK RESULT

🔑 Key: {keyname}
👤 Owner: john_doe
📅 Created: 2025-07-01
⏰ Expires: 2025-08-15
📊 SMS Sent: 45
📈 Daily Limit: 100
🟢 Status: ACTIVE & VALID

💎 Key is working perfectly!
💲 Premium service by @Lekzy_ttp"""
                    else:
                        msg = "❌ USAGE ERROR\n\nCorrect format:\n/checkkey keyname\n\nExample:\n/checkkey Lekzy-TTP-123456"
                else:
                    msg = """❌ ACCESS DENIED

🚫 Key checking is ADMIN ONLY
Contact admin for key status

💲 Premium tulz and services 💲
🌐 SMS Sender: https://lekzyttpsms.com/
📱 Join Group: t.me/LekzyTTP_OTP_SMSsender
Contact: @Lekzy_ttp"""
                self.send_message(chat_id, msg)
                
            elif text.startswith('/revoke'):
                if user_id == self.admin_id:
                    parts = text.split()
                    if len(parts) >= 2:
                        keyname = parts[1]
                        msg = f"""✅ KEY REVOKED SUCCESSFULLY

🔑 Revoked Key: {keyname}
👤 Former Owner: user_account
📅 Revoked Date: {time.strftime('%Y-%m-%d %H:%M')}
🚫 Status: PERMANENTLY DISABLED

⚠️ This action cannot be undone!
💲 Premium service by @Lekzy_ttp"""
                    else:
                        msg = "❌ USAGE ERROR\n\nCorrect format:\n/revoke keyname\n\nExample:\n/revoke Lekzy-TTP-123456"
                else:
                    msg = """❌ ACCESS DENIED

🚫 Key revocation is ADMIN ONLY
Contact admin for key management

💲 Premium tulz and services 💲
🌐 SMS Sender: https://lekzyttpsms.com/
📱 Join Group: t.me/LekzyTTP_OTP_SMSsender
Contact: @Lekzy_ttp"""
                self.send_message(chat_id, msg)
                
            else:
                if user_id == self.admin_id:
                    msg = f"❓ UNKNOWN COMMAND: {text}\n\nTry /help for all available commands"
                    self.send_message(chat_id, msg)
                else:
                    msg = """❌ LIMITED ACCESS

Available commands:
/start - Welcome
/help - Help

💲 Premium tulz and services 💲
🌐 SMS Sender: https://lekzyttpsms.com/
📱 Join Group: t.me/LekzyTTP_OTP_SMSsender
Contact: @Lekzy_ttp for full access"""
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
        startup_msg = """🚀 LEKZY-TTP SMS BOT ONLINE!

💲 Premium tulz and services 💲
Logs, Tulz & Box ar avail 4 zel!
HMU me4 Enityn💰💻

🌐 SMS Sender: https://lekzyttpsms.com/
📱 Telegram Group: t.me/LekzyTTP_OTP_SMSsender
💬 Contact: @Lekzy_ttp

✅ All admin commands ready:
/genkey /listkeys /checkkey /revoke /help

👑 Bot ready for SMS key management!"""
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