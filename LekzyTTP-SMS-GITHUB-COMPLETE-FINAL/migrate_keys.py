#!/usr/bin/env python3
"""
Migration script to transfer JSON-based API keys to PostgreSQL database
"""
import json
import os
import psycopg2
from datetime import datetime
from models import Database, UserManager

def migrate_json_to_database():
    """Migrate existing API keys from JSON to database"""
    try:
        # Load existing JSON keys
        with open('api_keys.json', 'r') as f:
            json_keys = json.load(f)
        
        print(f"Found {len(json_keys)} keys in JSON file")
        
        # Initialize database
        db = Database()
        user_manager = UserManager()
        
        migrated_count = 0
        
        for api_key, key_data in json_keys.items():
            try:
                # Parse expiration date
                expires_str = key_data.get('expires', '2025-12-31')
                expires_date = datetime.strptime(expires_str, '%Y-%m-%d')
                
                # Parse creation date
                created_str = key_data.get('created', '2025-07-15')
                created_date = datetime.strptime(created_str, '%Y-%m-%d')
                
                username = key_data.get('user', 'unknown_user')
                
                # Add user to database
                with db.get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO users (username, api_key, created_at, expires_at, is_active, total_sms_sent)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (api_key) DO NOTHING
                        """, (username, api_key, created_date, expires_date, True, 0))
                        
                        if cur.rowcount > 0:
                            migrated_count += 1
                            print(f"✓ Migrated: {api_key} -> {username}")
                        else:
                            print(f"- Skipped (exists): {api_key}")
                            
            except Exception as e:
                print(f"✗ Error migrating {api_key}: {str(e)}")
                
        print(f"\nMigration complete: {migrated_count} keys migrated to database")
        
        # Verify migration
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM users")
                total_users = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM users WHERE expires_at > NOW()")
                active_users = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM users WHERE expires_at <= NOW()")
                expired_users = cur.fetchone()[0]
                
                print(f"\nDatabase Summary:")
                print(f"Total Users: {total_users}")
                print(f"Active Users: {active_users}")
                print(f"Expired Users: {expired_users}")
                
    except Exception as e:
        print(f"Migration failed: {str(e)}")

if __name__ == "__main__":
    migrate_json_to_database()