#!/usr/bin/env python3
"""
Simple Supabase Table Creator for BharatVerse
Run this to create all necessary tables in your Supabase database
"""

import psycopg2
import json
import os
from pathlib import Path

def get_supabase_config():
    """Get Supabase configuration from environment or secrets"""
    # Try to get from environment variables first
    config = {
        'host': os.getenv('SUPABASE_HOST'),
        'port': os.getenv('SUPABASE_PORT', 5432),
        'database': os.getenv('SUPABASE_DATABASE'),
        'user': os.getenv('SUPABASE_USER'),
        'password': os.getenv('SUPABASE_PASSWORD')
    }
    
    # If not in environment, try to read from Streamlit secrets
    if not config['host']:
        secrets_path = Path('.streamlit/secrets.toml')
        if secrets_path.exists():
            print("📄 Reading from .streamlit/secrets.toml")
            try:
                import toml
                secrets = toml.load(secrets_path)
                postgres_config = secrets.get('postgres', {})
                config.update(postgres_config)
            except ImportError:
                print("⚠️ toml package not found. Install with: uv pip install toml")
                return None
        else:
            print("❌ No Supabase configuration found!")
            print("Please set environment variables or create .streamlit/secrets.toml")
            return None
    
    return config

def create_tables(config):
    """Create all necessary tables in Supabase"""
    try:
        # Connect to Supabase
        print(f"🔄 Connecting to Supabase at {config['host']}...")
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['user'],
            password=config['password']
        )
        
        cursor = conn.cursor()
        
        print("🏗️ Creating tables...")
        
        # Users table
        print("  📝 Creating users table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                full_name VARCHAR(255),
                avatar_url TEXT,
                provider VARCHAR(50) DEFAULT 'email',
                provider_id VARCHAR(255),
                role VARCHAR(20) DEFAULT 'user',
                is_active BOOLEAN DEFAULT true,
                preferences JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Contributions table
        print("  📚 Creating contributions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contributions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                title VARCHAR(500) NOT NULL,
                content TEXT,
                content_type VARCHAR(50),
                file_url TEXT,
                file_type VARCHAR(100),
                file_size INTEGER,
                language VARCHAR(50),
                region VARCHAR(100),
                tags TEXT[],
                metadata JSONB DEFAULT '{}',
                ai_analysis JSONB DEFAULT '{}',
                is_public BOOLEAN DEFAULT true,
                view_count INTEGER DEFAULT 0,
                like_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Analytics table
        print("  📊 Creating analytics table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                event_type VARCHAR(100) NOT NULL,
                event_data JSONB DEFAULT '{}',
                session_id VARCHAR(255),
                ip_address INET,
                user_agent TEXT,
                processing_time_ms INTEGER,
                status VARCHAR(20),
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Community interactions table
        print("  💬 Creating community_interactions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS community_interactions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                target_user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                contribution_id INTEGER REFERENCES contributions(id) ON DELETE CASCADE,
                interaction_type VARCHAR(50),
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        print("  🔍 Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contributions_user_id ON contributions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contributions_language ON contributions(language)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contributions_region ON contributions(region)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contributions_created_at ON contributions(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_user_id ON analytics(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_created_at ON analytics(created_at)")
        
        # Commit changes
        conn.commit()
        
        print("✅ All tables created successfully!")
        
        # Verify tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"\n📋 Tables in database ({len(tables)} total):")
        for table in tables:
            print(f"  ✅ {table[0]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def create_sample_user(config):
    """Create a sample user for testing"""
    try:
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['user'],
            password=config['password']
        )
        
        cursor = conn.cursor()
        
        # Check if sample user already exists
        cursor.execute("SELECT id FROM users WHERE username = 'demo_user'")
        if cursor.fetchone():
            print("ℹ️ Sample user already exists")
            cursor.close()
            conn.close()
            return
        
        # Create sample user
        cursor.execute("""
            INSERT INTO users (username, email, full_name, provider, role)
            VALUES ('demo_user', 'demo@bharatverse.com', 'Demo User', 'demo', 'user')
            RETURNING id
        """)
        
        user_id = cursor.fetchone()[0]
        
        # Create sample contribution
        cursor.execute("""
            INSERT INTO contributions (
                user_id, title, content, content_type, language, region, tags, metadata
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            user_id,
            "Sample Bengali Folk Tale",
            "এক সময় এক ছোট গ্রামে একটি সুন্দর গল্প ছিল... (Once upon a time in a small village, there was a beautiful story...)",
            "text",
            "Bengali",
            "West Bengal",
            ["folk", "story", "bengali", "traditional"],
            json.dumps({
                "author": "Traditional",
                "word_count": 25,
                "sample_data": True
            })
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Created sample user and contribution (User ID: {user_id})")
        
    except Exception as e:
        print(f"⚠️ Could not create sample data: {e}")

def main():
    """Main function"""
    print("🚀 BharatVerse Supabase Table Creator")
    print("=" * 50)
    
    # Get configuration
    config = get_supabase_config()
    if not config or not config.get('host'):
        print("\n❌ Supabase configuration not found!")
        print("\n🔧 Setup instructions:")
        print("1. Set environment variables:")
        print("   export SUPABASE_HOST=your-project.supabase.co")
        print("   export SUPABASE_DATABASE=postgres")
        print("   export SUPABASE_USER=postgres")
        print("   export SUPABASE_PASSWORD=your-password")
        print("\n2. Or create .streamlit/secrets.toml with:")
        print("   [postgres]")
        print("   host = 'your-project.supabase.co'")
        print("   database = 'postgres'")
        print("   user = 'postgres'")
        print("   password = 'your-password'")
        return
    
    # Create tables
    if create_tables(config):
        print("\n🎉 Database setup complete!")
        
        # Ask about sample data
        create_sample = input("\n❓ Create sample data for testing? (y/n): ").lower().strip()
        if create_sample in ['y', 'yes']:
            create_sample_user(config)
        
        print("\n🔗 Next steps:")
        print("1. Check your Supabase dashboard to see the tables")
        print("2. Run your Streamlit app to test the integration")
        print("3. Submit text contributions to verify storage")
        
    else:
        print("\n❌ Setup failed. Please check your Supabase configuration.")

if __name__ == "__main__":
    main()