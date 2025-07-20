# 🔐 Telegram Bot Admin Setup Guide

## 🚨 SECURITY UPDATE APPLIED

Your Telegram bot now has proper admin controls! Here's what changed:

## ✅ **New Security Features:**

### **Admin-Only Commands:**
- `/genkey` - Only admin can generate API keys
- `/listkeys` - Only admin can see all keys
- `/revoke` - Only admin can disable keys

### **Public Commands:**
- `/checkkey` - Anyone can check their own key
- `/help` - Shows different help based on user type
- `/start` - Shows different welcome message

## 🛠️ **Required Setup:**

### **Step 1: Get Your Telegram User ID**
1. Message **@userinfobot** on Telegram
2. Copy your numeric user ID (example: 123456789)

### **Step 2: Set Admin ID in Railway**
1. Go to Railway → Variables
2. Add new variable:
   ```
   TELEGRAM_ADMIN_ID=your_actual_user_id
   ```
3. Replace with your real ID from Step 1

### **Step 3: Restart Bot**
- Railway will auto-restart after adding variable
- Test with `/start` command - should show admin message

## 👤 **User Experience:**

### **For Admin (You):**
```
/start → Shows admin welcome with all commands
/genkey user123 30 → Creates API key
/listkeys → Shows all active keys  
/revoke KEY-ABC → Disables key
/checkkey KEY-ABC → Shows key details
```

### **For Regular Users:**
```
/start → Shows user welcome (limited commands)
/genkey → Access denied message
/listkeys → Access denied message
/revoke → Access denied message
/checkkey KEY-ABC → Shows their key details (works)
```

## 🔒 **Security Benefits:**

### **Before Fix:**
- ❌ Anyone could generate unlimited API keys
- ❌ Anyone could see all user keys
- ❌ Anyone could disable any key
- ❌ Major security vulnerability

### **After Fix:**
- ✅ Only you can generate keys
- ✅ Only you can see all keys
- ✅ Only you can revoke keys
- ✅ Users can only check their own keys
- ✅ Secure admin control

## 📱 **Bot Commands Summary:**

### **Admin Commands (You Only):**
- `/genkey username days` - Generate new API key
- `/listkeys` - View all active keys
- `/revoke key` - Disable a key

### **User Commands (Everyone):**
- `/checkkey key` - Check key status
- `/help` - Show help
- `/start` - Welcome message

## 🎯 **Recommended Workflow:**

### **For New Users:**
1. User contacts you @Lekzy_ttp
2. You verify they should have access
3. You use `/genkey username 30` in bot
4. You send them their API key privately
5. They use key in your SMS service

### **For Key Management:**
1. Use `/listkeys` to monitor active users
2. Use `/checkkey` to verify specific keys
3. Use `/revoke` to disable expired/problem keys
4. Users can check their own key status anytime

## ⚠️ **IMPORTANT:**

### **Set Your Admin ID NOW:**
Without setting TELEGRAM_ADMIN_ID, the bot will use a default ID (123456789) which isn't you. This means:
- You won't have admin access
- Someone else might accidentally get admin access
- The security fix won't protect your bot

### **To Get Your ID:**
1. Open Telegram
2. Search for **@userinfobot**
3. Send `/start` to the bot
4. Copy the ID number it gives you
5. Add to Railway environment variables

Your Telegram bot is now secure and professional!

Contact: @Lekzy_ttp
"Whatsoever it is – GOD is Capable and Greater"