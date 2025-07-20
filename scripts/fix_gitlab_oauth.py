#!/usr/bin/env python3
"""
Fix GitLab OAuth Configuration Issues
Provides options to disable or configure GitLab OAuth
"""

import os
import sys
from pathlib import Path

def print_header():
    print("🦊 GitLab OAuth Configuration Fix")
    print("=" * 35)
    print("Fix GitLab OAuth configuration errors in your app")
    print()

def show_current_status():
    """Show current GitLab OAuth configuration status"""
    print("🔍 Current GitLab OAuth Status:")
    print("-" * 30)
    
    gitlab_vars = [
        'GITLAB_CLIENT_ID',
        'GITLAB_CLIENT_SECRET', 
        'GITLAB_REDIRECT_URI',
        'GITLAB_BASE_URL',
        'GITLAB_SCOPES'
    ]
    
    configured_count = 0
    for var in gitlab_vars:
        value = os.getenv(var)
        if value:
            configured_count += 1
            if 'SECRET' in var:
                print(f"✅ {var}: {value[:10]}...")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not configured")
    
    print()
    if configured_count == 0:
        print("⚠️  GitLab OAuth is not configured (causing errors)")
    elif configured_count < len(gitlab_vars):
        print(f"⚠️  Partial configuration ({configured_count}/{len(gitlab_vars)} variables)")
    else:
        print("✅ GitLab OAuth is fully configured")
    
    return configured_count == len(gitlab_vars)

def option_disable_gitlab():
    """Option 1: Disable GitLab OAuth"""
    print("🚫 Option 1: Disable GitLab OAuth")
    print("-" * 32)
    print("This will disable GitLab integration and remove the errors.")
    print("Your app will work without GitLab authentication.")
    print()
    
    choice = input("Disable GitLab OAuth? (y/N): ").lower().strip()
    
    if choice.startswith('y'):
        # Add environment variables to disable GitLab
        env_content = """
# GitLab OAuth - DISABLED
GITLAB_CLIENT_ID=
GITLAB_CLIENT_SECRET=
GITLAB_REDIRECT_URI=
GITLAB_BASE_URL=
GITLAB_SCOPES=
DISABLE_GITLAB_AUTH=true
"""
        
        # Update .env file
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file, "a") as f:
                f.write(env_content)
        else:
            with open(env_file, "w") as f:
                f.write("# BharatVerse Environment Configuration" + env_content)
        
        # Update secrets.toml
        secrets_file = Path(".streamlit/secrets.toml")
        if secrets_file.exists():
            with open(secrets_file, "a") as f:
                f.write("""
# GitLab OAuth - DISABLED
[gitlab]
enabled = false
disable_auth = true
""")
        
        print("✅ GitLab OAuth disabled successfully!")
        print("✅ Configuration files updated")
        print("✅ App should now run without GitLab errors")
        return True
    
    return False

def option_configure_gitlab():
    """Option 2: Configure GitLab OAuth"""
    print("🔧 Option 2: Configure GitLab OAuth")
    print("-" * 33)
    print("This will help you set up GitLab OAuth integration.")
    print()
    
    print("You'll need to:")
    print("1. Create a GitLab application at your GitLab instance")
    print("2. Get the Client ID and Client Secret")
    print("3. Set the redirect URI")
    print()
    
    choice = input("Configure GitLab OAuth? (y/N): ").lower().strip()
    
    if not choice.startswith('y'):
        return False
    
    print("\n📝 GitLab OAuth Configuration:")
    print("-" * 30)
    
    # Get configuration values
    base_url = input("GitLab Base URL [https://gitlab.com]: ").strip()
    if not base_url:
        base_url = "https://gitlab.com"
    
    client_id = input("GitLab Client ID: ").strip()
    if not client_id:
        print("❌ Client ID is required")
        return False
    
    client_secret = input("GitLab Client Secret: ").strip()
    if not client_secret:
        print("❌ Client Secret is required")
        return False
    
    redirect_uri = input("Redirect URI [http://localhost:8501/auth/callback]: ").strip()
    if not redirect_uri:
        redirect_uri = "http://localhost:8501/auth/callback"
    
    scopes = input("Scopes [api read_user profile email]: ").strip()
    if not scopes:
        scopes = "api read_user profile email"
    
    # Create configuration
    env_content = f"""
# GitLab OAuth Configuration
GITLAB_BASE_URL={base_url}
GITLAB_CLIENT_ID={client_id}
GITLAB_CLIENT_SECRET={client_secret}
GITLAB_REDIRECT_URI={redirect_uri}
GITLAB_SCOPES={scopes}
"""
    
    # Update .env file
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, "a") as f:
            f.write(env_content)
    else:
        with open(env_file, "w") as f:
            f.write("# BharatVerse Environment Configuration" + env_content)
    
    # Update secrets.toml
    secrets_file = Path(".streamlit/secrets.toml")
    secrets_file.parent.mkdir(exist_ok=True)
    
    secrets_content = f"""
# GitLab OAuth Configuration
[gitlab]
base_url = "{base_url}"
client_id = "{client_id}"
client_secret = "{client_secret}"
redirect_uri = "{redirect_uri}"
scopes = "{scopes}"
enabled = true
"""
    
    if secrets_file.exists():
        with open(secrets_file, "a") as f:
            f.write(secrets_content)
    else:
        with open(secrets_file, "w") as f:
            f.write("# BharatVerse Secrets Configuration" + secrets_content)
    
    print("\n✅ GitLab OAuth configured successfully!")
    print("✅ Configuration files updated")
    print("✅ App should now work with GitLab authentication")
    
    print("\n💡 Next steps:")
    print("1. Make sure your GitLab application has the correct redirect URI")
    print("2. Launch your app: streamlit run Home.py")
    print("3. Test GitLab login functionality")
    
    return True

def option_skip_for_now():
    """Option 3: Skip and run without GitLab"""
    print("⏭️  Option 3: Skip for now")
    print("-" * 23)
    print("Continue using the app without GitLab OAuth.")
    print("You can configure it later if needed.")
    print()
    
    # Set environment variable to suppress errors
    os.environ['DISABLE_GITLAB_AUTH'] = 'true'
    
    # Add to .env file
    env_file = Path(".env")
    env_content = "\n# Temporarily disable GitLab OAuth\nDISABLE_GITLAB_AUTH=true\n"
    
    if env_file.exists():
        with open(env_file, "a") as f:
            f.write(env_content)
    else:
        with open(env_file, "w") as f:
            f.write("# BharatVerse Environment Configuration" + env_content)
    
    print("✅ GitLab OAuth temporarily disabled")
    print("✅ App should run without GitLab errors")
    print("💡 You can configure GitLab OAuth later by running this script again")
    
    return True

def test_configuration():
    """Test the current configuration"""
    print("\n🧪 Testing Configuration...")
    print("-" * 25)
    
    try:
        # Test app import
        from Home import main
        print("✅ App imports successfully")
        
        # Test GitLab auth import
        from streamlit_app.utils.auth import GitLabAuth
        auth = GitLabAuth()
        print("✅ GitLab auth module loads")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Main function"""
    print_header()
    
    # Show current status
    is_configured = show_current_status()
    
    if is_configured:
        print("✅ GitLab OAuth is already configured!")
        print("If you're still seeing errors, try restarting your app.")
        return
    
    print("\n🎯 Choose an option:")
    print("1. 🚫 Disable GitLab OAuth (recommended for local development)")
    print("2. 🔧 Configure GitLab OAuth (for full integration)")
    print("3. ⏭️  Skip for now (temporary fix)")
    print()
    
    choice = input("Enter your choice (1/2/3): ").strip()
    
    success = False
    
    if choice == "1":
        success = option_disable_gitlab()
    elif choice == "2":
        success = option_configure_gitlab()
    elif choice == "3":
        success = option_skip_for_now()
    else:
        print("❌ Invalid choice")
        return
    
    if success:
        print("\n🎉 Configuration Updated!")
        print("=" * 25)
        
        if test_configuration():
            print("✅ All tests passed!")
            print("\n🚀 Ready to launch:")
            print("   streamlit run Home.py")
        else:
            print("⚠️  Some issues detected, but configuration was updated.")
            print("Try launching the app to see if it works.")

if __name__ == "__main__":
    main()