#!/usr/bin/env python3
"""
Setup Supabase Database Tables for BharatVerse
Creates all necessary tables and indexes in your Supabase PostgreSQL database
"""

import streamlit as st
import sys
from pathlib import Path
import logging

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_supabase_tables():
    """Initialize Supabase database with all required tables"""
    try:
        from utils.supabase_db import DatabaseManager
        
        print("🔄 Connecting to Supabase...")
        db = DatabaseManager()
        
        print("🏗️ Creating database tables...")
        db.init_database()
        
        print("✅ Supabase database setup complete!")
        print("\n📊 Tables created:")
        print("- users (user accounts and profiles)")
        print("- contributions (text stories, proverbs, etc.)")
        print("- analytics (user activity tracking)")
        print("- community_interactions (likes, comments, etc.)")
        
        print("\n🔍 Indexes created for performance:")
        print("- contributions by user_id, language, region, created_at")
        print("- analytics by user_id, created_at")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up Supabase tables: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your Supabase connection in streamlit secrets")
        print("2. Ensure your Supabase project is active")
        print("3. Verify database credentials are correct")
        return False

def verify_tables():
    """Verify that all tables were created successfully"""
    try:
        from utils.supabase_db import DatabaseManager
        
        db = DatabaseManager()
        
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                # Check if tables exist
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                """)
                
                tables = cursor.fetchall()
                
                print("\n📋 Tables found in Supabase:")
                for table in tables:
                    print(f"  ✅ {table[0]}")
                
                # Check contributions table structure
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = 'contributions'
                    ORDER BY ordinal_position
                """)
                
                columns = cursor.fetchall()
                
                if columns:
                    print("\n📝 Contributions table structure:")
                    for col in columns:
                        nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                        print(f"  - {col[0]}: {col[1]} ({nullable})")
                else:
                    print("⚠️ Contributions table not found or empty")
                
                return len(tables) > 0
                
    except Exception as e:
        print(f"❌ Error verifying tables: {e}")
        return False

def create_sample_data():
    """Create some sample data for testing"""
    try:
        from utils.supabase_db import DatabaseManager
        
        db = DatabaseManager()
        
        print("\n🎯 Creating sample data...")
        
        # Create a sample user
        user_id = db.create_user(
            username="demo_user",
            email="demo@bharatverse.com",
            full_name="Demo User",
            provider="demo"
        )
        
        if user_id:
            print(f"✅ Created sample user with ID: {user_id}")
            
            # Create sample contributions
            contrib_id = db.insert_contribution(
                user_id=user_id,
                title="Sample Bengali Folk Tale",
                content="এক সময় এক ছোট গ্রামে একটি সুন্দর গল্প ছিল...",
                content_type="text",
                language="Bengali",
                region="West Bengal",
                tags=["folk", "story", "bengali", "traditional"],
                metadata={
                    "author": "Traditional",
                    "word_count": 25,
                    "character_count": 45,
                    "sample_data": True
                },
                ai_analysis={
                    "sentiment": "positive",
                    "themes": ["tradition", "culture", "storytelling"],
                    "cultural_significance": 0.85
                }
            )
            
            if contrib_id:
                print(f"✅ Created sample contribution with ID: {contrib_id}")
            
            # Create sample proverb
            proverb_id = db.insert_contribution(
                user_id=user_id,
                title="Sample Hindi Proverb",
                content="जैसी करनी वैसी भरनी - As you sow, so shall you reap",
                content_type="proverb",
                language="Hindi",
                region="North India",
                tags=["proverb", "wisdom", "hindi", "karma"],
                metadata={
                    "original_text": "जैसी करनी वैसी भरनी",
                    "translation": "As you sow, so shall you reap",
                    "meaning": "Your actions determine your consequences",
                    "category": "wisdom",
                    "sample_data": True
                }
            )
            
            if proverb_id:
                print(f"✅ Created sample proverb with ID: {proverb_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 BharatVerse Supabase Database Setup")
    print("=" * 50)
    
    # Step 1: Create tables
    if setup_supabase_tables():
        print("\n" + "=" * 50)
        
        # Step 2: Verify tables
        if verify_tables():
            print("\n" + "=" * 50)
            
            # Step 3: Create sample data
            create_sample = input("\n❓ Create sample data for testing? (y/n): ").lower().strip()
            if create_sample in ['y', 'yes']:
                create_sample_data()
            
            print("\n🎉 Setup complete! Your Supabase database is ready.")
            print("\n🔗 Next steps:")
            print("1. Check your Supabase dashboard to see the tables")
            print("2. Run your Streamlit app to test the integration")
            print("3. Submit some text contributions to verify storage")
            
        else:
            print("\n⚠️ Table verification failed. Check your Supabase connection.")
    else:
        print("\n❌ Setup failed. Please check your configuration.")

if __name__ == "__main__":
    main()