#!/usr/bin/env python3
"""
🚀 BharatVerse Interactive Setup Script
=====================================
This script helps you set up all the required cloud services and API keys.
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path
import boto3
from botocore.exceptions import ClientError

def print_header(text, emoji="🚀"):
    """Print a formatted header"""
    print(f"\n{emoji} {text}")
    print("=" * (len(text) + 4))

def print_step(step_num, title, emoji="📋"):
    """Print a step header"""
    print(f"\n{emoji} Step {step_num}: {title}")
    print("-" * 40)

def open_url_and_wait(url, message):
    """Open URL in browser and wait for user"""
    print(f"🌐 Opening: {url}")
    try:
        webbrowser.open(url)
    except:
        print(f"❌ Could not open browser. Please manually visit: {url}")
    
    input(f"\n✋ {message}\nPress Enter to continue...")

def get_user_input(prompt, required=True):
    """Get input from user with validation"""
    while True:
        value = input(f"📝 {prompt}: ").strip()
        if value or not required:
            return value
        print("❌ This field is required. Please enter a value.")

def update_secrets_file(secrets_file, updates):
    """Update the secrets.toml file with new values"""
    try:
        with open(secrets_file, 'r') as f:
            content = f.read()
        
        for placeholder, actual_value in updates.items():
            if actual_value:  # Only update if user provided a value
                content = content.replace(placeholder, actual_value)
        
        with open(secrets_file, 'w') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"❌ Error updating secrets file: {e}")
        return False

def test_and_setup_minio(endpoint_url: str, access_key: str, secret_key: str) -> bool:
    """Test MinIO connection and create bharatverse-bucket if needed"""
    print("\n🧪 Testing MinIO connection...")
    
    try:
        # Create MinIO client
        s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name='us-east-1'
        )
        
        # Test connection by listing buckets
        response = s3_client.list_buckets()
        print("✅ MinIO connection successful!")
        
        # Check if bharatverse-bucket exists
        bucket_name = 'bharatverse-bucket'
        existing_buckets = [bucket['Name'] for bucket in response.get('Buckets', [])]
        
        if bucket_name in existing_buckets:
            print(f"✅ Bucket '{bucket_name}' already exists!")
        else:
            print(f"🪣 Creating bucket '{bucket_name}'...")
            try:
                s3_client.create_bucket(Bucket=bucket_name)
                print(f"✅ Bucket '{bucket_name}' created successfully!")
            except ClientError as e:
                print(f"⚠️  Could not create bucket: {e}")
                return False
        
        # Test upload/download
        try:
            test_key = 'test/setup-test.txt'
            test_content = b'BharatVerse setup test file'
            
            # Upload test file
            s3_client.put_object(
                Bucket=bucket_name,
                Key=test_key,
                Body=test_content,
                ContentType='text/plain'
            )
            
            # Download test file  
            response = s3_client.get_object(Bucket=bucket_name, Key=test_key)
            downloaded_content = response['Body'].read()
            
            if downloaded_content == test_content:
                print("✅ File upload/download test successful!")
                # Clean up test file
                s3_client.delete_object(Bucket=bucket_name, Key=test_key)
                return True
            else:
                print("❌ File content mismatch in test")
                return False
                
        except ClientError as e:
            print(f"❌ Upload/download test failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ MinIO connection failed: {e}")
        print("   Please check:")
        print("   • MinIO endpoint URL is correct")
        print("   • MinIO service is running")
        print("   • Credentials are correct")
        return False

def main():
    """Main setup function"""
    print_header("BharatVerse Complete Setup", "🇮🇳")
    print("Welcome to the BharatVerse setup wizard!")
    print("We'll help you set up all the required cloud services.")
    print("\n🎯 Services we'll configure:")
    print("  • HuggingFace (AI APIs)")
    print("  • Supabase (Database)")
    print("  • Upstash (Redis Cache)")  
    print("  • MinIO on Render (Object Storage)")
    print("  • GitHub (Code Repository)")
    
    # Check if secrets file exists
    secrets_file = Path(".streamlit/secrets.toml")
    if not secrets_file.exists():
        print(f"\n❌ Secrets file not found: {secrets_file}")
        print("Please ensure you're running this from the bharatverse directory")
        print("and that the .streamlit/secrets.toml file exists.")
        return
    
    print(f"\n✅ Found secrets file: {secrets_file}")
    
    if input("\n🚀 Ready to start? (y/n): ").lower() != 'y':
        print("👋 Setup cancelled. Run again when ready!")
        return
    
    # Dictionary to store all the values we'll collect
    secrets_updates = {}
    
    # ===========================================
    # 1. HUGGINGFACE SETUP
    # ===========================================
    print_step(1, "HuggingFace AI API Setup", "🤗")
    print("HuggingFace provides free AI model APIs for text, audio, and image processing.")
    
    open_url_and_wait("https://huggingface.co/join", 
                      "Create your HuggingFace account and verify your email")
    
    open_url_and_wait("https://huggingface.co/settings/tokens",
                      "Create a new token with 'Read' permissions")
    
    hf_token = get_user_input("Enter your HuggingFace token (hf_...)")
    if hf_token.startswith('hf_'):
        secrets_updates["hf_your_token_here"] = hf_token
        print("✅ HuggingFace token saved")
    else:
        print("⚠️  Invalid token format. Please ensure it starts with 'hf_'")
    
    # ===========================================
    # 2. SUPABASE SETUP  
    # ===========================================
    print_step(2, "Supabase Database Setup", "🐘")
    print("Supabase provides a free PostgreSQL database with 500MB storage.")
    
    open_url_and_wait("https://supabase.com", 
                      "Create your Supabase account and create a new project named 'bharatverse'")
    
    print("\n📋 Now we need your Supabase project details...")
    
    project_id = get_user_input("Enter your Supabase project ID (from the URL)")
    db_password = get_user_input("Enter your database password (you created this)")
    
    if project_id and db_password:
        # Update database connection details
        secrets_updates["your-project-id"] = project_id
        secrets_updates["your-supabase-password"] = db_password
        secrets_updates["your-password"] = db_password
        print("✅ Supabase database config saved")
    
    open_url_and_wait(f"https://app.supabase.com/project/{project_id}/settings/api",
                      "Copy your API keys from the API settings page")
    
    anon_key = get_user_input("Enter your anon/public API key")
    service_key = get_user_input("Enter your service_role API key") 
    
    if anon_key and service_key:
        secrets_updates["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your-anon-key"] = anon_key
        secrets_updates["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your-service-role-key"] = service_key
        print("✅ Supabase API keys saved")
    
    # Offer to create tables
    create_tables = input("\n🗃️  Would you like to create the database tables now? (y/n): ").lower() == 'y'
    if create_tables:
        open_url_and_wait(f"https://app.supabase.com/project/{project_id}/sql/new",
                          "Paste the SQL from COMPLETE_SETUP_GUIDE.md and run it")
    
    # ===========================================
    # 3. UPSTASH REDIS SETUP
    # ===========================================
    print_step(3, "Upstash Redis Cache Setup", "⚡")
    print("Upstash provides free Redis caching with 10K requests per day.")
    
    open_url_and_wait("https://upstash.com", 
                      "Create your Upstash account and create a new Redis database named 'bharatverse-cache'")
    
    redis_url = get_user_input("Enter your Redis REST URL (https://...upstash.io)")
    redis_token = get_user_input("Enter your Redis REST token")
    
    if redis_url and redis_token:
        secrets_updates["https://your-db-id.upstash.io"] = redis_url
        secrets_updates["your-upstash-rest-token"] = redis_token
        print("✅ Upstash Redis config saved")
    
    # ===========================================
    # 4. MINIO ON RENDER SETUP
    # ===========================================
    print_step(4, "MinIO on Render Storage Setup", "🪣")
    print("MinIO on Render provides free object storage compatible with AWS S3.")
    print("We'll help you deploy MinIO on Render with default credentials.")
    
    has_render = input("\n📋 Do you already have a MinIO instance on Render? (y/n): ").lower() == 'y'
    
    if not has_render:
        print("\n🚀 Let's deploy MinIO on Render...")
        open_url_and_wait("https://render.com/", 
                          "Create your Render account (it's free!)")
        
        open_url_and_wait("https://render.com/deploy?repo=https://github.com/minio/minio",
                          "Deploy MinIO using Render's one-click deploy")
        
        print("\n⚙️  Configure your MinIO deployment:")
        print("   • Service Name: bharatverse-minio")
        print("   • Environment: Leave defaults (MINIO_ROOT_USER=minioadmin, MINIO_ROOT_PASSWORD=minioadmin)")
        print("   • Port: 9000")
        print("   • Plan: Free ($0/month)")
        
        input("\n✋ Complete the deployment and wait for it to be live. Press Enter when ready...")
    
    minio_endpoint = get_user_input("Enter your MinIO endpoint URL (https://your-app-name.onrender.com)")
    
    # Use default MinIO credentials
    access_key = "minioadmin"
    secret_key = "minioadmin"
    
    print(f"\n🔧 Using default MinIO credentials:")
    print(f"   • Access Key: {access_key}")
    print(f"   • Secret Key: {secret_key}")
    
    if minio_endpoint:
        # Test MinIO connection and create bucket
        test_success = test_and_setup_minio(minio_endpoint, access_key, secret_key)
        
        if test_success:
            secrets_updates["your-minio-endpoint"] = minio_endpoint
            secrets_updates["minioadmin"] = access_key
            secrets_updates["minioadmin-secret"] = secret_key
            print("✅ MinIO on Render configured and tested successfully!")
        else:
            print("⚠️  MinIO configuration saved but connection test failed.")
    
    # ===========================================
    # 5. GITHUB SETUP
    # ===========================================
    print_step(5, "GitHub Repository Setup", "🐙")
    print("GitHub will host your code for Streamlit Cloud deployment.")
    
    has_github = input("\n📋 Do you already have the code in a GitHub repository? (y/n): ").lower() == 'y'
    
    if not has_github:
        open_url_and_wait("https://github.com/new", 
                          "Create a new public repository named 'bharatverse'")
        
        github_username = get_user_input("Enter your GitHub username")
        github_repo = get_user_input("Enter your repository name", required=False) or "bharatverse"
        
        print(f"\n📤 To push your code to GitHub:")
        print(f"git remote add origin https://github.com/{github_username}/{github_repo}.git")
        print("git branch -M main")
        print("git add .")
        print('git commit -m "Initial commit: BharatVerse platform"')
        print("git push -u origin main")
        
        push_now = input("\n🚀 Would you like to push to GitHub now? (y/n): ").lower() == 'y'
        if push_now:
            try:
                # Initialize git and push
                subprocess.run(["git", "init"], cwd=".", check=True)
                subprocess.run(["git", "remote", "add", "origin", f"https://github.com/{github_username}/{github_repo}.git"], cwd=".", check=True)
                subprocess.run(["git", "branch", "-M", "main"], cwd=".", check=True)
                subprocess.run(["git", "add", "."], cwd=".", check=True)
                subprocess.run(["git", "commit", "-m", "Initial commit: BharatVerse platform"], cwd=".", check=True)
                subprocess.run(["git", "push", "-u", "origin", "main"], cwd=".", check=True)
                print("✅ Code pushed to GitHub successfully!")
            except subprocess.CalledProcessError as e:
                print(f"❌ Git error: {e}")
                print("Please push manually using the commands above.")
    
    # ===========================================
    # 6. UPDATE SECRETS FILE
    # ===========================================
    print_step(6, "Updating Configuration", "⚙️")
    
    if secrets_updates:
        print(f"🔧 Updating {len(secrets_updates)} configuration values...")
        
        if update_secrets_file(secrets_file, secrets_updates):
            print("✅ Secrets file updated successfully!")
        else:
            print("❌ Failed to update secrets file. Please check manually.")
    
    # ===========================================
    # 7. FINAL STEPS
    # ===========================================
    print_header("Setup Complete!", "🎉")
    
    print("✅ All services configured!")
    print("\n🚀 Next steps:")
    print("1. Test your setup: python scripts/test_cloud_setup.py")
    print("2. Run locally: streamlit run Home.py")
    print("3. Deploy to cloud: Visit https://share.streamlit.io")
    
    print("\n📚 Resources:")
    print("• Setup guide: COMPLETE_SETUP_GUIDE.md")
    print("• Architecture: ARCHITECTURE_IMPROVEMENTS.md")
    print("• Cloud deployment: Free_Cloud_Deployment.md")
    
    print("\n🎯 Your BharatVerse platform is ready!")
    print("Visit the live demo at your Streamlit Cloud URL once deployed.")

if __name__ == "__main__":
    try:
        # Install required packages if missing
        try:
            import boto3
        except ImportError:
            print("📦 Installing required packages...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "boto3", "botocore"])
            import boto3
            from botocore.exceptions import ClientError
            
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user. Run again when ready!")
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
        print("Please check the COMPLETE_SETUP_GUIDE.md for manual setup instructions.")