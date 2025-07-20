# Android SMS Gateway Compatible Devices & USA Carrier Guide

## 📱 Android Devices That Work for SMS Gateway

### Recommended Android Phones (USA Compatible):
1. **Samsung Galaxy Series**
   - Galaxy S21, S22, S23, S24 (all variants)
   - Galaxy Note 20, Note 21
   - Galaxy A53, A54, A73
   - Galaxy Z Fold/Flip series

2. **Google Pixel Series**
   - Pixel 6, 6 Pro, 6a
   - Pixel 7, 7 Pro, 7a
   - Pixel 8, 8 Pro, 8a
   - Pixel 9 series

3. **OnePlus Devices**
   - OnePlus 9, 9 Pro, 9RT
   - OnePlus 10, 10 Pro, 10T
   - OnePlus 11, 12 series
   - OnePlus Nord series

4. **Motorola**
   - Moto G Power, G Stylus
   - Moto Edge series
   - Motorola One series

5. **LG (Older Models)**
   - LG V60, V50
   - LG G8, G7
   - LG Wing, Velvet

### Requirements for SMS Gateway:
- **Android 8.0+** (API level 26 or higher)
- **Active SIM card** with SMS plan
- **WiFi or Mobile Data** connection
- **SMS Gateway App** installed (like SMS Gateway API)
- **Allow unknown sources** for app installation
- **Disable battery optimization** for the gateway app

---

## 🇺🇸 USA SIM Cards & Carriers for SMS Gateway

### Major Carriers (Postpaid):
1. **Verizon**
   - Plans: Unlimited, Play More, Do More, Get More
   - SMS: Unlimited domestic SMS
   - International: $5-12/month add-ons

2. **AT&T**
   - Plans: Unlimited Starter, Extra, Elite
   - SMS: Unlimited domestic SMS
   - International: $10/month add-on

3. **T-Mobile**
   - Plans: Essentials, Magenta, Magenta MAX
   - SMS: Unlimited domestic SMS
   - International: $15/month add-on

4. **Sprint (now T-Mobile)**
   - Legacy plans still supported
   - Unlimited SMS included

### Budget Carriers (Prepaid):
1. **Metro by T-Mobile**
   - $30-60/month unlimited plans
   - Unlimited SMS included

2. **Cricket (AT&T Network)**
   - $30-60/month unlimited plans
   - Unlimited SMS included

3. **Boost Mobile**
   - $25-50/month plans
   - Unlimited SMS included

4. **Mint Mobile**
   - $15-30/month plans (bulk purchase)
   - Unlimited SMS included

5. **Visible (Verizon Network)**
   - $30/month unlimited everything
   - Unlimited SMS included

### MVNOs (Mobile Virtual Network Operators):
1. **Google Fi**
   - $20/month + usage or unlimited plans
   - International SMS included

2. **Xfinity Mobile**
   - Verizon network
   - Unlimited plans available

3. **US Mobile**
   - Verizon/T-Mobile networks
   - Flexible plans

---

## 📧 SMTP Servers Supported for SMS Gateway

### Gmail (Google)
- **SMTP Server**: smtp.gmail.com
- **Port**: 587 (TLS) or 465 (SSL)
- **Authentication**: App Password required
- **Daily Limit**: 500 emails/day

### Outlook/Hotmail (Microsoft)
- **SMTP Server**: smtp-mail.outlook.com
- **Port**: 587 (TLS)
- **Authentication**: Regular password or App Password
- **Daily Limit**: 300 emails/day

### Yahoo Mail
- **SMTP Server**: smtp.mail.yahoo.com
- **Port**: 587 (TLS) or 465 (SSL)
- **Authentication**: App Password required
- **Daily Limit**: 500 emails/day

### Apple iCloud
- **SMTP Server**: smtp.mail.me.com
- **Port**: 587 (TLS)
- **Authentication**: App Password required
- **Daily Limit**: 200 emails/day

### ProtonMail
- **SMTP Server**: 127.0.0.1 (Bridge required)
- **Port**: 1025
- **Authentication**: Bridge setup needed
- **Daily Limit**: Based on plan

### Zoho Mail
- **SMTP Server**: smtp.zoho.com
- **Port**: 587 (TLS) or 465 (SSL)
- **Authentication**: Regular password
- **Daily Limit**: 250 emails/day (free), higher for paid

### SendGrid (Professional)
- **SMTP Server**: smtp.sendgrid.net
- **Port**: 587
- **Authentication**: API key
- **Daily Limit**: 100 emails/day (free), unlimited paid

### Mailgun (Professional)
- **SMTP Server**: smtp.mailgun.org
- **Port**: 587 or 2525
- **Authentication**: Domain credentials
- **Daily Limit**: Based on plan

---

## 🔧 SMS Gateway App Setup

### Recommended Apps:
1. **SMS Gateway API**
   - GitHub: android-sms-gateway
   - Free and open source
   - RESTful API interface

2. **SMS Forwarding**
   - Play Store available
   - Forward SMS to webhook/API

3. **SMS to URL**
   - Forward SMS to web endpoints
   - Webhook support

### Setup Steps:
1. Install SMS Gateway app on Android device
2. Grant SMS and Phone permissions
3. Configure API settings (port, password)
4. Disable battery optimization for the app
5. Keep device connected to power and WiFi
6. Test API endpoint from your SMS sender

---

## 📋 USA Carrier Email-to-SMS Domains

Your app already supports these major carriers:

- **Verizon**: @vtext.com
- **AT&T**: @txt.att.net
- **T-Mobile**: @tmomail.net
- **Sprint**: @messaging.sprintpcs.com
- **Cricket**: @sms.cricketwireless.net
- **Metro**: @mymetropcs.com
- **Boost**: @smsmyboostmobile.com
- **US Cellular**: @email.uscc.net

### International Options:
- **Bell (Canada)**: @txt.bell.ca
- **Rogers (Canada)**: @pcs.rogers.com
- **Telus (Canada)**: @msg.telus.com

---

## ⚠️ Important Notes:

### For Android Gateway:
- Keep device plugged in and connected
- Some carriers may block automated SMS
- Test with small batches first
- Monitor for carrier restrictions

### For SMTP Method:
- Use app-specific passwords
- Stay within daily limits
- Some carriers block email-to-SMS
- Test delivery rates regularly

### Legal Compliance:
- Follow CAN-SPAM Act rules
- Get consent for commercial messages
- Include opt-out options
- Respect carrier terms of service

---

This setup gives you maximum flexibility with both Android gateway and SMTP methods for reliable SMS delivery in the USA market.