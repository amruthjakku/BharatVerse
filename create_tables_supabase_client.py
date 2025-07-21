#!/usr/bin/env python3
"""
Create Supabase tables using the Supabase Python client
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def create_tables_with_supabase_client():
    """Create tables using Supabase client"""
    try:
        # Try to use the existing database manager
        from utils.supabase_db import DatabaseManager
        
        print("🔄 Initializing Supabase database...")
        db = DatabaseManager()
        
        print("🏗️ Creating tables...")
        db.init_database()
        
        print("✅ Tables created successfully!")
        
        # Test by creating a sample user
        print("🧪 Testing with sample data...")
        user_id = db.create_user(
            username="test_user",
            email="test@bharatverse.com",
            full_name="Test User"
        )
        
        if user_id:
            print(f"✅ Sample user created with ID: {user_id}")
            
            # Create a sample contribution
            contrib_id = db.insert_contribution(
                user_id=user_id,
                title="Test Bengali Story",
                content="এটি একটি পরীক্ষার গল্প। (This is a test story.)",
                content_type="text",
                language="Bengali",
                region="West Bengal",
                tags=["test", "bengali", "story"],
                metadata={"test": True, "word_count": 8},
                ai_analysis={"sentiment": "neutral", "test": True}
            )
            
            if contrib_id:
                print(f"✅ Sample contribution created with ID: {contrib_id}")
            
            # Verify by fetching contributions
            contributions = db.get_contributions(limit=5)
            print(f"✅ Found {len(contributions)} contributions in database")
            
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your Supabase project is active")
        print("2. Verify the database password is correct")
        print("3. Ensure your IP is allowed in Supabase settings")
        return False

def main():
    """Main function"""
    print("🚀 BharatVerse Supabase Setup (Client Method)")
    print("=" * 50)
    
    if create_tables_with_supabase_client():
        print("\n🎉 Supabase setup complete!")
        print("\n🔗 Next steps:")
        print("1. Check your Supabase dashboard to see the tables")
        print("2. Run your Streamlit app")
        print("3. Submit text contributions to test storage")
        print("\n📱 Your app will now store all data in Supabase!")
    else:
        print("\n❌ Setup failed. Please check the errors above.")

if __name__ == "__main__":
    main()