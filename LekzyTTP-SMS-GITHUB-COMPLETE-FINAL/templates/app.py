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
os.environ.setdefault('ADMIN_PASSWORD', 'LekzyTTP@3681')
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

# Initialize database and managers with error handling
try:
    db = Database()
    db.init_db()
    user_manager = UserManager()
    admin_manager = AdminManager()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Database initialization failed: {str(e)}")
    # Try to create managers anyway - they will handle connection issues
    try:
        user_manager = UserManager()
        admin_manager = AdminManager()
        logger.info("Managers created despite initialization error")
    except Exception as e2:
        logger.error(f"Manager creation failed: {str(e2)}")
        user_manager = None
        admin_manager = None

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
    if 'api_key' in session and user_manager is not None:
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
    
    try:
        # Ensure user_manager is available
        global user_manager
        if user_manager is None:
            from models import UserManager
            user_manager = UserManager()
        
        # Use database validation
        user = user_manager.get_user_by_key(api_key)
        if user and user_manager.is_key_valid(api_key):
            return jsonify({
                'valid': True,
                'expires': user['expires_at'].strftime('%Y-%m-%d')
            })
        
        return jsonify({'valid': False})
    except Exception as e:
        logger.error(f"Key validation error: {str(e)}")
        return jsonify({'valid': False})

@app.route('/login', methods=['POST'])
def login():
    """Handle login form submission"""
    api_key = request.form.get('api_key', '')
    
    try:
        # Ensure user_manager is available
        global user_manager
        if user_manager is None:
            from models import UserManager
            user_manager = UserManager()
        
        # Use database validation
        if user_manager.is_key_valid(api_key):
            session['authenticated'] = True
            session['api_key'] = api_key
            return redirect(url_for('main_menu'))
        
        return render_template('login.html', error='Invalid API Key')
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return render_template('login.html', error='System error - please try again')

# Admin Panel Routes (Hidden - No public access)
@app.route('/ttpadmin')
def admin_login():
    """Admin login page"""
    if 'admin_authenticated' in session and session['admin_authenticated']:
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

@app.route('/ttpadmin/login', methods=['POST'])
def admin_authenticate():
    """Handle admin login"""
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    try:
        # Force create admin_manager if None
        global admin_manager
        if admin_manager is None:
            from models import AdminManager
            admin_manager = AdminManager()
        
        admin = admin_manager.authenticate_admin(username, password)
        if admin:
            session['admin_authenticated'] = True
            session['admin_username'] = username
            return redirect(url_for('admin_dashboard'))
        
        return render_template('admin_login.html', error='Invalid credentials - Check username/password')
    except Exception as e:
        logger.error(f"Admin authentication error: {str(e)}")
        # Try to reinitialize database
        try:
            from models import Database
            db = Database()
            db.initialize_database()
            return render_template('admin_login.html', error='Database reinitialized - Please try again')
        except:
            return render_template('admin_login.html', error=f'Database error: {str(e)}')

@app.route('/ttpadmin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if 'admin_authenticated' not in session or not session['admin_authenticated']:
        return redirect(url_for('admin_login'))
    
    try:
        # Force initialize managers if None
        global admin_manager, user_manager
        if admin_manager is None:
            from models import AdminManager
            admin_manager = AdminManager()
        if user_manager is None:
            from models import UserManager
            user_manager = UserManager()
        
        stats = admin_manager.get_user_stats()
        users = user_manager.get_all_users()
        recent_activity = admin_manager.get_recent_activity(20)
        
        return render_template('admin_dashboard.html', 
                             stats=stats, 
                             users=users, 
                             recent_activity=recent_activity)
    except Exception as e:
        logger.error(f"Admin dashboard error: {str(e)}")
        return f"Database connection error: {str(e)}<br><br>Check that Railway PostgreSQL is connected and DATABASE_URL variable is set correctly.", 500

@app.route('/ttpadmin/generate-key', methods=['POST'])
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

@app.route('/ttpadmin/revoke-key', methods=['POST'])
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

@app.route('/ttpadmin/delete-key', methods=['POST'])
def admin_delete_key():
    """Permanently delete API key and user from database"""
    if 'admin_authenticated' not in session or not session['admin_authenticated']:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    api_key = data.get('api_key', '')
    
    username = user_manager.delete_user_permanently(api_key)
    if username:
        return jsonify({'success': True, 'username': username})
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/ttpadmin/extend-subscription', methods=['POST'])
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

@app.route('/ttpadmin/export-users')
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

@app.route('/ttpadmin/change-password', methods=['POST'])
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

@app.route('/ttpadmin/delete-log', methods=['POST'])
def admin_delete_log():
    """Delete individual SMS log entry"""
    if 'admin_authenticated' not in session or not session['admin_authenticated']:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    log_id = data.get('log_id', '')
    
    try:
        db = Database()
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM sms_logs WHERE id = %s", (log_id,))
                if cur.rowcount > 0:
                    return jsonify({'success': True})
                else:
                    return jsonify({'error': 'Log not found'}), 404
    except Exception as e:
        logger.error(f"Delete log error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/ttpadmin/clear-all-logs', methods=['POST'])
def admin_clear_all_logs():
    """Delete all SMS logs"""
    if 'admin_authenticated' not in session or not session['admin_authenticated']:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        db = Database()
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM sms_logs")
                count = cur.fetchone()[0]
                cur.execute("DELETE FROM sms_logs")
                return jsonify({'success': True, 'deleted_count': count})
    except Exception as e:
        logger.error(f"Clear all logs error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/ttpadmin/clear-old-logs', methods=['POST'])
def admin_clear_old_logs():
    """Delete SMS logs older than 30 days"""
    if 'admin_authenticated' not in session or not session['admin_authenticated']:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        db = Database()
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM sms_logs WHERE sent_at < NOW() - INTERVAL '30 days'")
                count = cur.fetchone()[0]
                cur.execute("DELETE FROM sms_logs WHERE sent_at < NOW() - INTERVAL '30 days'")
                return jsonify({'success': True, 'deleted_count': count})
    except Exception as e:
        logger.error(f"Clear old logs error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# User Activity Management Routes
@app.route('/user-activity')
def user_activity():
    """User's personal activity page"""
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('index'))
    
    try:
        api_key = session.get('api_key')
        user = user_manager.get_user_by_key(api_key) if user_manager else None
        
        if not user:
            return render_template('user_activity.html', activities=[], user_stats={})
        
        # Get user's SMS logs
        db = Database()
        with db.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, phone_number, message, method, status, error_message, sent_at
                    FROM sms_logs 
                    WHERE user_id = %s 
                    ORDER BY sent_at DESC 
                    LIMIT 50
                """, (user['id'],))
                activities = cur.fetchall()
                
                # Get user stats
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_messages,
                        COUNT(*) FILTER (WHERE status = 'Success') as successful_messages,
                        COUNT(*) FILTER (WHERE status = 'Failed') as failed_messages
                    FROM sms_logs 
                    WHERE user_id = %s
                """, (user['id'],))
                stats = cur.fetchone()
        
        user_stats = {
            'username': user.get('username', 'User'),
            'total_messages': stats['total_messages'] if stats else 0,
            'successful_messages': stats['successful_messages'] if stats else 0,
            'failed_messages': stats['failed_messages'] if stats else 0,
            'expires_at': user.get('expires_at')
        }
        
        return render_template('user_activity.html', activities=activities, user_stats=user_stats)
        
    except Exception as e:
        logger.error(f"User activity error: {str(e)}")
        return render_template('user_activity.html', activities=[], user_stats={}, error=str(e))

@app.route('/clear-my-activity', methods=['POST'])
def clear_user_activity():
    """Allow user to clear their own SMS activity"""
    if 'authenticated' not in session or not session['authenticated']:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        api_key = session.get('api_key')
        user = user_manager.get_user_by_key(api_key) if user_manager else None
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        db = Database()
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM sms_logs WHERE user_id = %s", (user['id'],))
                count = cur.fetchone()[0]
                cur.execute("DELETE FROM sms_logs WHERE user_id = %s", (user['id'],))
                
                # Reset user's SMS count
                cur.execute("UPDATE users SET total_sms_sent = 0 WHERE id = %s", (user['id'],))
                
                return jsonify({'success': True, 'deleted_count': count})
                
    except Exception as e:
        logger.error(f"Clear user activity error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/ttpadmin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_authenticated', None)
    session.pop('admin_username', None)
    return redirect(url_for('admin_login'))

@app.route('/main_menu')
def main_menu():
    """Main menu page with user activity stats"""
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('index'))
    
    # Get user's SMS activity count for display
    try:
        api_key = session.get('api_key')
        user = user_manager.get_user_by_key(api_key) if user_manager else None
        user_sms_count = user.get('total_sms_sent', 0) if user else 0
        username = user.get('username', 'User') if user else 'User'
    except:
        user_sms_count = 0
        username = 'User'
    
    return render_template('main_menu.html', user_sms_count=user_sms_count, username=username)

@app.route('/android-config')
@app.route('/android_sms')
def android_sms():
    """Android SMS configuration page"""
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('index'))
    return render_template('android_config.html')

@app.route('/smtp-config')
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

@app.route('/android_sending')
def android_sending():
    """Android SMS sending status page"""
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('index'))
    return render_template('android_sending.html')

@app.route('/smtp_sending')
def smtp_sending():
    """SMTP SMS sending status page"""
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('index'))
    return render_template('smtp_sending.html')

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

def log_result(phone, message, method, status, error=None):
    """Log SMS sending result to both file and database"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] Phone: {phone} | Method: {method} | Status: {status}"
    if error:
        log_entry += f" | Error: {error}"
    log_entry += f" | Message: {message[:50]}..."
    
    # Database logging with user tracking
    try:
        api_key = session.get('api_key')
        if api_key and user_manager:
            user = user_manager.get_user_by_key(api_key)
            if user:
                user_id = user['id']
                
                # Log to database
                db = Database()
                with db.get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO sms_logs (user_id, phone_number, message, method, status, error_message)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (user_id, phone, message[:500], method, status, error))
                        
                        # Update user SMS count if successful
                        if status == "SUCCESS":
                            cur.execute("""
                                UPDATE users 
                                SET total_sms_sent = total_sms_sent + 1, last_activity = NOW() 
                                WHERE id = %s
                            """, (user_id,))
    except Exception as e:
        logger.error(f"Database logging error: {str(e)}")
    
    # File logging (backup)
    if status == "SUCCESS":
        try:
            with open('Success/successful.txt', 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except:
            pass
    else:
        try:
            with open('Failed/failed.txt', 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except:
            pass

def validate_phone_number(phone):
    """Validate and clean phone number"""
    # Remove all non-digit characters
    cleaned = re.sub(r'\D', '', phone)
    # Check if length is valid (10-15 digits)
    if len(cleaned) >= 10 and len(cleaned) <= 15:
        return cleaned
    return None

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
