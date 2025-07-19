#!/usr/bin/env python3
"""
Simple local startup script for BharatVerse
Runs without database dependencies for UI development
"""

import os
import subprocess
import sys

def main():
    print("🚀 Starting BharatVerse in Simple Mode (No Database)")
    print("=" * 50)
    
    # Set environment variable to disable database
    os.environ['DISABLE_DATABASE'] = 'true'
    
    # Use local .env file
    if os.path.exists('.env.local'):
        print("✅ Using .env.local configuration")
        os.environ['ENV_FILE'] = '.env.local'
    
    # Start Streamlit
    print("\n📱 Starting Streamlit app...")
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "Home.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down BharatVerse...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
