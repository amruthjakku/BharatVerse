#!/usr/bin/env python3
"""
Quick Supabase Connection Test
"""

import psycopg2
import sys
from pathlib import Path

def test_connection():
    """Test Supabase connection"""
    try:
        print("🔄 Testing Supabase connection...")
        
        conn = psycopg2.connect(
            host="hzjbpthvkekfahwiujbz.supabase.co",
            port=5432,
            database="postgres",
            user="postgres",
            password="BharatVerse",
            connect_timeout=10
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        
        print("✅ Connection successful!")
        print(f"📊 Database: {version[:50]}...")
        
        # Check existing tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"\n📋 Existing tables ({len(tables)}):")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()