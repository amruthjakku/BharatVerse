#!/usr/bin/env python3
"""
Simple Test Startup Script for BharatVerse
Starts the simple API server and Streamlit app for testing
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def start_api_server():
    """Start the simple API server"""
    print("🚀 Starting Simple BharatVerse API Server...")
    
    # Change to the project directory
    os.chdir(Path(__file__).parent)
    
    # Start the API server in the background
    api_process = subprocess.Popen([
        sys.executable, "simple_api_server.py"
    ])
    
    return api_process

def start_streamlit_app():
    """Start the Streamlit app"""
    print("🎨 Starting BharatVerse Streamlit App...")
    
    # Change to the project directory
    os.chdir(Path(__file__).parent)
    
    # Start Streamlit app
    streamlit_process = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", 
        "streamlit_app/app.py", 
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ])
    
    return streamlit_process

def main():
    """Main function to start both services"""
    print("🇮🇳 BharatVerse - Testing Real Data Integration")
    print("=" * 60)
    
    # Start API server
    api_process = start_api_server()
    
    # Wait for API server to start
    print("⏳ Waiting for API server to start...")
    time.sleep(3)
    
    # Test API server
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running at http://localhost:8000")
        else:
            print("❌ API server is not responding properly")
    except Exception as e:
        print(f"❌ API server failed to start: {e}")
        api_process.terminate()
        sys.exit(1)
    
    # Start Streamlit app
    streamlit_process = start_streamlit_app()
    
    print("🎉 BharatVerse is starting up!")
    print("📡 API Server: http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    print("🎨 Streamlit App: http://localhost:8501")
    print()
    print("💡 To test real data integration:")
    print("   1. Open http://localhost:8501 in your browser")
    print("   2. Toggle 'Use Real Data' ON in the left sidebar")
    print("   3. You should see real data from the API instead of mock data")
    print()
    print("Press Ctrl+C to stop both services...")
    
    try:
        # Wait for both processes
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\\n👋 Shutting down BharatVerse services...")
        streamlit_process.terminate()
        api_process.terminate()
        
        # Wait for processes to terminate
        streamlit_process.wait()
        api_process.wait()
        
        print("✅ All services stopped successfully!")

if __name__ == "__main__":
    main()
