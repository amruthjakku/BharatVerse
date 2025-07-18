#!/usr/bin/env python3
"""
Script to help update GitLab OAuth callback URL configuration
This script provides instructions and validation for callback URL setup
"""

import os
import sys
import re
from urllib.parse import urlparse

def validate_callback_url(url):
    """Validate callback URL format"""
    try:
        parsed = urlparse(url)
        if not parsed.scheme:
            return False, "URL must include scheme (http:// or https://)"
        if not parsed.netloc:
            return False, "URL must include domain/host"
        if not parsed.path.endswith('/callback'):
            return False, "URL must end with '/callback'"
        return True, "Valid callback URL"
    except Exception as e:
        return False, f"Invalid URL format: {e}"

def get_current_config():
    """Get current OAuth configuration"""
    config = {}
    
    # Try to load from .env.local first, then .env
    env_files = ['.env.local', '.env']
    
    for env_file in env_files:
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('GITLAB_') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key] = value
            break
    
    return config

def main():
    print("🦊 GitLab OAuth Callback URL Configuration Helper")
    print("=" * 50)
    
    # Get current configuration
    config = get_current_config()
    
    if not config:
        print("❌ No GitLab OAuth configuration found!")
        print("Please ensure you have .env or .env.local file with GitLab OAuth settings.")
        return
    
    print("\n📋 Current Configuration:")
    for key, value in config.items():
        if 'SECRET' in key:
            print(f"  {key}: {'*' * 20}")
        else:
            print(f"  {key}: {value}")
    
    current_callback = config.get('GITLAB_REDIRECT_URI', '')
    
    print(f"\n🔗 Current Callback URL: {current_callback}")
    
    # Validate current URL
    if current_callback:
        is_valid, message = validate_callback_url(current_callback)
        if is_valid:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
    
    print("\n" + "=" * 50)
    print("📝 Instructions for updating callback URL:")
    print()
    
    print("1. 🌐 If running on different port:")
    print("   Update GITLAB_REDIRECT_URI in your .env.local file")
    print("   Example: GITLAB_REDIRECT_URI=http://localhost:8503/callback")
    print()
    
    print("2. 🔧 If you have admin access to GitLab:")
    print("   a. Go to: https://code.swecha.org/admin/applications")
    print("   b. Find application: BharatVerse gitlab oAuth")
    print("   c. Update 'Redirect URI' field")
    print("   d. Save changes")
    print()
    
    print("3. 🚀 For production deployment:")
    print("   a. Update callback URL to production domain")
    print("   b. Use HTTPS for security")
    print("   c. Example: https://your-domain.com/callback")
    print()
    
    print("4. 🧪 Testing different ports:")
    ports = [8501, 8502, 8503, 8504, 8505]
    print("   Common development ports:")
    for port in ports:
        url = f"http://localhost:{port}/callback"
        print(f"   - Port {port}: {url}")
    
    print("\n" + "=" * 50)
    print("🔧 Quick Port Update:")
    
    try:
        new_port = input("\nEnter new port number (or press Enter to skip): ").strip()
        
        if new_port:
            if not new_port.isdigit():
                print("❌ Invalid port number")
                return
            
            new_url = f"http://localhost:{new_port}/callback"
            is_valid, message = validate_callback_url(new_url)
            
            if is_valid:
                print(f"✅ New callback URL: {new_url}")
                
                # Update .env.local file
                env_file = '.env.local'
                if os.path.exists(env_file):
                    with open(env_file, 'r') as f:
                        content = f.read()
                    
                    # Replace the callback URL
                    pattern = r'GITLAB_REDIRECT_URI=.*'
                    replacement = f'GITLAB_REDIRECT_URI={new_url}'
                    
                    if re.search(pattern, content):
                        new_content = re.sub(pattern, replacement, content)
                        
                        with open(env_file, 'w') as f:
                            f.write(new_content)
                        
                        print(f"✅ Updated {env_file} with new callback URL")
                        print("🔄 Please restart your Streamlit app for changes to take effect")
                    else:
                        print(f"❌ Could not find GITLAB_REDIRECT_URI in {env_file}")
                else:
                    print(f"❌ {env_file} not found")
            else:
                print(f"❌ {message}")
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()