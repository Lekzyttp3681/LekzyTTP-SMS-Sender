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
            # Fallback for local development
            self.database_url = 'postgresql://localhost/lekzy_sms'
        
    def get_connection(self):
        return psycopg2.connect(self.database_url)
    
    def init_db(self):
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
    
    def is_key_valid(self, api_key):
        """Check if API key is valid and not expired"""
        user = self.get_user_by_key(api_key)
        if not user:
            return False
        
        return

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
