#!/usr/bin/env python3
"""
BharatVerse Streamlit Cloud Deployment Script
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def main():
    print("🚀 BharatVerse - Streamlit Cloud Deployment Setup")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("\n📋 Pre-deployment Checklist:")
    
    # Check if Docker is running
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker is running")
            
            # Check if BharatVerse containers are running
            if 'postgres' in result.stdout and 'redis' in result.stdout:
                print("✅ BharatVerse Docker containers are running")
            else:
                print("⚠️ BharatVerse containers not detected. Starting them...")
                subprocess.run(['docker-compose', 'up', '-d'])
        else:
            print("❌ Docker is not running. Please start Docker first.")
            return False
    except FileNotFoundError:
        print("❌ Docker not found. Please install Docker first.")
        return False
    
    # Check GitHub repository
    try:
        result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
        if 'github.com' in result.stdout:
            print("✅ GitHub repository detected")
        else:
            print("⚠️ No GitHub repository detected")
            setup_github = input("Would you like to set up a GitHub repository? (y/n): ")
            if setup_github.lower() == 'y':
                setup_github_repo()
    except FileNotFoundError:
        print("❌ Git not found. Please install Git first.")
        return False
    
    # Create deployment files
    print("\n📦 Creating deployment files...")
    
    # Copy requirements for Streamlit Cloud
    if Path('streamlit_cloud_requirements.txt').exists():
        print("✅ Streamlit Cloud requirements.txt ready")
    else:
        print("❌ Missing streamlit_cloud_requirements.txt")
        return False
    
    # Create .streamlit/config.toml for cloud
    streamlit_dir = Path('.streamlit')
    streamlit_dir.mkdir(exist_ok=True)
    
    config_content = """
[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#FF6B35"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
"""
    
    with open(streamlit_dir / 'config.toml', 'w') as f:
        f.write(config_content)
    print("✅ Streamlit config created")
    
    # Create secrets template
    secrets_template = """
# Copy these to Streamlit Cloud Secrets
# Go to: https://share.streamlit.io -> Your App -> Settings -> Secrets

POSTGRES_HOST = "your-tunnel-url"
POSTGRES_PORT = "5432"
POSTGRES_USER = "bharatverse_user"
POSTGRES_PASSWORD = "secretpassword"
POSTGRES_DB = "bharatverse"

REDIS_HOST = "your-tunnel-url"
REDIS_PORT = "6379"

MINIO_HOST = "your-tunnel-url:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"

API_URL = "https://your-tunnel-url:8000"

SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = "30"

AI_MODE = "cloud"
ENABLE_HEAVY_MODELS = "false"
USE_LIGHTWEIGHT_MODELS = "true"
"""
    
    with open('streamlit_secrets_template.toml', 'w') as f:
        f.write(secrets_template)
    print("✅ Secrets template created")
    
    print("\n🌐 Next Steps for Streamlit Cloud Deployment:")
    print("1. Push your code to GitHub:")
    print("   git add .")
    print("   git commit -m 'Prepare for Streamlit Cloud deployment'")
    print("   git push origin main")
    print()
    print("2. Set up ngrok tunnel for local services:")
    print("   # Install ngrok: https://ngrok.com/download")
    print("   ngrok http 5432  # For PostgreSQL")
    print("   ngrok http 6379  # For Redis")
    print("   ngrok http 8000  # For API")
    print()
    print("3. Go to https://share.streamlit.io")
    print("4. Connect your GitHub repository")
    print("5. Set main file as: Home.py")
    print("6. Add secrets from streamlit_secrets_template.toml")
    print("7. Deploy!")
    
    print("\n🎉 Deployment setup complete!")
    return True

def setup_github_repo():
    """Set up GitHub repository"""
    print("\n📁 Setting up GitHub repository...")
    
    repo_name = input("Enter repository name (default: bharatverse): ") or "bharatverse"
    
    print("Please create a repository on GitHub and then run:")
    print(f"git remote add origin https://github.com/YOUR_USERNAME/{repo_name}.git")
    print("git branch -M main")
    print("git push -u origin main")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)