# 🌐 Custom Domain Setup Guide - LekzyTTP SMS Sender

## 🎯 Your Current Railway Setup
Based on your screenshot:
- Current URL: `lekzyttp-sms-sender-production.up.railway.app`
- Port: 8080 (needs to be 5000 for your Flask app)
- Ready to add custom domain

## 🏆 **RECOMMENDED DOMAIN OPTIONS**

### Professional SMS Business Domains:
1. **lekzyttp-sms.com** - Short and professional
2. **lekzysms.com** - Brandable and memorable
3. **ttp-sms.com** - Clean business name
4. **lekzytools.com** - Expandable for future tools
5. **smslekzy.com** - SMS-focused branding

### Premium Brand Extensions:
- `.com` - Most trusted and professional
- `.io` - Tech-focused, modern
- `.app` - Perfect for applications
- `.pro` - Professional services
- `.biz` - Business-oriented

## 🛒 **WHERE TO BUY YOUR DOMAIN**

### 🏆 Top Recommended Registrars:

1. **NAMECHEAP** (Best Value)
   - Website: namecheap.com
   - .com domains: $8.88/year first year
   - Free privacy protection
   - Easy DNS management
   - Rating: ⭐⭐⭐⭐⭐

2. **CLOUDFLARE** (Best Performance)
   - Website: cloudflare.com/products/registrar
   - At-cost pricing (no markup)
   - Free SSL certificates
   - Built-in CDN and security
   - Rating: ⭐⭐⭐⭐⭐

3. **GOOGLE DOMAINS** (Simple Setup)
   - Website: domains.google.com
   - Clean interface
   - Google integration
   - Reliable DNS
   - Rating: ⭐⭐⭐⭐

4. **GODADDY** (Popular Choice)
   - Website: godaddy.com
   - Frequent promotions
   - 24/7 support
   - Many extensions available
   - Rating: ⭐⭐⭐⭐

## 📋 **STEP-BY-STEP CUSTOM DOMAIN SETUP**

### Step 1: Buy Your Domain
1. Choose registrar (recommend Namecheap or Cloudflare)
2. Search for your desired domain
3. Add to cart with privacy protection
4. Complete purchase
5. Verify email and activate domain

### Step 2: Fix Railway Port Configuration
Your app needs to run on port 5000, not 8080:

**Update your Railway deployment:**
1. Go to Railway project settings
2. Environment Variables → Add:
   ```
   PORT=5000
   ```
3. Redeploy your application

**Fix in your code (if needed):**
```python
# In app.py, ensure it uses PORT from environment
import os
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
```

### Step 3: Configure DNS Settings
In your domain registrar's DNS panel:

**Add these DNS records:**
```
Type: A
Name: @
Value: [Railway IP - get from Railway settings]
TTL: 300

Type: CNAME  
Name: www
Value: lekzyttp-sms-sender-production.up.railway.app
TTL: 300
```

### Step 4: Add Domain to Railway
1. In Railway dashboard → Settings → Domains
2. Click "Add Custom Domain"
3. Enter your domain: `yourdomain.com`
4. Set port to: `5000` (not 8080!)
5. Click "Add Domain"

### Step 5: SSL Certificate Setup
Railway will automatically:
- Generate SSL certificate
- Enable HTTPS
- Redirect HTTP to HTTPS
- Update in 5-10 minutes

## 🚀 **ALTERNATIVE HOSTING OPTIONS**

If you want complete control without Railway branding:

### Option 1: DigitalOcean App Platform
- Custom domains included
- $5/month
- No platform branding
- Professional deployment

### Option 2: Heroku Custom Domain
- Custom domains available
- Free SSL certificates  
- No Heroku branding on custom domain
- $7/month for hobby plan

### Option 3: VPS + Nginx
- Complete control
- Your own server
- Custom everything
- $5-20/month depending on provider

### Option 4: Cloudflare Pages + Workers
- Free custom domain hosting
- Global CDN
- Serverless backend
- Professional setup

## 🎨 **DOMAIN SUGGESTIONS FOR LEKZYTTP**

### Short & Memorable:
- `lekzysms.com` ⭐⭐⭐⭐⭐
- `ttpsms.com` ⭐⭐⭐⭐⭐
- `lekzytools.com` ⭐⭐⭐⭐
- `ttptools.com` ⭐⭐⭐⭐

### Professional Business:
- `lekzyttp-solutions.com` ⭐⭐⭐⭐
- `lekzy-communications.com` ⭐⭐⭐
- `ttp-messaging.com` ⭐⭐⭐⭐

### Tech-Focused:
- `lekzysms.io` ⭐⭐⭐⭐⭐
- `ttpsms.app` ⭐⭐⭐⭐⭐
- `lekzytools.dev` ⭐⭐⭐⭐

### Brand Extensions:
- `lekzyttp.pro` ⭐⭐⭐⭐
- `sms-lekzy.biz` ⭐⭐⭐
- `lekzyttp.tech` ⭐⭐⭐⭐

## 🔧 **TECHNICAL REQUIREMENTS**

### DNS Configuration:
```
A Record: @ → Railway IP
CNAME: www → your-app.up.railway.app
```

### Railway App Settings:
```
PORT=5000
DOMAIN=yourdomain.com
FORCE_HTTPS=true
```

### SSL Certificate:
- Automatically provided by Railway
- Let's Encrypt certificates
- Auto-renewal enabled
- HTTPS redirect configured

## ⚡ **QUICK SETUP CHECKLIST**

### Pre-Setup:
- [ ] Choose domain name
- [ ] Select registrar
- [ ] Budget: $10-15/year for domain

### Purchase Domain:
- [ ] Buy domain with privacy protection
- [ ] Verify email confirmation
- [ ] Access DNS management panel

### Railway Configuration:
- [ ] Fix port to 5000 (currently 8080)
- [ ] Add environment variable PORT=5000  
- [ ] Redeploy application
- [ ] Test app works on Railway URL

### Domain Connection:
- [ ] Add A record pointing to Railway IP
- [ ] Add CNAME for www subdomain
- [ ] Add custom domain in Railway settings
- [ ] Wait for SSL certificate (5-10 minutes)
- [ ] Test your custom domain works

### Final Verification:
- [ ] https://yourdomain.com loads your app
- [ ] SSL certificate shows green lock
- [ ] All features work (login, SMS, admin)
- [ ] No Railway branding visible

## 💡 **PRO TIPS**

### Domain Selection:
- Keep it short and memorable
- Avoid hyphens if possible
- .com is most trusted
- Check social media availability

### Performance Optimization:
- Use Cloudflare for DNS (fast global DNS)
- Enable Cloudflare CDN for speed
- Set up email forwarding
- Monitor uptime with UptimeRobot

### SEO Considerations:
- Choose brandable domain
- Set up Google Search Console
- Create Google Analytics account
- Optimize for search engines

### Security Best Practices:
- Enable domain privacy protection
- Use strong registrar password
- Enable 2FA on registrar account
- Monitor domain expiration dates

## 🎯 **RECOMMENDED COMPLETE SETUP**

### Best Value Option:
1. **Domain**: `lekzysms.com` from Namecheap ($8.88)
2. **Hosting**: Keep Railway (free/cheap)
3. **DNS**: Cloudflare (free) 
4. **SSL**: Railway auto-SSL (free)
5. **Total**: ~$9/year

### Premium Professional Setup:
1. **Domain**: `lekzytools.com` from Cloudflare
2. **Hosting**: DigitalOcean App Platform ($5/month)
3. **DNS**: Cloudflare with CDN
4. **SSL**: Auto-managed
5. **Monitoring**: UptimeRobot alerts
6. **Total**: ~$70/year

## 📞 **SUPPORT RESOURCES**

### Domain Help:
- Namecheap support: 24/7 chat
- Cloudflare docs: developers.cloudflare.com
- Railway docs: docs.railway.app

### DNS Tools:
- DNS Checker: dnschecker.org
- SSL Test: ssllabs.com/ssltest
- Website Speed: gtmetrix.com

Your LekzyTTP SMS Sender will look completely professional with your own custom domain - no Railway branding anywhere!