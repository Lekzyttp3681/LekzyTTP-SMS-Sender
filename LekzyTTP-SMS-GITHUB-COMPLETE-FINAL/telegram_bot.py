import os
import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from models import Database, UserManager

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

class LekzyTTPBot:
    def __init__(self, token):
        self.token = token
        self.user_manager = UserManager()
        self.application = Application.builder().token(token).build()
        
        # Initialize database
        db = Database()
        db.init_db()
        
        # Add command handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("genkey", self.generate_key))
        self.application.add_handler(CommandHandler("listkeys", self.list_keys))
        self.application.add_handler(CommandHandler("checkkey", self.check_key))
        self.application.add_handler(CommandHandler("revoke", self.revoke_key))
        self.application.add_handler(CommandHandler("help", self.help_command))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        welcome_message = """🚀 Welcome to Lekzy-TTP SMS Bot!

🔑 Available Commands:
• /genkey [username] [days] - Generate API key
• /listkeys - List all active keys  
• /checkkey [key] - Check key validity
• /revoke [key] - Disable a key
• /help - Show this help message

📱 About Lekzy-TTP:
Advanced SMS sending system with Android & SMTP support.

Telegram: @Lekzy_ttp
"Whatsoever it is – GOD is Capable and Greater" """
        await update.message.reply_text(welcome_message)
    
    async def generate_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate a new API key"""
        try:
            # Check if user provided correct arguments
            if len(context.args) < 2:
                await update.message.reply_text(
                    "❌ Usage: /genkey [username] [days]\nExample: /genkey user123 30"
                )
                return
            
            username = context.args[0]
            try:
                days = int(context.args[1])
                if days < 1 or days > 365:
                    raise ValueError("Days must be between 1 and 365")
            except ValueError:
                await update.message.reply_text(
                    "❌ Error: Days must be a number between 1-365"
                )
                return
            
            # Generate the key
            api_key = self.user_manager.generate_api_key(username, days)
            expires_date = (datetime.now().replace(microsecond=0) + 
                          timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
            
            response = f"""✅ API Key Generated Successfully!

🔑 Key: {api_key}
👤 User: {username}
📅 Expires: {expires_date}
⏰ Valid for: {days} days

Note: Keep this key secure and don't share it publicly."""
            
            await update.message.reply_text(response)
            logger.info(f"Generated API key for {username}: {api_key}")
            
        except Exception as e:
            logger.error(f"Error generating key: {e}")
            await update.message.reply_text(
                "❌ **Error:** Failed to generate API key. Please try again."
            )
    
    async def list_keys(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all active API keys"""
        try:
            active_keys = self.user_manager.get_active_keys()
            
            if not active_keys:
                await update.message.reply_text(
                    "📝 **No active API keys found.**"
                )
                return
            
            response = "📋 **Active API Keys:**\n\n"
            
            for i, key_info in enumerate(active_keys, 1):
                expires_str = key_info['expires_at'].strftime('%Y-%m-%d %H:%M')
                response += f"""
**{i}.** `{key_info['api_key']}`
👤 **User:** {key_info['username']}
📅 **Expires:** {expires_str}
📊 **SMS Sent:** {key_info['total_sms_sent']}
                """
                
                if i < len(active_keys):
                    response += "\n" + "─" * 30 + "\n"
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error listing keys: {e}")
            await update.message.reply_text(
                "❌ **Error:** Failed to retrieve keys. Please try again."
            )
    
    async def check_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check if an API key is valid"""
        try:
            if len(context.args) != 1:
                await update.message.reply_text(
                    "❌ **Usage:** `/checkkey [key]`\n"
                    "**Example:** `/checkkey KEY-Lekzy-TTP-ABC12345`",
                    parse_mode='Markdown'
                )
                return
            
            api_key = context.args[0]
            user = self.user_manager.get_user_by_key(api_key)
            
            if not user:
                await update.message.reply_text("❌ **Invalid API key.**")
                return
            
            is_valid = self.user_manager.is_key_valid(api_key)
            status = "✅ **ACTIVE**" if is_valid else "❌ **EXPIRED/INACTIVE**"
            
            expires_str = user['expires_at'].strftime('%Y-%m-%d %H:%M:%S')
            created_str = user['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            response = f"""
🔍 **API Key Information:**

🔑 **Key:** `{api_key}`
📊 **Status:** {status}
👤 **User:** {user['username']}
📅 **Created:** {created_str}
⏰ **Expires:** {expires_str}
📱 **SMS Sent:** {user['total_sms_sent']}
🎯 **Last Activity:** {user['last_activity'].strftime('%Y-%m-%d %H:%M:%S') if user['last_activity'] else 'Never'}
            """
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error checking key: {e}")
            await update.message.reply_text(
                "❌ **Error:** Failed to check key. Please try again."
            )
    
    async def revoke_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Revoke an API key"""
        try:
            if len(context.args) != 1:
                await update.message.reply_text(
                    "❌ **Usage:** `/revoke [key]`\n"
                    "**Example:** `/revoke KEY-Lekzy-TTP-ABC12345`",
                    parse_mode='Markdown'
                )
                return
            
            api_key = context.args[0]
            username = self.user_manager.revoke_key(api_key)
            
            if username:
                response = f"""
✅ **API Key Revoked Successfully!**

🔑 **Key:** `{api_key}`
👤 **User:** {username}
🚫 **Status:** Disabled

The key is now inactive and cannot be used.
                """
                await update.message.reply_text(response, parse_mode='Markdown')
                logger.info(f"Revoked API key for {username}: {api_key}")
            else:
                await update.message.reply_text(
                    "❌ **Error:** API key not found or already inactive."
                )
            
        except Exception as e:
            logger.error(f"Error revoking key: {e}")
            await update.message.reply_text(
                "❌ **Error:** Failed to revoke key. Please try again."
            )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help information"""
        help_text = """
🤖 **Lekzy-TTP SMS Bot Commands:**

🔑 **Key Management:**
• `/genkey [username] [days]` - Generate new API key
  Example: `/genkey john123 30`

📋 **Information:**
• `/listkeys` - Show all active API keys
• `/checkkey [key]` - Check key status and details
  Example: `/checkkey KEY-Lekzy-TTP-ABC12345`

🚫 **Administration:**
• `/revoke [key]` - Disable an API key
  Example: `/revoke KEY-Lekzy-TTP-ABC12345`

❓ **Support:**
• `/help` - Show this help message
• `/start` - Welcome message

📱 **Contact:** @Lekzy_ttp
🌟 *"Whatsoever it is – GOD is Capable and Greater"*
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    def run(self):
        """Run the bot"""
        logger.info("Starting Lekzy-TTP Telegram Bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    # Bot token should be provided as environment variable
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable not set")
        print("Please set your Telegram bot token in the environment variables.")
        exit(1)
    
    # Initialize and run the bot
    bot = LekzyTTPBot(BOT_TOKEN)
    bot.run()