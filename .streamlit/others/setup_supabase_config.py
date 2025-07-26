#!/usr/bin/env python3
"""
Supabase Configuration Helper for BharatVerse
Helps you set up Supabase connection and create tables
"""

import os
from pathlib import Path

def get_supabase_info():
    """Get Supabase connection information from user"""
    print("🔧 Supabase Configuration Setup")
    print("=" * 40)
    print("\n📋 You'll need the following from your Supabase project:")
    print("1. Project URL (e.g., https://your-project.supabase.co)")
    print("2. Database password (from your Supabase dashboard)")
    print("\n🔗 Find these in your Supabase dashboard:")
    print("   Settings → Database → Connection info")
    
    print("\n" + "=" * 40)
    
    # Get project URL
    project_url = input("🌐 Enter your Supabase project URL: ").strip()
    if not project_url:
        print("❌ Project URL is required!")
        return None
    
    # Extract host from URL
    if project_url.startswith('https://'):
        host = project_url.replace('https://', '')
    elif project_url.startswith('http://'):
        host = project_url.replace('http://', '')
    else:
        host = project_url
    
    # Get password
    password = input("🔐 Enter your database password: ").strip()
    if not password:
        print("❌ Database password is required!")
        return None
    
    return {
        'host': host,
        'port': 5432,
        'database': 'postgres',
        'user': 'postgres',
        'password': password
    }

def update_secrets_file(config):
    """Update the secrets.toml file with Supabase configuration"""
    secrets_path = Path('.streamlit/secrets.toml')
    
    if not secrets_path.exists():
        print("❌ .streamlit/secrets.toml not found!")
        return False
    
    try:
        # Read existing content
        with open(secrets_path, 'r') as f:
            content = f.read()
        
        # Add Supabase configuration
        supabase_config = f"""
# 🗄️ Supabase Database Configuration
[postgres]
host = "{config['host']}"
port = {config['port']}
database = "{config['database']}"
user = "{config['user']}"
password = "{config['password']}"
"""
        
        # Append to file
        with open(secrets_path, 'a') as f:
            f.write(supabase_config)
        
        print("✅ Updated .streamlit/secrets.toml with Supabase configuration")
        return True
        
    except Exception as e:
        print(f"❌ Error updating secrets file: {e}")
        return False

def test_connection(config):
    """Test the Supabase connection"""
    try:
        import psycopg2
        
        print("🔄 Testing Supabase connection...")
        
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['user'],
            password=config['password']
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print("✅ Connection successful!")
        print(f"📊 Database version: {version}")
        return True
        
    except ImportError:
        print("⚠️ psycopg2 not installed. Install with: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your project URL is correct")
        print("2. Verify your database password")
        print("3. Ensure your Supabase project is active")
        return False

def create_tables_with_config(config):
    """Create tables using the provided configuration"""
    try:
        import psycopg2
        
        print("🏗️ Creating Supabase tables...")
        
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['user'],
            password=config['password']
        )
        
        cursor = conn.cursor()
        
        # Users table
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
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contributions_user_id ON contributions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contributions_language ON contributions(language)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contributions_region ON contributions(region)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contributions_created_at ON contributions(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_user_id ON analytics(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_created_at ON analytics(created_at)")
        
        conn.commit()
        
        # Verify tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        print(f"✅ Created {len(tables)} tables successfully!")
        print("\n📋 Tables created:")
        for table in tables:
            print(f"  ✅ {table[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 BharatVerse Supabase Setup")
    print("=" * 50)
    
    # Step 1: Get Supabase info
    config = get_supabase_info()
    if not config:
        return
    
    # Step 2: Test connection
    if not test_connection(config):
        return
    
    # Step 3: Update secrets file
    if not update_secrets_file(config):
        return
    
    # Step 4: Create tables
    if create_tables_with_config(config):
        print("\n🎉 Supabase setup complete!")
        print("\n🔗 Next steps:")
        print("1. Check your Supabase dashboard to see the tables")
        print("2. Run your Streamlit app to test the integration")
        print("3. Submit text contributions to verify storage")
        print("\n📱 Your app will now store all text contributions in Supabase!")
    else:
        print("\n❌ Setup incomplete. Please check the errors above.")

if __name__ == "__main__":
    main()