#!/usr/bin/env python3
"""
Simple script to make first user admin using direct SQL
"""

import sqlite3
import os

def make_first_user_admin():
    db_path = 'instance/community_connect.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        print("💡 Please run your Flask app first to create the database")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current users
        cursor.execute("SELECT id, username, email, is_admin FROM user")
        users = cursor.fetchall()
        
        if not users:
            print("❌ No users found in database")
            print("💡 Please register a user through the website first")
            return
        
        print("👥 Current Users:")
        for user in users:
            user_id, username, email, is_admin = user
            admin_status = " (ADMIN)" if is_admin else ""
            print(f"   {user_id}: {username} {admin_status}")
        
        # Make first user admin
        first_user_id = users[0][0]
        first_username = users[0][1]
        
        cursor.execute("UPDATE user SET is_admin = 1 WHERE id = ?", (first_user_id,))
        conn.commit()
        
        print(f"✅ Made '{first_username}' an admin user")
        
        # Verify the change
        cursor.execute("SELECT username, is_admin FROM user WHERE id = ?", (first_user_id,))
        updated_user = cursor.fetchone()
        
        if updated_user and updated_user[1]:
            print(f"✅ Verified: {updated_user[0]} is now admin")
        else:
            print("❌ Failed to update admin status")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    make_first_user_admin()