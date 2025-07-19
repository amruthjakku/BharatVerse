#!/usr/bin/env python3
"""
Setup script for BharatVerse Free Cloud Deployment
Prepares the application for deployment on Streamlit Cloud with free cloud services
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def print_step(step_num: int, description: str):
    """Print formatted step description"""
    print(f"\n🚀 Step {step_num}: {description}")
    print("=" * 50)

def print_success(message: str):
    """Print success message"""
    print(f"✅ {message}")

def print_warning(message: str):
    """Print warning message"""
    print(f"⚠️  {message}")

def print_error(message: str):
    """Print error message"""
    print(f"❌ {message}")

def check_file_exists(filepath: str) -> bool:
    """Check if file exists"""
    return Path(filepath).exists()

def create_directory(dirpath: str):
    """Create directory if it doesn't exist"""
    Path(dirpath).mkdir(parents=True, exist_ok=True)
    print_success(f"Directory created/verified: {dirpath}")

def copy_file(source: str, destination: str):
    """Copy file from source to destination"""
    try:
        import shutil
        shutil.copy2(source, destination)
        print_success(f"File copied: {source} -> {destination}")
    except Exception as e:
        print_error(f"Failed to copy {source}: {e}")

def create_streamlit_config():
    """Create Streamlit configuration for cloud deployment"""
    print_step(1, "Creating Streamlit Configuration")
    
    # Create .streamlit directory
    streamlit_dir = ".streamlit"
    create_directory(streamlit_dir)
    
    # Create config.toml
    config_content = """[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFEAA7"
secondaryBackgroundColor = "#FDCB6E"
textColor = "#2D3436"

[server]
enableCORS = false
enableXsrfProtection = false
maxUploadSize = 50

[browser]
gatherUsageStats = false
"""
    
    config_path = f"{streamlit_dir}/config.toml"
    with open(config_path, 'w') as f:
        f.write(config_content)
    print_success(f"Created: {config_path}")

def create_cloud_requirements():
    """Create requirements file optimized for cloud deployment"""
    print_step(2, "Creating Cloud Requirements File")
    
    # Use the cloud requirements we created earlier
    if check_file_exists("requirements_cloud.txt"):
        print_success("Cloud requirements file already exists")
    else:
        print_warning("Cloud requirements file not found. Using default requirements.txt")

def create_runtime_txt():
    """Create runtime.txt for Python version"""
    print_step(3, "Creating Runtime Configuration")
    
    runtime_content = "python-3.11.5\n"
    
    with open("runtime.txt", 'w') as f:
        f.write(runtime_content)
    print_success("Created: runtime.txt")

def create_packages_txt():
    """Create packages.txt for system packages"""
    print_step(4, "Creating System Packages Configuration")
    
    packages_content = """# System packages required for BharatVerse
libsndfile1
ffmpeg
libsm6
libxext6
libxrender-dev
libgomp1
"""
    
    with open("packages.txt", 'w') as f:
        f.write(packages_content)
    print_success("Created: packages.txt")

def create_cloud_optimized_app():
    """Create a cloud-optimized version of the main app"""
    print_step(5, "Creating Cloud-Optimized Application")
    
    # Check if Home.py exists and create cloud version
    if check_file_exists("Home.py"):
        print_success("Home.py found - will be used as main entry point")
    else:
        print_warning("Home.py not found - creating basic version")
        
        home_content = """import streamlit as st
from core.cloud_ai_manager import get_cloud_ai_manager

# Configure page
st.set_page_config(
    page_title="BharatVerse - Cultural Heritage Platform",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize cloud AI manager
ai_manager = get_cloud_ai_manager()

# Main content
st.title("🏛️ BharatVerse - Cultural Heritage Platform")
st.markdown("### Preserving India's Rich Cultural Legacy with AI")

# System status
with st.expander("🔧 System Status"):
    status = ai_manager.get_system_status()
    st.json(status)

st.markdown('''
Welcome to BharatVerse - a platform for preserving and sharing India's cultural heritage using advanced AI technology.

**Features:**
- 🎵 **Audio Transcription**: Convert cultural audio content to text
- 📝 **Text Analysis**: Analyze cultural texts for sentiment and context  
- 📸 **Image Analysis**: Understand cultural images and artifacts
- 🌐 **Translation**: Translate content between languages
- 📊 **Analytics**: Track cultural preservation efforts

**Navigate using the sidebar to explore different features.**
''')

# Footer
st.markdown("---")
st.markdown("Built with ❤️ for preserving cultural heritage | Powered by free cloud services")
"""
        
        with open("Home.py", 'w') as f:
            f.write(home_content)
        print_success("Created: Home.py")

def create_gitignore():
    """Create .gitignore file"""
    print_step(6, "Creating .gitignore")
    
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/

# Streamlit
.streamlit/secrets.toml

# Local files
*.env
.env.local
.env.production

# Logs
*.log

# Database
*.db
*.sqlite3

# Cache
.cache/
.pytest_cache/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Local development
docker-compose.override.yml
local_models/
temp/
"""
    
    with open(".gitignore", 'w') as f:
        f.write(gitignore_content)
    print_success("Created: .gitignore")

def create_readme():
    """Create README for cloud deployment"""
    print_step(7, "Creating Deployment README")
    
    readme_content = """# 🏛️ BharatVerse - Free Cloud Deployment

A scalable cultural heritage platform using **100% free cloud services**.

## 🌐 Architecture

```
[🧑‍💻 User] → [🌐 Streamlit Cloud] → [🔮 HF Spaces] + [🐘 Supabase] + [⚡ Upstash] + [🪣 R2]
```

## 🚀 Free Services Used

- **Frontend**: Streamlit Cloud (Free)
- **AI Processing**: Hugging Face Inference API (Free tier)
- **Database**: Supabase PostgreSQL (500MB free)
- **Cache**: Upstash Redis (10k commands/day free)
- **Storage**: Cloudflare R2 (10GB free)

## 📦 Deployment Steps

1. **Fork this repository**
2. **Set up free services**:
   - Create Supabase project
   - Create Upstash Redis instance
   - Create Cloudflare R2 bucket
   - Get Hugging Face token
3. **Deploy to Streamlit Cloud**:
   - Connect GitHub repository
   - Add secrets from `streamlit_secrets_template.toml`
   - Deploy!

## 🔧 Configuration

Copy `streamlit_secrets_template.toml` to Streamlit Cloud secrets and fill in your values.

## 💰 Cost

**$0/month** - Everything runs on free tiers!

## 📚 Documentation

See `Free_Cloud_Deployment.md` for detailed setup instructions.

## 🎯 Features

- Real AI-powered audio transcription
- Intelligent text analysis with cultural context
- Advanced image processing and captioning
- Multi-language translation support
- Real-time analytics and monitoring
- User authentication and profiles
- Community features and collaboration

---

Built with ❤️ for preserving cultural heritage
"""
    
    with open("README_CLOUD_DEPLOY.md", 'w') as f:
        f.write(readme_content)
    print_success("Created: README_CLOUD_DEPLOY.md")

def validate_setup():
    """Validate the cloud deployment setup"""
    print_step(8, "Validating Setup")
    
    required_files = [
        "Home.py",
        "requirements_cloud.txt", 
        "runtime.txt",
        "packages.txt",
        ".streamlit/config.toml",
        "streamlit_secrets_template.toml",
        "utils/r2.py",
        "utils/db.py", 
        "utils/inference.py",
        "utils/redis_cache.py",
        "core/cloud_ai_manager.py"
    ]
    
    missing_files = []
    
    for file in required_files:
        if check_file_exists(file):
            print_success(f"Found: {file}")
        else:
            print_error(f"Missing: {file}")
            missing_files.append(file)
    
    if missing_files:
        print_warning(f"Missing {len(missing_files)} required files. Please check your setup.")
        return False
    else:
        print_success("All required files are present!")
        return True

def show_next_steps():
    """Show next steps for deployment"""
    print_step(9, "Next Steps")
    
    print("""
🎉 **Setup Complete!** Your BharatVerse application is ready for free cloud deployment.

**Next Steps:**

1. **Set up free cloud services:**
   - Supabase: https://supabase.com (PostgreSQL)
   - Upstash: https://upstash.com (Redis)  
   - Cloudflare R2: https://cloudflare.com (Storage)
   - Hugging Face: https://huggingface.co (AI API token)

2. **Deploy to Streamlit Cloud:**
   - Push code to GitHub
   - Go to https://share.streamlit.io
   - Connect your repository
   - Set main file to: `Home.py`
   - Copy secrets from `streamlit_secrets_template.toml` to Streamlit secrets

3. **Test your deployment:**
   - Verify all features work
   - Check AI processing
   - Test file uploads
   - Monitor analytics

**Documentation:**
- Setup Guide: `Free_Cloud_Deployment.md`
- Secrets Template: `streamlit_secrets_template.toml` 
- Cloud README: `README_CLOUD_DEPLOY.md`

**Total Monthly Cost: $0** 🎉

Your cultural heritage platform is ready to scale with free cloud services!
    """)

def main():
    """Main setup function"""
    print("🏛️ BharatVerse Free Cloud Deployment Setup")
    print("=" * 60)
    
    try:
        create_streamlit_config()
        create_cloud_requirements()
        create_runtime_txt()
        create_packages_txt() 
        create_cloud_optimized_app()
        create_gitignore()
        create_readme()
        
        if validate_setup():
            show_next_steps()
        else:
            print_error("Setup validation failed. Please check the errors above.")
            sys.exit(1)
            
    except Exception as e:
        print_error(f"Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()