import os
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta
import secrets
import string
import bcrypt

class Database:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            self.database_url = 'postgresql://localhost/lekzy_sms'
        
    def get_connection(self):
        return psycopg2.connect(self.database_url)
    
    def init_db(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            
        """Initialize database tables"""
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
                
                # Insert default admin user
                default_password = os.getenv('ADMIN_PASSWORD', 'ChangeMeNow!')
                password_hash = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt())
                cur.execute("""
                    INSERT INTO admin_users (username, password_hash) 
                    VALUES (%s, %s) 
                    ON CONFLICT (username) DO NOTHING
                """, ('admin', password_hash.decode('utf-8')))
                
                conn.commit()

class UserManager:
    def __init__(self):
        self.db = Database()
    
    def generate_api_key(self, username, days=30):
        """Generate a new API key for a user"""
        # Generate unique API key
        while True:
            key = f"KEY-Lekzy-TTP-{''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))}"
            if not self.get_user_by_key(key):
                break
        
        expires_at = datetime.now() + timedelta(days=days)
        
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                # Check if user already exists
                cur.execute("SELECT id FROM users WHERE username = %s", (username,))
                existing_user = cur.fetchone()
                
                if existing_user:
                    # Update existing user
                    cur.execute("""
                        UPDATE users 
                        SET api_key = %s, expires_at = %s, is_active = TRUE, last_activity = CURRENT_TIMESTAMP
                        WHERE username = %s
                        RETURNING id
                    """, (key, expires_at, username))
                else:
                    # Create new user
                    cur.execute("""
                        INSERT INTO users (username, api_key, expires_at) 
                        VALUES (%s, %s, %s)
                        RETURNING id
                    """, (username, key, expires_at))
                
                conn.commit()
                return key
    
    def get_user_by_key(self, api_key):
        """Get user by API key"""
        with self.db.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM users WHERE api_key = %s AND is_active = TRUE
                """, (api_key,))
                return cur.fetchone()
    
    def get_user_by_username(self, username):
        """Get user by username"""
        with self.db.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM users WHERE username = %s
                """, (username,))
                return cur.fetchone()
    
    def is_key_valid(self, api_key):
        """Check if API key is valid and not expired"""
        user = self.get_user_by_key(api_key)
        if not user:
            return False
        
        return user['is_active'] and datetime.now() < user['expires_at']
    
    def get_all_users(self):
        """Get all users"""
        with self.db.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT *, 
                           CASE WHEN expires_at > CURRENT_TIMESTAMP AND is_active THEN 'Active'
                                WHEN expires_at <= CURRENT_TIMESTAMP THEN 'Expired'
                                ELSE 'Inactive'
                           END as status
                    FROM users 
                    ORDER BY created_at DESC
                """)
                return cur.fetchall()
    
    def get_active_keys(self):
        """Get all active API keys"""
        with self.db.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT username, api_key, expires_at, total_sms_sent
                    FROM users 
                    WHERE is_active = TRUE AND expires_at > CURRENT_TIMESTAMP
                    ORDER BY expires_at DESC
                """)
                return cur.fetchall()
    
    def revoke_key(self, api_key):
        """Revoke an API key"""
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE users SET is_active = FALSE 
                    WHERE api_key = %s
                    RETURNING username
                """, (api_key,))
                result = cur.fetchone()
                conn.commit()
                return result[0] if result else None
    
    def extend_subscription(self, api_key, days):
        """Extend user subscription"""
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE users 
                    SET expires_at = expires_at + INTERVAL '%s days'
                    WHERE api_key = %s
                    RETURNING username, expires_at
                """, (days, api_key))
                result = cur.fetchone()
                conn.commit()
                return result if result else None
    
    def log_sms(self, api_key, phone_number, message, method, status, error_message=None):
        """Log SMS sending activity"""
        user = self.get_user_by_key(api_key)
        if not user:
            return
        
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                # Log the SMS
                cur.execute("""
                    INSERT INTO sms_logs (user_id, phone_number, message, method, status, error_message)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (user['id'], phone_number, message[:100], method, status, error_message))
                
                # Update user's total SMS count if successful
                if status == 'SUCCESS':
                    cur.execute("""
                        UPDATE users 
                        SET total_sms_sent = total_sms_sent + 1, last_activity = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (user['id'],))
                
                conn.commit()

class AdminManager:
    def __init__(self):
        self.db = Database()
    
    def authenticate_admin(self, username, password):
        """Authenticate admin user"""
        with self.db.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM admin_users WHERE username = %s
                """, (username,))
                admin = cur.fetchone()
                
                if admin and bcrypt.checkpw(password.encode('utf-8'), admin['password_hash'].encode('utf-8')):
                    # Update last login
                    cur.execute("""
                        UPDATE admin_users SET last_login = CURRENT_TIMESTAMP WHERE id = %s
                    """, (admin['id'],))
                    conn.commit()
                    return admin
                
                return None
    
    def change_admin_password(self, username, new_password):
        """Change admin password"""
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE admin_users 
                    SET password_hash = %s
                    WHERE username = %s
                    RETURNING id
                """, (password_hash.decode('utf-8'), username))
                result = cur.fetchone()
                conn.commit()
                return result is not None
    
    def get_user_stats(self):
        """Get user statistics for admin dashboard"""
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_users,
                        COUNT(*) FILTER (WHERE is_active = TRUE AND expires_at > CURRENT_TIMESTAMP) as active_users,
                        COUNT(*) FILTER (WHERE expires_at <= CURRENT_TIMESTAMP) as expired_users,
                        SUM(total_sms_sent) as total_sms_sent
                    FROM users
                """)
                return cur.fetchone()
    
    def get_recent_activity(self, limit=10):
        """Get recent SMS activity"""
        with self.db.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT u.username, sl.phone_number, sl.method, sl.status, sl.sent_at
                    FROM sms_logs sl
                    JOIN users u ON sl.user_id = u.id
                    ORDER BY sl.sent_at DESC
                    LIMIT %s
                """, (limit,))
                return cur.fetchall()

# Initialize database when module is imported
if __name__ == "__main__":
    db = Database()
    db.init_db()
    print("Database initialized successfully!")
