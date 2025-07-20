#!/usr/bin/env python3
"""
Lekzy-TTP SMS Telegram Bot - Railway Production Ready
Clean, error-free bot for Railway deployment
"""

import os
import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from models import UserManager

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class LekzyTTPBot:
    def __init__(self, token):
        self.token = token
        self.application = Application.builder().token(token).build()
        
        # Initialize user manager
        try:
            self.user_manager = UserManager()
            logger.info("UserManager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize UserManager: {e}")
            self.user_manager = None
        
        # Admin user ID - Set via environment variable
        self.admin_user_id = os.getenv('TELEGRAM_ADMIN_ID', '1241344415')
        logger.info(f"Admin user ID: {self.admin_user_id}")
        
        # Add command handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("genkey", self.generate_key))
        self.application.add_handler(CommandHandler("listkeys", self.list_keys))
        self.application.add_handler(CommandHandler("checkkey", self.check_key))
        self.application.add_handler(CommandHandler("revoke", self.revoke_key))
        self.application.add_handler(CommandHandler("help", self.help_command))
    
    def is_admin(self, user_id):
        """Check if user is admin"""
        return str(user_id) == str(self.admin_user_id)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send welcome message"""
        user_id = update.effective_user.id
        is_admin = self.is_admin(user_id)
        
        if is_admin:
            message = """🚀 Welcome to Lekzy-TTP SMS Bot, Admin!

👑 ADMIN COMMANDS:
• /genkey [username] [days] - Generate API key
• /listkeys - List all active keys  
• /revoke [key] - Disable a key

🔍 USER COMMANDS:
• /checkkey [key] - Check key validity
• /help - Show help message

💀 About Lekzy-TTP:
Elite SMS system with Android & SMTP support.
Advanced tools for the digital underground.

🔥 Contact: @Lekzy_ttp
"Whatsoever it is – GOD is Capable and Greater"
"""
        else:
            message = """🚀 Welcome to Lekzy-TTP SMS Bot!

🔍 Available Commands:
• /checkkey [key] - Check your key status
• /help - Show help message

💀 About Lekzy-TTP:
Elite SMS system with Android & SMTP support.
Professional tools for serious users.

💲 Premium tulz and services 💲
Logs, Tulz & Box ar avail 4 zel! HMU me4 Enityn💰💻

🔥 For API access or support: @Lekzy_ttp
"Whatsoever it is – GOD is Capable and Greater"
"""
        
        await update.message.reply_text(message)
    
    async def generate_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate a new API key - ADMIN ONLY"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            message = """🚫 Access Denied: Only admins can generate API keys.
Contact @Lekzy_ttp for key generation.

💲 Premium tulz and services 💲
Logs, Tulz & Box ar avail 4 zel! HMU me4 Enityn💰💻"""
            await update.message.reply_text(message)
            return

        if not self.user_manager:
            await update.message.reply_text("❌ Database error. Please try again later.")
            return
        
        try:
            if len(context.args) != 2:
                await update.message.reply_text("❌ Usage: /genkey [username] [days]\nExample: /genkey john123 30")
                return
            
            username = context.args[0]
            try:
                days = int(context.args[1])
            except ValueError:
                await update.message.reply_text("❌ Days must be a number")
                return
            
            if days < 1 or days > 365:
                await update.message.reply_text("❌ Days must be between 1 and 365")
                return
            
            api_key = self.user_manager.generate_api_key(username, days)
            expires_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
            
            message = f"""✅ API Key Generated Successfully!

🔑 Key: {api_key}
👤 User: {username}
⏰ Expires: {expires_date}
📅 Valid for: {days} days

💀 Elite access granted!
Contact: @Lekzy_ttp"""
            
            await update.message.reply_text(message)
            logger.info(f"Generated API key for {username}")
            
        except Exception as e:
            logger.error(f"Error generating key: {e}")
            await update.message.reply_text("❌ Error: Failed to generate API key. Please try again.")
    
    async def list_keys(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all active API keys - ADMIN ONLY"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            message = """🚫 Access Denied: Only admins can view all keys.
Use /checkkey [your-key] to check your specific key.

💲 Premium tulz and services 💲
Logs, Tulz & Box ar avail 4 zel! HMU me4 Enityn💰💻
Contact: @Lekzy_ttp"""
            await update.message.reply_text(message)
            return

        if not self.user_manager:
            await update.message.reply_text("❌ Database error. Please try again later.")
            return
        
        try:
            active_keys = self.user_manager.get_active_keys()
            
            if not active_keys:
                await update.message.reply_text("📭 No active API keys found.")
                return
            
            message = "📋 Active API Keys:\n\n"
            
            for i, key_info in enumerate(active_keys, 1):
                expires_str = key_info['expires_at'].strftime('%Y-%m-%d %H:%M')
                message += f"{i}. {key_info['api_key']}\n"
                message += f"👤 User: {key_info['username']}\n"
                message += f"📅 Expires: {expires_str}\n"
                message += f"📊 SMS Sent: {key_info['total_sms_sent']}\n"
                
                if i < len(active_keys):
                    message += "━" * 30 + "\n\n"
            
            await update.message.reply_text(message)
            
        except Exception as e:
            logger.error(f"Error listing keys: {e}")
            await update.message.reply_text("❌ Error: Failed to retrieve keys. Please try again.")
    
    async def check_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check if an API key is valid"""
        if not self.user_manager:
            await update.message.reply_text("❌ Database error. Please try again later.")
            return
            
        try:
            if len(context.args) != 1:
                await update.message.reply_text("❌ Usage: /checkkey [key]\nExample: /checkkey KEY-Lekzy-TTP-ABC12345")
                return
            
            api_key = context.args[0]
            user = self.user_manager.get_user_by_key(api_key)
            
            if not user:
                await update.message.reply_text("❌ Invalid API key.")
                return
            
            is_valid = self.user_manager.is_key_valid(api_key)
            status = "✅ ACTIVE" if is_valid else "❌ EXPIRED/INACTIVE"
            
            expires_str = user['expires_at'].strftime('%Y-%m-%d %H:%M:%S')
            created_str = user['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            last_activity = user['last_activity'].strftime('%Y-%m-%d %H:%M:%S') if user['last_activity'] else 'Never'
            
            message = f"""🔍 API Key Information:

🔑 Key: {api_key}
📊 Status: {status}
👤 User: {user['username']}
📅 Created: {created_str}
⏰ Expires: {expires_str}
📱 SMS Sent: {user['total_sms_sent']}
🎯 Last Activity: {last_activity}

💲 Premium tulz and services 💲
Logs, Tulz & Box ar avail 4 zel! HMU me4 Enityn💰💻
Contact: @Lekzy_ttp"""
            
            await update.message.reply_text(message)
            
        except Exception as e:
            logger.error(f"Error checking key: {e}")
            await update.message.reply_text("❌ Error: Could not check key. Please try again.")
    
    async def revoke_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Revoke an API key - ADMIN ONLY"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            message = """🚫 Access Denied: Only admins can revoke keys.
Contact @Lekzy_ttp for key revocation.

💲 Premium tulz and services 💲
Logs, Tulz & Box ar avail 4 zel! HMU me4 Enityn💰💻"""
            await update.message.reply_text(message)
            return

        if not self.user_manager:
            await update.message.reply_text("❌ Database error. Please try again later.")
            return
        
        try:
            if len(context.args) != 1:
                await update.message.reply_text("❌ Usage: /revoke [key]\nExample: /revoke KEY-Lekzy-TTP-ABC12345")
                return
            
            api_key = context.args[0]
            username = self.user_manager.revoke_key(api_key)
            
            if username:
                await update.message.reply_text(f"✅ API key revoked for user: {username}")
                logger.info(f"Revoked API key for {username}")
            else:
                await update.message.reply_text("❌ API key not found or already inactive")
                
        except Exception as e:
            logger.error(f"Error revoking key: {e}")
            await update.message.reply_text("❌ Error: Could not revoke key. Please try again.")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help information"""
        user_id = update.effective_user.id
        is_admin = self.is_admin(user_id)
        
        if is_admin:
            message = """🤖 Lekzy-TTP SMS Bot - ADMIN Commands:

👑 ADMIN ONLY:
• /genkey [username] [days] - Generate new API key
  Example: /genkey john123 30
• /listkeys - Show all active API keys
• /revoke [key] - Disable an API key
  Example: /revoke KEY-Lekzy-TTP-ABC12345

🔍 PUBLIC COMMANDS:
• /checkkey [key] - Check key status and details
  Example: /checkkey KEY-Lekzy-TTP-ABC12345

❓ Support:
• /help - Show this help message
• /start - Welcome message

💀 Elite SMS Tools
Advanced systems for professionals

🔥 Contact: @Lekzy_ttp
"Whatsoever it is – GOD is Capable and Greater"
"""
        else:
            message = """🤖 Lekzy-TTP SMS Bot Commands:

🔍 Available to You:
• /checkkey [key] - Check your key status and details
  Example: /checkkey KEY-Lekzy-TTP-ABC12345
• /help - Show this help message
• /start - Welcome message

🔑 Need an API Key?
Contact admin: @Lekzy_ttp

💀 About LekzyTTP SMS:
Professional SMS sending service with Android & SMTP support.
Elite tools for serious operations.

💲 Premium tulz and services 💲
Logs, Tulz & Box ar avail 4 zel! HMU me4 Enityn💰💻

❓ Having Problems?
Contact support: @Lekzy_ttp

🔥 "Whatsoever it is – GOD is Capable and Greater"
"""
        
        await update.message.reply_text(message)
    
    def run(self):
        """Run the bot"""
        logger.info("Starting Lekzy-TTP Telegram Bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable not set")
        exit(1)
    
    bot = LekzyTTPBot(BOT_TOKEN)
    bot.run()