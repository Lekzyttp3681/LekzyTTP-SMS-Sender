# Lekzy-TTP SMS Sender

A comprehensive SMS sending application built for Replit deployment with secure API key authentication.

## 🚀 Quick Start

Your SMS sender is already running on Replit! Just:

1. **Click the "Open Website" button** in Replit
2. **Log in** with your API key (ask admin for access)
3. **Start sending SMS** via Android Gateway or SMTP methods

## 🔐 Access Methods

### User Interface
- **Main App**: Your Replit preview URL
- **Login**: Use API key provided by admin

### Admin Panel (Hidden)
- **URL**: Add `/lekzy-admin-panel-secret` to your main URL
- **Login**: `admin` / `LekzyTTP@2025`

## ✨ Features

### SMS Sending
- **Android SMS Gateway** - Direct SIM card sending
- **SMTP SMS** - Email-to-SMS via carriers (Verizon, AT&T, T-Mobile, etc.)
- **Batch messaging** - Send to multiple numbers at once
- **Delivery tracking** - Real-time success/failure logs

### Admin Features
- **API Key Management** - Generate keys with custom expiration
- **User Dashboard** - View all users and activity
- **SMS Statistics** - Track total messages sent
- **Activity Monitoring** - Real-time SMS logs

### Security
- **API Key Authentication** - Secure user access
- **Hidden Admin Panel** - No public links to admin features
- **Session Management** - Automatic logout after inactivity
- **Database Logging** - All activities tracked

## 🤖 Telegram Bot (Optional)

The system includes a Telegram bot for API key management:
- Generate new API keys
- List active keys
- Check key validity
- Revoke keys

## 🛠️ Technical Stack

- **Backend**: Python Flask + PostgreSQL
- **Authentication**: API key-based with database storage
- **Deployment**: Optimized for Replit hosting
- **Real-time logging**: Database + file-based tracking

## 📞 Support

For API keys or technical support, contact your system administrator.

---

**Ready for production use on Replit! 🎯**