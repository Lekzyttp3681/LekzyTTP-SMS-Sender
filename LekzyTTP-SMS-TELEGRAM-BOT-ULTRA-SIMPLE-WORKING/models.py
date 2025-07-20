import os
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta
import secrets
import string
import bcrypt

class Database:
    def __init__(self):
        # Get DATABASE_URL from Railway environment
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            # Fallback for local development
            self.database_url = 'postgresql://localhost/lekzy_sms'
        
    def get_connection(self):
        try:
            return psycopg2.connect(self.database_url)
        except Exception as e:
            print(f"Database connection error: {e}")
            raise
    
    def init_db(self):
        """Initialize database tables"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Create users table
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            username VARCHAR(100) UNIQUE NOT NULL,
                            api_key VARCHAR(100) UNIQUE NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            expires_at TIMESTAMP NOT NULL,
                            is_active BOOLEAN DEFAULT TRUE,
                            total_sms_sent INTEGER DEFAULT 0,
                            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Create admin users table
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS admin_users (
                            id SERIAL PRIMARY KEY,
                            username VARCHAR(50) UNIQUE NOT NULL,
                            password_hash VARCHAR(255) NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            last_login TIMESTAMP
                        )
                    """)
                    
                    # Create SMS logs table
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS sms_logs (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER REFERENCES users(id),
                            phone_number VARCHAR(20),
                            message TEXT,
                            method VARCHAR(20),
                            status VARCHAR(10),
                            error_message TEXT,
                            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Insert default admin user - FORCE UPDATE HASH
                    admin_password = 'LekzyTTP@3681'  # Fixed password
                    password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())
                    cur.execute("""
                        INSERT INTO admin_users (username, password_hash) 
                        VALUES (%s, %s) 
                        ON CONFLICT (username) DO UPDATE SET password_hash = EXCLUDED.password_hash
                    """, ('LekzyTTP', password_hash.decode('utf-8')))
                    
                    # Insert default API key for testing with new format
                    default_api_key = os.getenv('DEFAULT_API_KEY', 'Lekzy-TTP-123464')
                    cur.execute("""
                        INSERT INTO users (username, api_key, expires_at) 
                        VALUES (%s, %s, %s) 
                        ON CONFLICT (api_key) DO NOTHING
                    """, ('admin', default_api_key, datetime.now() + timedelta(days=365)))
                    
                    conn.commit()
                    print("Database initialized successfully with admin user and default API key")
        except Exception as e:
            print(f"Database initialization error: {e}")
            raise

class UserManager:
    def __init__(self):
        self.db = Database()
    
    def generate_api_key(self, username, days=30):
        """Generate a new API key for a user"""
        # Generate random API key with Lekzy-TTP prefix
        api_key = 'Lekzy-TTP-' + ''.join(secrets.choice(string.digits) for _ in range(6))
        expires_at = datetime.now() + timedelta(days=days)
        
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO users (username, api_key, expires_at) 
                    VALUES (%s, %s, %s)
                """, (username, api_key, expires_at))
                conn.commit()
        
        return api_key
    
    def is_key_valid(self, api_key):
        """Check if API key is valid and not expired"""
        with self.db.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT * FROM users 
                    WHERE api_key = %s AND expires_at > %s AND is_active = TRUE
                """, (api_key, datetime.now()))
                return cur.fetchone() is not None
    
    def get_user_by_key(self, api_key):
        """Get user by API key"""
        with self.db.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("SELECT * FROM users WHERE api_key = %s", (api_key,))
                return cur.fetchone()
    
    def get_all_users(self):
        """Get all users"""
        with self.db.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT *, 
                           CASE WHEN expires_at > %s THEN 'Active' ELSE 'Expired' END as status
                    FROM users ORDER BY created_at DESC
                """, (datetime.now(),))
                return cur.fetchall()
    
    def revoke_key(self, api_key):
        """Revoke an API key"""
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET is_active = FALSE WHERE api_key = %s RETURNING username", (api_key,))
                result = cur.fetchone()
                conn.commit()
                return result[0] if result else None
    
    def extend_subscription(self, api_key, days):
        """Extend user subscription"""
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE users SET expires_at = expires_at + INTERVAL '%s days' 
                    WHERE api_key = %s RETURNING username, expires_at
                """, (days, api_key))
                result = cur.fetchone()
                conn.commit()
                return result if result else None
    
    def get_active_keys(self):
        """Get all active API keys"""
        with self.db.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT api_key, username, expires_at, total_sms_sent, created_at, last_activity
                    FROM users 
                    WHERE expires_at > %s 
                    ORDER BY expires_at DESC
                """, (datetime.now(),))
                return cur.fetchall()
    
    def delete_user_permanently(self, api_key):
        """Permanently delete user and all associated data from database"""
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                # Get username before deletion
                cur.execute("SELECT username FROM users WHERE api_key = %s", (api_key,))
                user = cur.fetchone()
                if user:
                    username = user[0]
                    
                    # Delete SMS logs first (foreign key constraint)
                    cur.execute("DELETE FROM sms_logs WHERE user_id = (SELECT id FROM users WHERE api_key = %s)", (api_key,))
                    
                    # Delete user
                    cur.execute("DELETE FROM users WHERE api_key = %s", (api_key,))
                    conn.commit()
                    
                    return username
                return None

    def log_sms(self, api_key, phone, message, method, status, error=None):
        """Log SMS sending attempt"""
        user = self.get_user_by_key(api_key)
        if user:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO sms_logs (user_id, phone_number, message, method, status, error_message)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (user['id'], phone, message, method, status, error))
                    
                    if status == 'SUCCESS':
                        cur.execute("UPDATE users SET total_sms_sent = total_sms_sent + 1 WHERE id = %s", (user['id'],))
                    
                    conn.commit()

class AdminManager:
    def __init__(self):
        self.db = Database()
    
    def authenticate_admin(self, username, password):
        """Authenticate admin user"""
        with self.db.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("SELECT * FROM admin_users WHERE username = %s", (username,))
                admin = cur.fetchone()
                
                if admin and bcrypt.checkpw(password.encode('utf-8'), admin['password_hash'].encode('utf-8')):
                    # Update last login
                    cur.execute("UPDATE admin_users SET last_login = %s WHERE id = %s", (datetime.now(), admin['id']))
                    conn.commit()
                    return admin
                
                return None
    
    def get_user_stats(self):
        """Get user statistics"""
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM users")
                total_users = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM users WHERE expires_at > %s", (datetime.now(),))
                active_users = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM users WHERE expires_at <= %s", (datetime.now(),))
                expired_users = cur.fetchone()[0]
                
                cur.execute("SELECT SUM(total_sms_sent) FROM users")
                total_sms = cur.fetchone()[0] or 0
                
                return {
                    'total_users': total_users,
                    'active_users': active_users,
                    'expired_users': expired_users,
                    'total_sms_sent': total_sms
                }
    
    def get_recent_activity(self, limit=20):
        """Get recent SMS activity with complete log details"""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute("""
                        SELECT s.id, s.phone_number, s.message, s.method, s.status, 
                               s.error_message, s.sent_at, u.username 
                        FROM sms_logs s 
                        JOIN users u ON s.user_id = u.id 
                        ORDER BY s.sent_at DESC 
                        LIMIT %s
                    """, (limit,))
                    return cur.fetchall()
        except Exception as e:
            print(f"Error getting recent activity: {e}")
            return []
    
    def change_admin_password(self, username, new_password):
        """Change admin password"""
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE admin_users SET password_hash = %s WHERE username = %s", 
                           (password_hash.decode('utf-8'), username))
                conn.commit()
                return cur.rowcount > 0