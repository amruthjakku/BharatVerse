#!/usr/bin/env python3
"""
BharatVerse System Startup Script
Starts the API server and Streamlit frontend
"""

import subprocess
import sys
import os
import time
import threading
from pathlib import Path

def run_api_server():
    """Run the FastAPI server"""
    print("🚀 Starting BharatVerse API server...")
    
    # Change to the project directory
    os.chdir(Path(__file__).parent)
    
    # Run the API server
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "core.api_service:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ API server failed to start: {e}")
        sys.exit(1)

def run_streamlit_app():
    """Run the Streamlit frontend"""
    print("🎨 Starting BharatVerse Streamlit app...")
    
    # Change to the project directory
    os.chdir(Path(__file__).parent)
    
    # Wait a moment for the API server to start
    time.sleep(5)
    
    # Run the Streamlit app
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_app/app.py", 
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Streamlit app failed to start: {e}")
        sys.exit(1)

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'streamlit', 'fastapi', 'uvicorn', 'requests', 
        'pandas', 'numpy', 'plotly', 'psycopg2'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("📦 Please install them with: uv pip install -e .")
        sys.exit(1)
    
    print("✅ All dependencies are installed!")

def main():
    """Main function to start the system"""
    print("🇮🇳 BharatVerse - Cultural Heritage Preservation Platform")
    print("=" * 60)
    
    # Check dependencies
    check_dependencies()
    
    # Start API server in a separate thread
    api_thread = threading.Thread(target=run_api_server, daemon=True)
    api_thread.start()
    
    # Start Streamlit app (this will block)
    try:
        run_streamlit_app()
    except KeyboardInterrupt:
        print("\n👋 Shutting down BharatVerse system...")
        sys.exit(0)

if __name__ == "__main__":
    main()
