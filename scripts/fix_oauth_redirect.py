#!/usr/bin/env python3
"""
Fix OAuth Redirect URI Configuration
This script helps update the OAuth configuration for different environments
"""

import os
import sys
from pathlib import Path

def main():
    print("🔧 OAuth Redirect URI Configuration Fix")
    print("=" * 50)
    
    # Get project root
    project_root = Path(__file__).parent.parent
    
    print("\n📋 Current Configuration:")
    print(f"Local .env file: {project_root / '.env'}")
    
    # Read current .env
    env_file = project_root / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
        
        print("\nCurrent GitLab OAuth settings in .env:")
        for line in content.split('\n'):
            if line.startswith(('GITLAB_', 'APP_ENV')):
                print(f"  {line}")
    
    print("\n🌍 Environment Detection:")
    print("Based on your debug output, you're running on Streamlit Cloud")
    print("Detected redirect URI: https://amruth-bharatverse.streamlit.app/callback")
    
    print("\n🔧 Required Actions:")
    print("1. Update GitLab OAuth Application:")
    print("   - Go to: https://code.swecha.org/-/profile/applications")
    print("   - Find your application with Client ID: 3a7ccf98f1...")
    print("   - Update Redirect URI to: https://amruth-bharatverse.streamlit.app/callback")
    
    print("\n2. Streamlit Cloud Secrets Configuration:")
    print("   Add these secrets in your Streamlit Cloud dashboard:")
    print("   [gitlab]")
    print("   client_id = \"3a7ccf98f197e891fc2fbff9f4841e4d54c6f069f901bed75b86f1bebf123f95\"")
    print("   client_secret = \"gloas-45d17f9456ef8e6831ae5b7c74af71d1d316c46fe8001a622ba184bdcf688a8a\"")
    print("   base_url = \"https://code.swecha.org\"")
    print("   redirect_uri = \"https://amruth-bharatverse.streamlit.app/callback\"")
    print("   scopes = \"api read_user profile email\"")
    print("   ")
    print("   [app]")
    print("   APP_ENV = \"streamlit_cloud\"")
    print("   debug = true")
    
    print("\n3. Alternative: Support Multiple Redirect URIs")
    print("   You can configure multiple redirect URIs in GitLab:")
    print("   - http://localhost:8501/callback (for local development)")
    print("   - https://amruth-bharatverse.streamlit.app/callback (for production)")
    
    print("\n✅ After making these changes:")
    print("1. The OAuth authentication should work properly")
    print("2. The 401 'invalid_client' error should be resolved")
    print("3. Users will be able to login via GitLab")
    
    print("\n🔍 Testing:")
    print("1. Go to your Streamlit app")
    print("2. Navigate to the OAuth Debug page")
    print("3. Click the OAuth authorization link")
    print("4. Complete the GitLab login flow")
    
if __name__ == "__main__":
    main()