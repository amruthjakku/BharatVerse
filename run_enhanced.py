#!/usr/bin/env python3
"""
Enhanced BharatVerse Launcher
Starts both the Streamlit app and FastAPI server
"""

import subprocess
import sys
import time
import os
from pathlib import Path
import threading
import signal

def install_dependencies():
    """Install required dependencies"""
    print("🔧 Installing dependencies...")
    
    try:
        # Install core dependencies
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements_core.txt"
        ], check=True)
        
        # Install API dependencies
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "api/requirements.txt"
        ], check=True)
        
        print("✅ Dependencies installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def start_api_server():
    """Start the FastAPI server"""
    print("🚀 Starting API server...")
    
    try:
        os.chdir("api")
        subprocess.run([
            sys.executable, "-m", "uvicorn", "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 API server stopped")
    except Exception as e:
        print(f"❌ Error starting API server: {e}")
    finally:
        os.chdir("..")

def start_streamlit_app():
    """Start the Streamlit application"""
    print("🌟 Starting Streamlit app...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app/app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Streamlit app stopped")
    except Exception as e:
        print(f"❌ Error starting Streamlit app: {e}")

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment not detected. Consider using a virtual environment.")
    
    # Check if required files exist
    required_files = [
        "streamlit_app/app.py",
        "api/main.py",
        "requirements_core.txt",
        "api/requirements.txt"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ Required file not found: {file_path}")
            return False
    
    print("✅ All requirements met!")
    return True

def show_banner():
    """Display application banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║                    🇮🇳 BharatVerse Enhanced                    ║
    ║                                                              ║
    ║              Preserving India's Culture with AI             ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    
    🌟 Enhanced Features:
    • 🔍 Advanced Search & Discovery
    • 📊 Real-time Analytics Dashboard  
    • 🤝 Community Collaboration Hub
    • 🤖 AI-Powered Cultural Insights
    • 👥 Project Management Tools
    • 🌐 Professional REST API
    
    """
    print(banner)

def show_urls():
    """Display application URLs"""
    urls = """
    🌐 Application URLs:
    
    📱 Streamlit App:    http://localhost:8501
    🔧 API Server:       http://localhost:8000
    📚 API Docs:         http://localhost:8000/docs
    🔍 API Redoc:        http://localhost:8000/redoc
    
    """
    print(urls)

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n🛑 Shutting down BharatVerse Enhanced...")
    print("Thank you for preserving India's cultural heritage! 🙏")
    sys.exit(0)

def main():
    """Main launcher function"""
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Show banner
    show_banner()
    
    # Check requirements
    if not check_requirements():
        print("❌ Requirements check failed. Please fix the issues and try again.")
        sys.exit(1)
    
    # Ask user if they want to install dependencies
    install_deps = input("📦 Install/update dependencies? (y/N): ").lower().strip()
    if install_deps in ['y', 'yes']:
        if not install_dependencies():
            print("❌ Failed to install dependencies. Exiting.")
            sys.exit(1)
    
    # Show URLs
    show_urls()
    
    print("🚀 Starting BharatVerse Enhanced...")
    print("Press Ctrl+C to stop all services")
    print("-" * 60)
    
    # Start API server in a separate thread
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    
    # Give API server time to start
    time.sleep(3)
    
    # Start Streamlit app (this will block)
    try:
        start_streamlit_app()
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()