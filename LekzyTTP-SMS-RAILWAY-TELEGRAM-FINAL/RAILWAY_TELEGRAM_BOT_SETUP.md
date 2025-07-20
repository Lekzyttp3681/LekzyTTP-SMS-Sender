# 🤖 RAILWAY TELEGRAM BOT SETUP GUIDE

## ✅ **What We Fixed:**

### **🔧 Railway Configuration Updated:**
- **Created `run_both.py`** - Runs both Flask app and Telegram bot together
- **Updated `railway.json`** - Uses new startup command for both services
- **Modified `Procfile`** - Proper process definitions for Railway

### **🌐 How It Works on Railway:**
1. **Main process** runs Flask SMS application on the web port
2. **Background thread** runs Telegram bot simultaneously  
3. **Both services** share the same database and environment
4. **Health checks** ensure everything stays running

## 🚀 **Deployment Steps:**

### **1. Environment Variables Required:**
Make sure these are set in Railway:
```
TELEGRAM_BOT_TOKEN=7356697443:AAFHPL6u1Riyun6qn_A5ubFjjgm8dxaaA1E
TELEGRAM_ADMIN_ID=1241344415
DATABASE_URL=your_railway_postgres_url
SECRET_KEY=your_secret_key
ADMIN_PASSWORD=your_admin_password
DEFAULT_API_KEY=your_default_api_key
```

### **2. Deploy to Railway:**
- **Upload files** to Railway or push to GitHub
- **Railway will automatically** run `python run_both.py`
- **Both services start** - SMS app and Telegram bot
- **Check logs** to confirm both are running

### **3. Test Your Bot:**
- **Search for** `@ttpsmsenderbot` on Telegram
- **Send** `/start` command
- **You should see** admin welcome message
- **All commands** will work: /genkey, /listkeys, /checkkey, /revoke

## 📱 **Bot Commands Available:**
- **/start** - Welcome with admin/user detection
- **/genkey username 30** - Generate API keys (admin only)
- **/listkeys** - Show all active keys (admin only)
- **/checkkey KEY-ABC** - Check key status (all users)
- **/revoke KEY-ABC** - Disable keys (admin only)
- **/help** - Show help with promotional messages

## 🎯 **Expected Behavior:**
- **SMS app available** at your Railway URL and custom domain
- **Telegram bot responding** to commands immediately
- **Admin access working** for user 1241344415
- **Database shared** between both services
- **No conflicts** - both run smoothly together

## 🔍 **Troubleshooting:**
If bot still doesn't work:
1. **Check Railway logs** for Telegram bot startup messages
2. **Verify environment variables** are set correctly
3. **Confirm bot token** is valid and not used elsewhere
4. **Test bot locally** first to ensure code works

Your Telegram bot will now work perfectly on Railway alongside your SMS application!

**Contact:** @Lekzy_ttp  
**"Whatsoever it is – GOD is Capable and Greater"**