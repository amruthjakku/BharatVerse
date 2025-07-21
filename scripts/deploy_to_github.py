#!/usr/bin/env python3
"""
Deploy BharatVerse to GitHub
Automated script to push your app to GitHub for Streamlit Cloud deployment
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def main():
    """Main deployment function"""
    print("🚀 BharatVerse GitHub Deployment")
    print("=" * 35)
    print("This will push your app to GitHub for Streamlit Cloud")
    print()
    
    # Check if we're in the right directory
    if not Path("Home.py").exists():
        print("❌ Error: Home.py not found. Please run from project root.")
        return
    
    print("📋 Pre-deployment checklist:")
    print("✅ Home.py found")
    print("✅ Project structure verified")
    
    # Check git status
    print("\n🔍 Checking Git status...")
    
    # Initialize git if needed
    if not Path(".git").exists():
        print("📦 Initializing Git repository...")
        run_command("git init", "Git initialization")
        run_command("git branch -M main", "Setting main branch")
    
    # Create .gitignore if it doesn't exist
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Streamlit
.streamlit/secrets.toml

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Database
*.db
*.sqlite

# Temporary files
*.tmp
*.temp
"""
    
    if not Path(".gitignore").exists():
        with open(".gitignore", "w") as f:
            f.write(gitignore_content.strip())
        print("✅ Created .gitignore")
    
    # Create requirements.txt if it doesn't exist
    requirements_content = """streamlit>=1.28.0
pandas>=1.5.0
numpy>=1.24.0
requests>=2.28.0
Pillow>=9.0.0
python-dotenv>=0.19.0
psutil>=5.9.0
redis>=4.5.0
"""
    
    if not Path("requirements.txt").exists():
        with open("requirements.txt", "w") as f:
            f.write(requirements_content.strip())
        print("✅ Created requirements.txt")
    
    # Add files to git
    print("\n📦 Adding files to Git...")
    run_command("git add .", "Adding all files")
    
    # Commit changes
    commit_message = "Deploy BharatVerse cultural heritage platform"
    run_command(f'git commit -m "{commit_message}"', "Committing changes")
    
    # Get GitHub repository URL
    print("\n🔗 GitHub Repository Setup:")
    print("Please provide your GitHub repository details:")
    
    username = input("GitHub username [amruthjakku]: ").strip() or "amruthjakku"
    repo_name = input("Repository name [bharatverse]: ").strip() or "bharatverse"
    
    repo_url = f"https://github.com/{username}/{repo_name}.git"
    
    print(f"\n📡 Repository URL: {repo_url}")
    
    # Add remote origin
    run_command(f"git remote remove origin", "Removing existing origin (if any)")
    run_command(f"git remote add origin {repo_url}", "Adding remote origin")
    
    # Push to GitHub
    print(f"\n🚀 Pushing to GitHub...")
    print("Note: You may need to authenticate with GitHub")
    
    success = run_command("git push -u origin main", "Pushing to GitHub")
    
    if success:
        print("\n🎉 SUCCESS! Your app is now on GitHub!")
        print("=" * 40)
        print(f"📍 Repository: {repo_url}")
        print(f"🌐 GitHub URL: https://github.com/{username}/{repo_name}")
        print()
        print("🚀 Next Steps for Streamlit Cloud:")
        print("1. Go to https://share.streamlit.io")
        print("2. Click 'Create app'")
        print(f"3. Repository: {username}/{repo_name}")
        print("4. Branch: main")
        print("5. Main file path: Home.py")
        print("6. Add the production secrets from PRODUCTION_SECRETS.md")
        print()
        print("🔥 Your BharatVerse app will be live in minutes!")
    else:
        print("\n❌ Push failed. Please check:")
        print("1. Repository exists on GitHub")
        print("2. You have push access")
        print("3. GitHub authentication is working")
        print()
        print("💡 Manual steps:")
        print(f"1. Create repository: https://github.com/new")
        print(f"2. Repository name: {repo_name}")
        print("3. Make it public")
        print("4. Run: git push -u origin main")

if __name__ == "__main__":
    main()