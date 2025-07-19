#!/usr/bin/env python3
"""
BharatVerse Free Deployment Setup
Prepares the application for zero-cost deployment
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def main():
    print("🆓 BharatVerse - Free Deployment Setup")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("\n🎯 Preparing for 100% FREE deployment...")
    
    # Create free tier requirements
    print("📦 Creating optimized requirements...")
    
    # Update Home.py for free tier
    print("⚙️ Configuring for free tier...")
    
    # Check if we need to modify the AI imports
    home_py = Path("Home.py")
    if home_py.exists():
        content = home_py.read_text()
        if "enhanced_ai_models" in content and "free_tier_ai" not in content:
            # Add free tier AI import
            new_content = content.replace(
                "# Import styling and authentication",
                """# Import AI manager based on deployment mode
try:
    if os.getenv("AI_MODE", "free_tier") == "free_tier":
        from core.free_tier_ai import get_ai_manager
    else:
        from core.enhanced_ai_models import get_ai_manager
except ImportError:
    from core.free_tier_ai import get_ai_manager

# Import styling and authentication"""
            )
            home_py.write_text(new_content)
            print("✅ Home.py configured for free tier")
    
    # Create deployment-specific files
    deployment_files = {
        "requirements.txt": "requirements_free.txt",
        "Procfile": "web: streamlit run Home.py --server.port=$PORT --server.address=0.0.0.0",
        "runtime.txt": "python-3.11.6",
        "app.json": {
            "name": "BharatVerse",
            "description": "Digital Cultural Heritage Platform with AI",
            "repository": "https://github.com/YOUR_USERNAME/bharatverse",
            "keywords": ["streamlit", "ai", "cultural-heritage", "india"],
            "env": {
                "AI_MODE": {
                    "description": "AI deployment mode",
                    "value": "free_tier"
                },
                "USE_LIGHTWEIGHT_MODELS": {
                    "description": "Use lightweight AI models",
                    "value": "true"
                }
            },
            "formation": {
                "web": {
                    "quantity": 1,
                    "size": "free"
                }
            },
            "addons": [
                "heroku-postgresql:mini"
            ]
        }
    }
    
    # Copy requirements for free tier
    if Path("requirements_free.txt").exists():
        import shutil
        shutil.copy("requirements_free.txt", "requirements.txt")
        print("✅ Free tier requirements copied")
    
    # Create Procfile for Heroku-style deployments
    with open("Procfile", "w") as f:
        f.write("web: streamlit run Home.py --server.port=$PORT --server.address=0.0.0.0\n")
    print("✅ Procfile created")
    
    # Create runtime.txt
    with open("runtime.txt", "w") as f:
        f.write("python-3.11.6\n")
    print("✅ Runtime configuration created")
    
    # Create app.json for one-click deployments
    with open("app.json", "w") as f:
        json.dump(deployment_files["app.json"], f, indent=2)
    print("✅ App configuration created")
    
    # Create .env.example for free tier
    env_example = """# Free Tier Environment Variables
AI_MODE=free_tier
USE_LIGHTWEIGHT_MODELS=true
DEPLOYMENT_MODE=free

# Database (will be auto-configured by platform)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=bharatverse_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=bharatverse

# Security
SECRET_KEY=your-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Optional: GitLab OAuth
GITLAB_CLIENT_ID=your_client_id
GITLAB_CLIENT_SECRET=your_client_secret
GITLAB_REDIRECT_URI=https://your-app.railway.app/auth/callback
"""
    
    with open(".env.example", "w") as f:
        f.write(env_example)
    print("✅ Environment example created")
    
    # Check git status
    print("\n📚 Checking Git repository...")
    try:
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git repository ready")
            
            # Check for GitHub remote
            result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
            if 'github.com' in result.stdout:
                print("✅ GitHub remote configured")
                github_ready = True
            else:
                print("⚠️ No GitHub remote found")
                github_ready = False
        else:
            print("❌ Not a git repository")
            github_ready = False
    except FileNotFoundError:
        print("❌ Git not found")
        github_ready = False
    
    print("\n🎉 Free Deployment Setup Complete!")
    print("=" * 50)
    
    print("\n🚀 Choose Your FREE Deployment Platform:")
    print("\n1. 🚂 Railway.app (Recommended)")
    print("   • 8GB RAM, 100GB storage")
    print("   • Go to: https://railway.app")
    print("   • Deploy from GitHub repo")
    print("   • Add PostgreSQL database")
    print("   • Your app will be live!")
    
    print("\n2. 🎨 Render.com")
    print("   • Go to: https://render.com")
    print("   • New → Blueprint")
    print("   • Connect GitHub repo")
    print("   • Auto-deploy with render.yaml")
    
    print("\n3. 🪂 Fly.io")
    print("   • Install: brew install flyctl")
    print("   • Run: flyctl deploy")
    print("   • Add database: flyctl postgres create")
    
    print("\n4. ☁️ Streamlit Cloud")
    print("   • Go to: https://share.streamlit.io")
    print("   • Connect GitHub repo")
    print("   • Set main file: Home.py")
    print("   • Add database secrets")
    
    if not github_ready:
        print("\n⚠️ FIRST: Set up GitHub repository")
        print("1. Create repo at: https://github.com/new")
        print("2. Make it PUBLIC (required for free tiers)")
        print("3. Run these commands:")
        print("   git remote add origin https://github.com/YOUR_USERNAME/bharatverse.git")
        print("   git add .")
        print("   git commit -m 'Ready for free deployment'")
        print("   git push -u origin main")
    else:
        print("\n✅ Ready to deploy! Just push your changes:")
        print("   git add .")
        print("   git commit -m 'Configured for free deployment'")
        print("   git push origin main")
    
    print("\n💡 What you'll get (100% FREE):")
    print("   ✅ Professional web application")
    print("   ✅ PostgreSQL database")
    print("   ✅ AI-powered text analysis")
    print("   ✅ Cultural heritage features")
    print("   ✅ File upload capabilities")
    print("   ✅ Real-time analytics")
    print("   ✅ HTTPS & custom domain")
    print("   ✅ Global CDN")
    
    print(f"\n🎯 Total cost: $0 forever!")
    print("🚀 Your cultural heritage platform will be live in 10 minutes!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)