#!/usr/bin/env python3
"""
FIXED Telegram Bot for Lekzy-TTP SMS
This version completely replaces the broken bot with working logic
"""

import os
import sys
import requests
import time
import logging
import random
import string
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LekzyTTPBot:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.last_update_id = 0
        self.admin_user_id = 1241344415
        
        # Initialize user manager
        self.user_manager = None
        try:
            from models import UserManager
            self.user_manager = UserManager()
            logger.info("✅ UserManager initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize UserManager: {e}")
    
    def send_message(self, chat_id, text):
        """Send message to chat"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text
            }
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get('ok'):
                logger.info(f"✅ Message sent to {chat_id}")
            else:
                logger.error(f"❌ Failed to send message: {result}")
            
            return result
        except Exception as e:
            logger.error(f"❌ Send message error: {e}")
            return None
    
    def get_updates(self):
        """Get updates from Telegram"""
        try:
            url = f"{self.base_url}/getUpdates"
            params = {
                'offset': self.last_update_id + 1,
                'timeout': 5,
                'limit': 100
            }
            response = requests.get(url, params=params, timeout=10)
            return response.json()
        except Exception as e:
            logger.error(f"❌ Get updates error: {e}")
            return {'ok': False, 'result': []}
    
    def is_admin(self, user_id):
        """Check if user is admin"""
        return user_id == self.admin_user_id
    
    def cmd_start(self, chat_id, user_id):
        """Handle /start command"""
        logger.info(f"🚀 Processing /start for user {user_id}")
        
        if self.is_admin(user_id):
            message = """🚀 Welcome to Lekzy-TTP SMS Bot, Admin!

👑 ADMIN COMMANDS:
• /genkey username days - Generate API key
• /listkeys - List all active keys  
• /revoke key - Disable a key
• /checkkey key - Check key validity
• /help - Show help message

💀 About Lekzy-TTP:
Elite SMS system with Android & SMTP support.
Advanced tools for the digital underground.

💲 Premium tulz and services 💲
Logs, Tulz & Box ar avail 4 zel!
HMU me4 Enityn💰💻

🔥 Contact: @Lekzy_ttp
"Whatsoever it is – GOD is Capable and Greater\""""
        else:
            message = """🚀 Welcome to Lekzy-TTP SMS Bot!

🔍 COMMANDS:
• /checkkey key - Check API key validity
• /help - Show help message

💀 About Lekzy-TTP:
Professional SMS services for verified users.

🔥 Contact: @Lekzy_ttp for premium access
"Whatsoever it is – GOD is Capable and Greater\""""
        
        self.send_message(chat_id, message)
    
    def cmd_help(self, chat_id, user_id):
        """Handle /help command"""
        logger.info(f"📚 Processing /help for user {user_id}")
        
        if self.is_admin(user_id):
            message = """📚 LEKZY-TTP BOT HELP - ADMIN

👑 ADMIN COMMANDS:
• /start - Welcome message
• /genkey username days - Generate new API key
• /listkeys - Show all active keys
• /revoke keycode - Disable specific key
• /checkkey keycode - Check key status
• /help - This help message

💡 EXAMPLES:
• /genkey john 30 - Create 30-day key for john
• /revoke Lekzy-TTP-123456 - Disable key
• /checkkey Lekzy-TTP-123456 - Check key status

🔥 Contact: @Lekzy_ttp"""
        else:
            message = """📚 LEKZY-TTP BOT HELP

🔍 AVAILABLE COMMANDS:
• /start - Welcome message
• /checkkey keycode - Check API key validity
• /help - This help message

💡 EXAMPLE:
• /checkkey Lekzy-TTP-123456 - Check if key is valid

🔥 Contact: @Lekzy_ttp for premium access"""
        
        self.send_message(chat_id, message)
    
    def cmd_listkeys(self, chat_id, user_id):
        """Handle /listkeys command"""
        logger.info(f"📋 Processing /listkeys for user {user_id}")
        
        if not self.is_admin(user_id):
            self.send_message(chat_id, "❌ Admin access required")
            return
        
        if not self.user_manager:
            self.send_message(chat_id, "❌ Database connection error")
            return
        
        try:
            users = self.user_manager.get_all_users()
            if not users:
                self.send_message(chat_id, "📝 No API keys found")
                return
            
            message = "📋 Active API Keys:\n\n"
            for i, user in enumerate(users, 1):
                # Format expiry date
                expires = user.get('expires_at', 'Unknown')
                if expires and expires != 'Unknown':
                    try:
                        if isinstance(expires, str):
                            expires = expires[:16]  # Truncate to YYYY-MM-DD HH:MM
                        else:
                            expires = str(expires)[:16]
                    except:
                        expires = 'Unknown'
                
                message += f"{i}. {user.get('api_key', 'N/A')}\n"
                message += f"👤 User: {user.get('username', 'Unknown')}\n"
                message += f"📅 Expires: {expires}\n"
                message += f"📊 SMS Sent: {user.get('total_sms_sent', 0)}\n"
                message += "──────────────────────────────\n\n"
            
            self.send_message(chat_id, message)
            
        except Exception as e:
            logger.error(f"❌ Error listing keys: {e}")
            self.send_message(chat_id, "❌ Error retrieving keys")
    
    def cmd_genkey(self, chat_id, user_id, args):
        """Handle /genkey command"""
        logger.info(f"🔑 Processing /genkey for user {user_id}, args: {args}")
        
        if not self.is_admin(user_id):
            self.send_message(chat_id, "❌ Admin access required")
            return
        
        if len(args) < 2:
            self.send_message(chat_id, "❌ Usage: /genkey username days\nExample: /genkey john 30")
            return
        
        username = args[0]
        try:
            days = int(args[1])
        except ValueError:
            self.send_message(chat_id, "❌ Days must be a number")
            return
        
        # Generate API key
        key_suffix = ''.join(random.choices(string.digits, k=6))
        api_key = f'Lekzy-TTP-{key_suffix}'
        
        # Calculate expiry
        expiry_date = datetime.now() + timedelta(days=days)
        expiry_str = expiry_date.strftime('%Y-%m-%d')
        
        try:
            if self.user_manager:
                success = self.user_manager.add_user(username, api_key, expiry_str)
                if success:
                    message = f"""✅ API Key Generated Successfully!

🆔 Key: {api_key}
👤 Username: {username}
📅 Valid for: {days} days
⏰ Expires: {expiry_str} 23:59

💀 Lekzy-TTP Premium Access Granted
🔥 Contact: @Lekzy_ttp
"Whatsoever it is – GOD is Capable and Greater\""""
                else:
                    message = f"❌ Failed to create key for {username}"
            else:
                message = "❌ Database connection error"
            
            self.send_message(chat_id, message)
            
        except Exception as e:
            logger.error(f"❌ Error generating key: {e}")
            self.send_message(chat_id, f"❌ Error generating key: {str(e)[:100]}")
    
    def cmd_revoke(self, chat_id, user_id, args):
        """Handle /revoke command"""
        logger.info(f"🚫 Processing /revoke for user {user_id}, args: {args}")
        
        if not self.is_admin(user_id):
            self.send_message(chat_id, "❌ Admin access required")
            return
        
        if len(args) < 1:
            self.send_message(chat_id, "❌ Usage: /revoke API-KEY\nExample: /revoke Lekzy-TTP-123456")
            return
        
        key = args[0]
        
        try:
            if self.user_manager:
                username = self.user_manager.revoke_key(key)
                if username:
                    message = f"""✅ API key revoked successfully!

🔑 Key: {key}
👤 User: {username}

🚫 Access disabled"""
                else:
                    message = f"❌ Key not found: {key}"
            else:
                message = "❌ Database connection error"
            
            self.send_message(chat_id, message)
            
        except Exception as e:
            logger.error(f"❌ Error revoking key: {e}")
            self.send_message(chat_id, f"❌ Error revoking key: {str(e)[:100]}")
    
    def cmd_checkkey(self, chat_id, user_id, args):
        """Handle /checkkey command"""
        logger.info(f"🔍 Processing /checkkey for user {user_id}, args: {args}")
        
        if len(args) < 1:
            self.send_message(chat_id, "❌ Usage: /checkkey YOUR-API-KEY\nExample: /checkkey Lekzy-TTP-123456")
            return
        
        key = args[0]
        
        try:
            if self.user_manager:
                user = self.user_manager.get_user_by_key(key)
                if user:
                    status = "🟢 Active" if user.get('is_active') else "🔴 Inactive"
                    message = f"""🔍 Key Status Check:

🔑 Key: {key}
👤 User: {user.get('username', 'Unknown')}
📊 Status: {status}
📅 Expires: {user.get('expires_at', 'Unknown')}
📱 SMS Sent: {user.get('total_sms_sent', 0)}

🔥 Connect to SMS portal for full access"""
                else:
                    message = f"❌ Key not found: {key}"
            else:
                message = f"🔍 Checking key: {key}\n\n⚠️ Connect to SMS portal for full validation"
            
            self.send_message(chat_id, message)
            
        except Exception as e:
            logger.error(f"❌ Error checking key: {e}")
            self.send_message(chat_id, f"🔍 Checking key: {key}\n\n⚠️ Database error, connect to SMS portal")
    
    def process_message(self, message):
        """Process incoming message"""
        try:
            chat_id = message['chat']['id']
            user_id = message['from']['id']
            text = message.get('text', '').strip()
            
            logger.info(f"📨 Message from {user_id}: '{text}'")
            
            if not text.startswith('/'):
                return
            
            # Parse command and arguments
            parts = text.split()
            command = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            logger.info(f"🎯 Command: {command}, Args: {args}, Admin: {self.is_admin(user_id)}")
            
            # Route commands
            if command == '/start':
                self.cmd_start(chat_id, user_id)
            elif command == '/help':
                self.cmd_help(chat_id, user_id)
            elif command == '/listkeys':
                self.cmd_listkeys(chat_id, user_id)
            elif command == '/genkey':
                self.cmd_genkey(chat_id, user_id, args)
            elif command == '/revoke':
                self.cmd_revoke(chat_id, user_id, args)
            elif command == '/checkkey':
                self.cmd_checkkey(chat_id, user_id, args)
            else:
                logger.warning(f"❓ Unknown command: {command}")
                if self.is_admin(user_id):
                    self.send_message(chat_id, f"❓ Unknown command: {command}\nUse /help for available commands.")
                
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def run(self):
        """Main bot loop"""
        logger.info("🤖 Lekzy-TTP Telegram Bot FIXED VERSION started...")
        
        # Test bot connection
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=10)
            result = response.json()
            if result.get('ok'):
                logger.info(f"✅ Bot connected: @{result['result']['username']}")
            else:
                logger.error(f"❌ Bot connection failed: {result}")
                return
        except Exception as e:
            logger.error(f"❌ Bot connection error: {e}")
            return
        
        while True:
            try:
                updates = self.get_updates()
                
                if updates.get('ok') and updates.get('result'):
                    for update in updates['result']:
                        self.last_update_id = update['update_id']
                        
                        if 'message' in update:
                            self.process_message(update['message'])
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("🛑 Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Bot error: {e}")
                time.sleep(5)

def main():
    """Start the fixed bot"""
    # Use new working token as fallback
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '7356697443:AAERgF724RHu8Ec7BTlPgewp5hM-yoYOM2A')
    if not bot_token:
        logger.error("❌ TELEGRAM_BOT_TOKEN not set")
        return
    
    logger.info(f"🔑 Using bot token: {bot_token[:20]}...")
    logger.info(f"👑 Admin user ID: 1241344415")
    
    bot = LekzyTTPBot(bot_token)
    bot.run()

if __name__ == "__main__":
    main()