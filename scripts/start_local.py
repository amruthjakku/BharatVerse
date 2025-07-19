#!/usr/bin/env python3
"""
Local development startup script for BharatVerse
Sets up the environment for local development with localhost database connections
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def setup_local_environment():
    """Setup environment variables for local development"""
    
    # Load local environment variables
    env_local_path = Path(__file__).parent / '.env.local'
    
    if env_local_path.exists():
        print("📝 Loading local environment configuration...")
        
        # Read and set environment variables
        with open(env_local_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    print(f"   {key}={value}")
        
        print("✅ Local environment configured")
    else:
        print("❌ .env.local file not found")
        return False
    
    return True

def check_database_connection():
    """Check if database is accessible"""
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST', 'localhost'),
            port=os.environ.get('POSTGRES_PORT', '5432'),
            database=os.environ.get('POSTGRES_DB', 'bharatverse'),
            user=os.environ.get('POSTGRES_USER', 'bharatverse_user'),
            password=os.environ.get('POSTGRES_PASSWORD', 'secretpassword')
        )
        conn.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Make sure to run: docker-compose -f docker-compose-db.yml up -d")
        return False

def start_streamlit():
    """Start Streamlit application"""
    try:
        print("🚀 Starting Streamlit application...")
        
        # Change to project directory
        os.chdir(Path(__file__).parent)
        
        # Start Streamlit
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'Home.py',
            '--server.port', '8501',
            '--server.address', '0.0.0.0'
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Failed to start application: {e}")

def main():
    """Main startup function"""
    print("🤝 BharatVerse Local Development Startup")
    print("=" * 50)
    
    # Setup environment
    if not setup_local_environment():
        print("❌ Failed to setup environment")
        sys.exit(1)
    
    # Check database
    print("\n🔍 Checking database connection...")
    if not check_database_connection():
        print("\n💡 To start the database, run:")
        print("   docker-compose -f docker-compose-db.yml up -d")
        print("   Then wait a few seconds and try again")
        sys.exit(1)
    
    # Start application
    print("\n🚀 Starting BharatVerse with Community Features...")
    print("📱 The application will be available at: http://localhost:8501")
    print("🤝 Navigate to the Community page to explore the new features!")
    print("\nPress Ctrl+C to stop the application")
    print("-" * 50)
    
    start_streamlit()

if __name__ == "__main__":
    main()