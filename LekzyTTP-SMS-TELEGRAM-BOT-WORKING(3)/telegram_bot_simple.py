#!/usr/bin/env python3
"""
Simple synchronous Telegram bot for Railway deployment
"""
import os
import time
import requests
import logging
from models import UserManager
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleTelegramBot:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.admin_user_id = int(os.getenv('TELEGRAM_ADMIN_ID', '1241344415'))
        self.last_update_id = 0
        
        # Initialize user manager
        try:
            self.user_manager = UserManager()
            logger.info("UserManager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize UserManager: {e}")
            self.user_manager = None
    
    def send_message(self, chat_id, text, parse_mode='Markdown'):
        """Send message to chat"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            response = requests.post(url, json=data, timeout=10)
            return response.json()
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
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
            logger.error(f"Failed to get updates: {e}")
            return {'ok': False, 'result': []}
    
    def is_admin(self, user_id):
        """Check if user is admin"""
        logger.info(f"Admin check: user_id={user_id}, admin_id={self.admin_user_id}, match={user_id == self.admin_user_id}")
        return user_id == self.admin_user_id
    
    def handle_start(self, chat_id, user_id):
        """Handle /start command"""
        if self.is_admin(user_id):
            message = """🚀 *Welcome to Lekzy-TTP SMS Bot, Admin!*

👑 *ADMIN COMMANDS:*
• `/genkey username days` - Generate API key
• `/listkeys` - List all active keys  
• `/revoke key` - Disable a key

🔍 *USER COMMANDS:*
• `/checkkey key` - Check key validity
• `/help` - Show help message

💀 *About Lekzy-TTP:*
Elite SMS system with Android & SMTP support.
Advanced tools for the digital underground.

💲 *Premium tulz and services* 💲
*Logs, Tulz & Box ar avail 4 zel!*
*HMU me4 Enityn💰💻*

🔥 *Contact:* @Lekzy_ttp
*"Whatsoever it is – GOD is Capable and Greater"*"""
        else:
            message = """🚀 *Welcome to Lekzy-TTP SMS Bot!*

🔍 *COMMANDS:*
• `/checkkey key` - Check API key validity
• `/help` - Show help message

💀 *About Lekzy-TTP:*
Professional SMS services for verified users.

🔥 *Contact:* @Lekzy_ttp for premium access
*"Whatsoever it is – GOD is Capable and Greater"*"""
        
        self.send_message(chat_id, message)
    
    def handle_listkeys(self, chat_id, user_id):
        """Handle /listkeys command"""
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
                # Format expiry date properly
                expires = user.get('expires', 'Unknown')
                if expires and expires != 'Unknown':
                    try:
                        # Parse and reformat date
                        from datetime import datetime
                        if isinstance(expires, str):
                            if 'T' in expires:
                                dt = datetime.fromisoformat(expires.replace('Z', '+00:00'))
                            else:
                                dt = datetime.strptime(expires, '%Y-%m-%d')
                            expires = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        expires = str(expires)[:16] if expires else 'Unknown'
                
                message += f"{i}. {user.get('api_key', 'N/A')}\n"
                message += f"👤 User: {user.get('username', 'Unknown')}\n"
                message += f"📅 Expires: {expires}\n"
                message += f"📊 SMS Sent: {user.get('sms_count', 0)}\n"
                message += "──────────────────────────────\n\n"
            
            self.send_message(chat_id, message)
        except Exception as e:
            logger.error(f"Error listing keys: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.send_message(chat_id, "❌ Error retrieving keys")
    
    def handle_help(self, chat_id, user_id):
        """Handle /help command"""
        if self.is_admin(user_id):
            message = """📚 *LEKZY-TTP BOT HELP - ADMIN*

👑 *ADMIN COMMANDS:*
• `/start` - Welcome message
• `/genkey username days` - Generate new API key
• `/listkeys` - Show all active keys
• `/revoke keycode` - Disable specific key
• `/checkkey keycode` - Check key status
• `/help` - This help message

💡 *EXAMPLES:*
• `/genkey john 30` - Create 30-day key for john
• `/revoke ABC-123-XYZ` - Disable key ABC-123-XYZ
• `/checkkey ABC-123-XYZ` - Check key status

🔥 *Contact:* @Lekzy_ttp"""
        else:
            message = """📚 *LEKZY-TTP BOT HELP*

🔍 *AVAILABLE COMMANDS:*
• `/start` - Welcome message
• `/checkkey keycode` - Check API key validity
• `/help` - This help message

💡 *EXAMPLE:*
• `/checkkey ABC-123-XYZ` - Check if key is valid

🔥 *Contact:* @Lekzy_ttp for premium access"""
        
        self.send_message(chat_id, message)
    
    def handle_genkey(self, chat_id, user_id, text):
        """Handle /genkey command"""
        if not self.is_admin(user_id):
            self.send_message(chat_id, "❌ Admin access required")
            return
        
        parts = text.split()
        if len(parts) < 3:
            self.send_message(chat_id, "❌ Usage: `/genkey username days`\nExample: `/genkey john 30`")
            return
        
        try:
            username = parts[1]
            days = int(parts[2])
            
            if not self.user_manager:
                self.send_message(chat_id, "❌ Database connection error")
                return
            
            # Generate new API key in Lekzy-TTP format
            import random, string
            key_suffix = ''.join(random.choices(string.digits, k=6))
            api_key = f'Lekzy-TTP-{key_suffix}'
            
            # Calculate expiry date
            expiry_date = datetime.now() + timedelta(days=days)
            expiry_str = expiry_date.strftime('%Y-%m-%d')
            
            # Try to add user to database
            try:
                success = self.user_manager.add_user(username, api_key, expiry_str)
                
                if success:
                    message = f"""✅ API Key Generated Successfully!

🆔 Key: `{api_key}`
👤 Username: {username}
📅 Valid for: {days} days
⏰ Expires: {expiry_str} 23:59

💀 Lekzy-TTP Premium Access Granted
🔥 Contact: @Lekzy_ttp
"Whatsoever it is – GOD is Capable and Greater\""""
                    self.send_message(chat_id, message)
                else:
                    self.send_message(chat_id, f"❌ Failed to create key for {username}")
                    
            except Exception as db_error:
                logger.error(f"Database error in genkey: {db_error}")
                import traceback
                logger.error(traceback.format_exc())
                
                # Try direct database insert as fallback
                try:
                    from models import Database
                    db = Database()
                    query = """
                    INSERT INTO users (username, api_key, expires, status, created_at, sms_count)
                    VALUES (%s, %s, %s, 'active', CURRENT_TIMESTAMP, 0)
                    """
                    db.execute_query(query, (username, api_key, expiry_str))
                    
                    message = f"""✅ API Key Generated Successfully!

🆔 Key: `{api_key}`
👤 Username: {username}
📅 Valid for: {days} days
⏰ Expires: {expiry_str} 23:59

💀 Lekzy-TTP Premium Access Granted
🔥 Contact: @Lekzy_ttp"""
                    self.send_message(chat_id, message)
                    
                except Exception as fallback_error:
                    logger.error(f"Fallback database error: {fallback_error}")
                    self.send_message(chat_id, f"❌ Database error: {str(db_error)[:100]}")
                
        except ValueError:
            self.send_message(chat_id, "❌ Days must be a number")
        except Exception as e:
            logger.error(f"Error generating key: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.send_message(chat_id, f"❌ Error: {str(e)[:100]}")
    
    def handle_revoke(self, chat_id, user_id, text):
        """Handle /revoke command"""
        if not self.is_admin(user_id):
            self.send_message(chat_id, "❌ Admin access required")
            return
        
        parts = text.split(' ', 1)
        if len(parts) < 2:
            self.send_message(chat_id, "❌ Usage: `/revoke API-KEY`")
            return
        
        key = parts[1].strip()
        
        if not self.user_manager:
            self.send_message(chat_id, "❌ Database connection error")
            return
        
        try:
            success = self.user_manager.revoke_user(key)
            if success:
                self.send_message(chat_id, f"✅ API key revoked: `{key}`")
            else:
                self.send_message(chat_id, f"❌ Key not found: `{key}`")
        except Exception as e:
            logger.error(f"Error revoking key: {e}")
            self.send_message(chat_id, "❌ Error revoking key")

    def process_command(self, message):
        """Process incoming command"""
        try:
            chat_id = message['chat']['id']
            user_id = message['from']['id']
            text = message.get('text', '').strip()
            
            logger.info(f"Processing command from user {user_id}: {text}")
            
            if text.startswith('/start'):
                self.handle_start(chat_id, user_id)
            elif text.startswith('/listkeys'):
                self.handle_listkeys(chat_id, user_id)
            elif text.startswith('/help'):
                self.handle_help(chat_id, user_id)
            elif text.startswith('/genkey'):
                self.handle_genkey(chat_id, user_id, text)
            elif text.startswith('/revoke'):
                self.handle_revoke(chat_id, user_id, text)
            elif text.startswith('/checkkey'):
                parts = text.split(' ', 1)
                if len(parts) > 1:
                    key = parts[1].strip()
                    # Simple key validation
                    self.send_message(chat_id, f"🔍 Checking key: `{key}`\n\n⚠️ Connect to SMS portal for full validation")
                else:
                    self.send_message(chat_id, "❌ Usage: `/checkkey YOUR-API-KEY`")
            else:
                self.send_message(chat_id, f"❓ Unknown command: {text}\nUse `/help` for available commands.")
                
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def run(self):
        """Main bot loop"""
        logger.info("🤖 Lekzy-TTP Telegram Bot started polling...")
        
        while True:
            try:
                updates = self.get_updates()
                
                if updates.get('ok') and updates.get('result'):
                    for update in updates['result']:
                        self.last_update_id = update['update_id']
                        
                        if 'message' in update:
                            self.process_command(update['message'])
                
                time.sleep(1)  # Small delay to prevent rate limiting
                
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"Bot error: {e}")
                time.sleep(5)  # Wait before retrying


def main():
    """Start the simple bot"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not set")
        return
    
    bot = SimpleTelegramBot(bot_token)
    bot.run()


if __name__ == "__main__":
    main()