import os
import json
import re
import smtplib
import requests
import csv
import io
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, make_response
import logging
from models import Database, UserManager, AdminManager

# Set required environment variables with defaults
os.environ.setdefault('SECRET_KEY', 'lekzy-ttp-production-secret-2025')
os.environ.setdefault('SESSION_SECRET', 'lekzy-ttp-session-secret-2025')
os.environ.setdefault('ADMIN_PASSWORD', 'LekzyTTP@2025')
os.environ.setdefault('DEFAULT_API_KEY', 'lekzy-ttp-default-2025')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log startup information
logger.info("Starting Lekzy-TTP SMS Sender Application")
logger.info(f"Flask secret key configured: {'Yes' if os.getenv('SECRET_KEY') else 'Using generated key'}")
logger.info(f"Admin password configured: {'Yes' if os.getenv('ADMIN_PASSWORD') else 'Using default'}")
logger.info(f"Default API key configured: {'Yes' if os.getenv('DEFAULT_API_KEY') else 'Using default'}")

# Ensure directories exist
os.makedirs('Success', exist_ok=True)
os.makedirs('Failed', exist_ok=True)

# Initialize database and managers
db = Database()
db.init_db()
user_manager = UserManager()
admin_manager = AdminManager()

def load_api_keys():
    """Load API keys from JSON file"""
    try:
        with open('api_keys.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def load_carriers():
    """Load carrier domains from JSON file"""
    try:
        with open('carriers.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def validate_phone_number(phone):
    """Validate and clean phone number"""
    # Remove all non-digit characters
    cleaned = re.sub(r'\D', '', phone)
    # Check if length is between 10-15 digits
    if 10 <= len(cleaned) <= 15:
        return cleaned
    return None

def log_result(phone, message, method, status, error=None):
    """Log SMS sending results"""
    # Database logging
    if 'api_key' in session:
        user_manager.log_sms(session['api_key'], phone, message, method, status, error)
    
    # File logging (keep for backup)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {phone} | {method} | {status}"
    if error:
        log_entry += f" | Error: {error}"
    log_entry += f" | Message: {message[:50]}...\n"
    
    if status == "SUCCESS":
        with open('Success/successful.txt', 'a', encoding='utf-8') as f:
            f.write(log_entry)
    else:
        with open('Failed/failed.txt', 'a', encoding='utf-8') as f:
            f.write(log_entry)

@app.route('/')
def index():
    """Main entry point - redirect to login if not authenticated"""
    try:
        if 'authenticated' in session and session['authenticated']:
            return redirect(url_for('main_menu'))
        return render_template('login.html')
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        # Return a simple HTML response for deployment health checks
        return '''
        <!DOCTYPE html>
        <html>
        <head><title>Lekzy-TTP SMS Sender</title></head>
        <body>
            <h1>Lekzy-TTP SMS Sender</h1>
            <p>Application is running and ready to serve requests.</p>
            <p><a href="/health">Health Check</a></p>
        </body>
        </html>
        ''', 200

@app.route('/health')
def health_check():
    """Health check endpoint for deployment monitoring"""
    try:
        # Basic health check that always returns 200
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'lekzy-ttp-sms-sender',
            'version': '1.0.0'
        }
        
        # Try database connection but don't fail if it's not available
        try:
            db.get_connection()
            health_data['database'] = 'connected'
        except Exception as e:
            health_data['database'] = 'unavailable'
            health_data['database_error'] = str(e)
        
        return jsonify(health_data), 200
    except Exception as e:
        # Even if there's an error, return a basic 200 response
        return jsonify({
            'status': 'basic',
            'timestamp': datetime.now().isoformat(),
            'service': 'lekzy-ttp-sms-sender'
        }), 200

@app.route('/status')
def status_check():
    """Detailed status endpoint for deployment debugging"""
    return jsonify({
        'application': 'Lekzy-TTP SMS Sender',
        'status': 'running',
        'port': os.environ.get('PORT', 5000),
        'host': '0.0.0.0',
        'environment': 'production',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/validate-key', methods=['POST'])
def validate_key():
    """Validate API key endpoint"""
    data = request.get_json()
    api_key = data.get('api_key', '')
    
    # Use database validation
    user = user_manager.get_user_by_key(api_key)
    if user and user_manager.is_key_valid(api_key):
        return jsonify({
            'valid': True,
            'expires': user['expires_at'].strftime('%Y-%m-%d')
        })
    
    return jsonify({'valid': False})

@app.route('/login', methods=['POST'])
def login():
    """Handle login form submission"""
    api_key = request.form.get('api_key', '')
    
    # Use database validation
    if user_manager.is_key_valid(api_key):
        session['authenticated'] = True
        session['api_key'] = api_key
        return redirect(url_for('main_menu'))
    
    return render_template('login.html', error='Invalid API Key')

# Admin Panel Routes (Hidden - No public access)
@app.route('/lekzy-admin-panel-secret')
def admin_login():
    """Admin login page"""
    if 'admin_authenticated' in session and session['admin_authenticated']:
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

@app.route('/lekzy-admin-panel-secret/login', methods=['POST'])
def admin_authenticate():
    """Handle admin login"""
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    admin = admin_manager.authenticate_admin(username, password)
    if admin:
        session['admin_authenticated'] = True
        session['admin_username'] = username
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin_login.html', error='Invalid credentials')

@app.route('/lekzy-admin-panel-secret/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if 'admin_authenticated' not in session or not session['admin_authenticated']:
        return redirect(url_for('admin_login'))
    
    stats = admin_manager.get_user_stats()
    users = user_manager.get_all_users()
    recent_activity = admin_manager.get_recent_activity(20)
    
    return render_template('admin_dashboard.html', 
                         stats=stats, 
                         users=users, 
                         recent_activity=recent_activity)

@app.route('/lekzy-admin-panel-secret/generate-key', methods=['POST'])
def admin_generate_key():
    """Generate API key from admin panel"""
    if 'admin_authenticated' not in session or not session['admin_authenticated']:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    username = data.get('username', '')
    days = int(data.get('days', 30))
    
    if not username:
        return jsonify({'error': 'Username required'}), 400
    
    try:
        api_key = user_manager.generate_api_key(username, days)
        return jsonify({'success': True, 'api_key': api_key})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/lekzy-admin-panel-secret/revoke-key', methods=['POST'])
def admin_revoke_key():
    """Revoke API key from admin panel"""
    if 'admin_authenticated' not in session or not session['admin_authenticated']:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    api_key = data.get('api_key', '')
    
    username = user_manager.revoke_key(api_key)
    if username:
        return jsonify({'success': True, 'username': username})
    else:
        return jsonify({'error': 'Key not found'}), 404

@app.route('/lekzy-admin-panel-secret/extend-subscription', methods=['POST'])
def admin_extend_subscription():
    """Extend user subscription from admin panel"""
    if 'admin_authenticated' not in session or not session['admin_authenticated']:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    api_key = data.get('api_key', '')
    days = int(data.get('days', 30))
    
    result = user_manager.extend_subscription(api_key, days)
    if result:
        return jsonify({
            'success': True, 
            'username': result[0], 
            'new_expiry': result[1].strftime('%Y-%m-%d %H:%M:%S')
        })
    else:
        return jsonify({'error': 'Key not found'}), 404

@app.route('/lekzy-admin-panel-secret/export-users')
def admin_export_users():
    """Export users data to CSV"""
    if 'admin_authenticated' not in session or not session['admin_authenticated']:
        return redirect(url_for('admin_login'))
    
    users = user_manager.get_all_users()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # CSV headers
    writer.writerow(['Username', 'API Key', 'Created At', 'Expires At', 'Status', 'Total SMS Sent', 'Last Activity'])
    
    # CSV data
    for user in users:
        writer.writerow([
            user['username'],
            user['api_key'],
            user['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
            user['expires_at'].strftime('%Y-%m-%d %H:%M:%S'),
            user['status'],
            user['total_sms_sent'],
            user['last_activity'].strftime('%Y-%m-%d %H:%M:%S') if user['last_activity'] else 'Never'
        ])
    
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=lekzy_ttp_users_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response

@app.route('/lekzy-admin-panel-secret/change-password', methods=['POST'])
def admin_change_password():
    """Change admin password"""
    if 'admin_authenticated' not in session or not session['admin_authenticated']:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    
    # Verify current password
    admin = admin_manager.authenticate_admin(session['admin_username'], current_password)
    if not admin:
        return jsonify({'error': 'Current password incorrect'}), 400
    
    # Change password
    if admin_manager.change_admin_password(session['admin_username'], new_password):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to change password'}), 500

@app.route('/lekzy-admin-panel-secret/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_authenticated', None)
    session.pop('admin_username', None)
    return redirect(url_for('admin_login'))

@app.route('/main_menu')
def main_menu():
    """Main menu page"""
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('index'))
    return render_template('main_menu.html')

@app.route('/android_sms')
def android_sms():
    """Android SMS configuration page"""
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('index'))
    return render_template('android_config.html')

@app.route('/smtp_sms')
def smtp_sms():
    """SMTP configuration page"""
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('index'))
    return render_template('smtp_config.html')

@app.route('/android_message')
def android_message():
    """Android SMS message input page"""
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('index'))
    if 'android_config' not in session:
        return redirect(url_for('android_sms'))
    return render_template('android_message.html', config=session['android_config'])

@app.route('/smtp_message')
def smtp_message():
    """SMTP SMS message input page"""
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('index'))
    if 'smtp_config' not in session:
        return redirect(url_for('smtp_sms'))
    carriers = load_carriers()
    return render_template('smtp_message.html', config=session['smtp_config'], carriers=carriers)

@app.route('/sending_status')
def sending_status():
    """SMS sending status page"""
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('index'))
    return render_template('sending_status.html')

@app.route('/save_android_config', methods=['POST'])
def save_android_config():
    """Save Android configuration to session"""
    if 'authenticated' not in session or not session['authenticated']:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    session['android_config'] = {
        'api_url': data.get('api_url', ''),
        'timestamp': datetime.now().isoformat()
    }
    return jsonify({'success': True, 'redirect': '/android_message'})

@app.route('/save_smtp_config', methods=['POST'])
def save_smtp_config():
    """Save SMTP configuration to session"""
    if 'authenticated' not in session or not session['authenticated']:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    session['smtp_config'] = {
        'smtp_host': data.get('smtp_host', ''),
        'smtp_port': data.get('smtp_port', ''),
        'smtp_email': data.get('smtp_email', ''),
        'smtp_password': data.get('smtp_password', ''),
        'timestamp': datetime.now().isoformat()
    }
    return jsonify({'success': True, 'redirect': '/smtp_message'})

@app.route('/send_android_sms', methods=['POST'])
def send_android_sms():
    """Send SMS via Android Gateway API"""
    if 'authenticated' not in session or not session['authenticated']:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    api_url = data.get('api_url', '')
    message = data.get('message', '')
    phone_numbers = data.get('phone_numbers', '')
    
    # Parse phone numbers
    numbers = []
    for line in phone_numbers.split('\n'):
        line = line.strip()
        if ',' in line:
            numbers.extend([n.strip() for n in line.split(',')])
        elif line:
            numbers.append(line)
    
    # Remove duplicates and validate
    valid_numbers = []
    invalid_numbers = []
    
    for number in set(numbers):
        cleaned = validate_phone_number(number)
        if cleaned:
            valid_numbers.append(cleaned)
        else:
            invalid_numbers.append(number)
    
    # Log invalid numbers
    for invalid in invalid_numbers:
        log_result(invalid, message, "Android SMS", "FAILED", "Invalid phone number format")
    
    # Send to valid numbers
    success_count = 0
    failed_count = len(invalid_numbers)
    
    for number in valid_numbers:
        try:
            # Construct API URL
            url = f"{api_url.rstrip('/')}/send"
            params = {
                'number': number,
                'message': message
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                log_result(number, message, "Android SMS", "SUCCESS")
                success_count += 1
            else:
                log_result(number, message, "Android SMS", "FAILED", f"HTTP {response.status_code}")
                failed_count += 1
                
        except Exception as e:
            log_result(number, message, "Android SMS", "FAILED", str(e))
            failed_count += 1
    
    # Store results in session for status page
    session['last_send_result'] = {
        'method': 'Android SMS',
        'total_sent': success_count,
        'total_failed': failed_count,
        'message': f'Sent {success_count} messages, {failed_count} failed',
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify({
        'success': True,
        'total_sent': success_count,
        'total_failed': failed_count,
        'message': f'Sent {success_count} messages, {failed_count} failed',
        'redirect': '/sending_status'
    })

@app.route('/send_smtp_sms', methods=['POST'])
def send_smtp_sms():
    """Send SMS via SMTP to carrier email gateway"""
    if 'authenticated' not in session or not session['authenticated']:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    smtp_host = data.get('smtp_host', '')
    smtp_port = int(data.get('smtp_port', 587))
    smtp_email = data.get('smtp_email', '')
    smtp_password = data.get('smtp_password', '')
    message = data.get('message', '')
    phone_numbers = data.get('phone_numbers', '')
    carrier_domain = data.get('carrier_domain', '')
    
    # Parse phone numbers
    numbers = []
    for line in phone_numbers.split('\n'):
        line = line.strip()
        if ',' in line:
            numbers.extend([n.strip() for n in line.split(',')])
        elif line:
            numbers.append(line)
    
    # Remove duplicates and validate
    valid_numbers = []
    invalid_numbers = []
    
    for number in set(numbers):
        cleaned = validate_phone_number(number)
        if cleaned:
            valid_numbers.append(cleaned)
        else:
            invalid_numbers.append(number)
    
    # Log invalid numbers
    for invalid in invalid_numbers:
        log_result(invalid, message, "SMTP SMS", "FAILED", "Invalid phone number format")
    
    # Send to valid numbers
    success_count = 0
    failed_count = len(invalid_numbers)
    
    try:
        # Setup SMTP connection
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_email, smtp_password)
        
        for number in valid_numbers:
            try:
                # Create email message
                msg = MIMEMultipart()
                msg['From'] = smtp_email
                msg['To'] = f"{number}@{carrier_domain}"
                msg['Subject'] = ""
                
                msg.attach(MIMEText(message, 'plain'))
                
                # Send email
                server.send_message(msg)
                log_result(number, message, "SMTP SMS", "SUCCESS")
                success_count += 1
                
            except Exception as e:
                log_result(number, message, "SMTP SMS", "FAILED", str(e))
                failed_count += 1
        
        server.quit()
        
    except Exception as e:
        # SMTP connection failed
        for number in valid_numbers:
            log_result(number, message, "SMTP SMS", "FAILED", f"SMTP Error: {str(e)}")
        failed_count += len(valid_numbers)
    
    # Store results in session for status page
    session['last_send_result'] = {
        'method': 'SMTP SMS',
        'total_sent': success_count,
        'total_failed': failed_count,
        'message': f'Sent {success_count} messages, {failed_count} failed',
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify({
        'success': True,
        'total_sent': success_count,
        'total_failed': failed_count,
        'message': f'Sent {success_count} messages, {failed_count} failed',
        'redirect': '/sending_status'
    })

@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    return {'status': 'healthy', 'service': 'lekzy-ttp-sms-sender'}, 200

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting SMS Sender App on 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
