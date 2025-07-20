#!/usr/bin/env python3
"""
Lekzy-TTP SMS Telegram Bot - Ultra Simple Version for Testing
"""

import os
import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from models import UserManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleLekzyBot:
    def __init__(self, token):
        self.token = token
        self.admin_user_id = os.getenv('TELEGRAM_ADMIN_ID', '1241344415')
        
        # Initialize user manager with error handling
        try:
            self.user_manager = UserManager()
            logger.info("UserManager initialized")
        except Exception as e:
            logger.error(f"UserManager error: {e}")
            self.user_manager = None
        
        # Build application
        self.application = Application.builder().token(token).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_cmd))
        self.application.add_handler(CommandHandler("genkey", self.generate_key))
        self.application.add_handler(CommandHandler("listkeys", self.list_keys))
        self.application.add_handler(CommandHandler("checkkey", self.check_key))
        self.application.add_handler(CommandHandler("revoke", self.revoke_key))
    
    def is_admin(self, user_id):
        return str(user_id) == str(self.admin_user_id)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        username = update.effective_user.username or "User"
        
        if self.is_admin(user_id):
            message = f"""🚀 Welcome Admin {username}!

You have full access to Lekzy-TTP SMS Bot.

Commands:
/genkey username days - Generate API key
/listkeys - Show all keys
/checkkey key - Check key status
/revoke key - Disable key
/help - Show help

💀 Elite SMS System Active
Contact: @Lekzy_ttp"""
        else:
            message = f"""🚀 Welcome {username}!

Lekzy-TTP SMS Bot Commands:
/checkkey your-key - Check your key
/help - Show help

💲 Premium services available
Contact: @Lekzy_ttp for access"""
        
        await update.message.reply_text(message)
        logger.info(f"Start command from user {user_id} ({username})")
    
    async def help_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Help: Use /start for commands")
    
    async def generate_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ Admin only. Contact @Lekzy_ttp")
            return
        
        if not self.user_manager:
            await update.message.reply_text("❌ Database error")
            return
        
        if len(context.args) != 2:
            await update.message.reply_text("Usage: /genkey username days")
            return
        
        try:
            username = context.args[0]
            days = int(context.args[1])
            
            api_key = self.user_manager.generate_api_key(username, days)
            await update.message.reply_text(f"✅ Key created: {api_key}\nUser: {username}\nDays: {days}")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def list_keys(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ Admin only")
            return
        
        if not self.user_manager:
            await update.message.reply_text("❌ Database error")
            return
        
        try:
            keys = self.user_manager.get_active_keys()
            if not keys:
                await update.message.reply_text("📭 No active keys")
                return
            
            message = "📋 Active Keys:\n\n"
            for key in keys[:5]:  # Limit to 5 keys
                message += f"Key: {key['api_key']}\n"
                message += f"User: {key['username']}\n"
                message += f"SMS: {key['total_sms_sent']}\n\n"
            
            await update.message.reply_text(message)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def check_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.user_manager:
            await update.message.reply_text("❌ Database error")
            return
        
        if len(context.args) != 1:
            await update.message.reply_text("Usage: /checkkey YOUR-KEY")
            return
        
        try:
            api_key = context.args[0]
            user = self.user_manager.get_user_by_key(api_key)
            
            if not user:
                await update.message.reply_text("❌ Invalid key")
                return
            
            valid = self.user_manager.is_key_valid(api_key)
            status = "✅ ACTIVE" if valid else "❌ EXPIRED"
            
            message = f"""Key Status: {status}
User: {user['username']}
SMS Sent: {user['total_sms_sent']}
Expires: {user['expires_at'].strftime('%Y-%m-%d')}"""
            
            await update.message.reply_text(message)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def revoke_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ Admin only")
            return
        
        if not self.user_manager:
            await update.message.reply_text("❌ Database error")
            return
        
        if len(context.args) != 1:
            await update.message.reply_text("Usage: /revoke KEY")
            return
        
        try:
            api_key = context.args[0]
            username = self.user_manager.revoke_key(api_key)
            
            if username:
                await update.message.reply_text(f"✅ Key revoked for: {username}")
            else:
                await update.message.reply_text("❌ Key not found")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    def run(self):
        logger.info("Starting Simple Lekzy-TTP Bot...")
        self.application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not set")
        exit(1)
    
    bot = SimpleLekzyBot(BOT_TOKEN)
    bot.run()