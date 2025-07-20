# 🥷🏿 Lekzy-TTP SMS Sender 🥷🏿

[![Deploy to Railway](https://railway.app/button.svg)](https://railway.app)

## 🚀 Elite SMS Sending Platform

A comprehensive Flask-based SMS sender with advanced user management, admin dashboard, and multi-platform messaging capabilities.

### ⚡ Features

- **🔐 Advanced Authentication**: API key-based system with PostgreSQL storage
- **📱 Dual SMS Methods**: Android Gateway + SMTP-to-SMS support
- **👑 Admin Dashboard**: Hidden panel at `/ttpadmin` with full user management
- **📊 Real-time Analytics**: User statistics, SMS tracking, activity monitoring
- **🗑️ Complete Delete System**: Remove users, API keys, and SMS logs permanently
- **🥷🏿 Ninja Branding**: Custom dark theme with ninja styling
- **📱 Responsive Design**: Perfect on phone, tablet, and desktop
- **💰 Smart Advertising**: "💲 Premium tulz and services" popup (once per hour)

### 🎯 Admin Features

- **User Management**: Generate, revoke, extend, and permanently delete API keys
- **SMS Log Control**: Delete individual logs, clear all logs, or remove old logs (30+ days)
- **CSV Export**: Download complete user database
- **Password Security**: Change admin credentials securely
- **Real-time Stats**: Live user counts and SMS statistics

### 🔧 Quick Deploy

#### Railway Deployment (Recommended)
1. Fork this repository
2. Connect to Railway
3. Add PostgreSQL database
4. Set environment variables:
   ```
   SECRET_KEY=your-secret-key
   ADMIN_PASSWORD=LekzyTTP@3681
   DEFAULT_API_KEY=your-default-key
   ```
5. Deploy automatically

#### Local Development
```bash
git clone https://github.com/yourusername/lekzy-ttp-sms-sender.git
cd lekzy-ttp-sms-sender
pip install -r requirements.txt
export DATABASE_URL=postgresql://localhost/lekzy_sms
python app.py
```

### 🎮 Usage

#### User Access
- Visit the application URL
- Enter your API key (starts with "Lekzy-TTP-")
- Choose SMS method: Android Gateway or SMTP
- Configure settings and send messages

#### Admin Access
- Go to `/ttpadmin` (hidden URL)
- Login: `LekzyTTP` / `LekzyTTP@3681`
- Manage users and monitor activity

### 🏗️ Architecture

```
📁 Project Structure
├── app.py              # Main Flask application
├── models.py           # Database models and managers
├── templates/          # HTML templates
├── static/            # CSS and JS files
├── carriers.json      # SMTP carrier domains
├── api_keys.json      # Backup key storage
├── migrate_keys.py    # JSON to PostgreSQL migration
└── telegram_bot.py    # Telegram integration
```

### 🔐 Security

- Environment-based secrets (no hardcoded passwords)
- Secure password hashing with bcrypt
- API key validation and expiration
- Admin session management
- Database connection error handling

### 📞 Support

- **Telegram**: @Lekzy_ttp
- **Quote**: "What's so ever it's GOD is Capable and Greater"

### ⚖️ License

Private project - All rights reserved

---

**Built with 🥷🏿 by Lekzy-TTP** | *Elite tools for elite users*