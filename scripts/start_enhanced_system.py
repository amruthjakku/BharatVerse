#!/usr/bin/env python3
"""
Enhanced startup script for BharatVerse
Starts the enhanced API server and Streamlit app with real AI capabilities
"""

import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path
import requests
import json

class BharatVerseSystem:
    def __init__(self):
        self.api_process = None
        self.streamlit_process = None
        self.running = False
        
    def check_dependencies(self):
        """Check if all dependencies are installed"""
        print("🔍 Checking dependencies...")
        
        missing_deps = []
        
        # Check core dependencies
        try:
            import streamlit
            print("✅ Streamlit available")
        except ImportError:
            missing_deps.append("streamlit")
        
        try:
            import fastapi
            print("✅ FastAPI available")
        except ImportError:
            missing_deps.append("fastapi")
        
        # Check AI dependencies
        try:
            import torch
            print("✅ PyTorch available")
        except ImportError:
            missing_deps.append("torch")
        
        try:
            import whisper
            print("✅ Whisper available")
        except ImportError:
            missing_deps.append("openai-whisper")
        
        try:
            import transformers
            print("✅ Transformers available")
        except ImportError:
            missing_deps.append("transformers")
        
        if missing_deps:
            print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
            print("Run the installation script first:")
            print("python install_ai_dependencies.py")
            return False
        
        print("✅ All dependencies available")
        return True
    
    def start_api_server(self):
        """Start the enhanced API server"""
        print("\n🚀 Starting Enhanced API Server...")
        
        try:
            # Set environment for local development
            env = os.environ.copy()
            
            # Load local environment file if it exists
            local_env_path = Path(".env.local")
            if local_env_path.exists():
                try:
                    from dotenv import load_dotenv
                    load_dotenv(".env.local", override=True)
                    print("✅ Loaded local environment configuration")
                except ImportError:
                    print("⚠️  python-dotenv not available, using system environment")
            
            # Check if enhanced API exists
            api_file = Path(__file__).parent / "api" / "enhanced_main.py"
            if not api_file.exists():
                print("❌ Enhanced API file not found. Using fallback API...")
                api_file = Path(__file__).parent / "api" / "main.py"
            
            # Start API server
            cmd = [
                sys.executable, 
                str(api_file),
                "--host", "0.0.0.0",
                "--port", "8000"
            ]
            
            self.api_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            
            # Wait for API to start
            print("⏳ Waiting for API server to start...")
            for i in range(30):  # Wait up to 30 seconds
                try:
                    response = requests.get("http://localhost:8000/health", timeout=2)
                    if response.status_code == 200:
                        print("✅ API server started successfully")
                        health_data = response.json()
                        print(f"   Version: {health_data.get('version', 'unknown')}")
                        
                        # Show AI model status
                        ai_models = health_data.get('ai_models', {})
                        if ai_models:
                            print("   AI Models:")
                            for model, status in ai_models.items():
                                if isinstance(status, dict):
                                    for sub_model, sub_status in status.items():
                                        print(f"     {sub_model}: {'✅' if sub_status else '❌'}")
                                else:
                                    print(f"     {model}: {'✅' if status else '❌'}")
                        
                        return True
                except requests.exceptions.RequestException:
                    time.sleep(1)
            
            print("❌ API server failed to start within 30 seconds")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start API server: {e}")
            return False
    
    def start_streamlit_app(self):
        """Start the Streamlit application"""
        print("\n🎨 Starting Streamlit Application...")
        
        try:
            app_file = Path(__file__).parent / "streamlit_app" / "app.py"
            
            cmd = [
                sys.executable, "-m", "streamlit", "run",
                str(app_file),
                "--server.port=8501",
                "--server.address=0.0.0.0",
                "--server.headless=true"
            ]
            
            self.streamlit_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for Streamlit to start
            print("⏳ Waiting for Streamlit to start...")
            time.sleep(5)  # Streamlit takes a bit longer to start
            
            try:
                response = requests.get("http://localhost:8501", timeout=5)
                if response.status_code == 200:
                    print("✅ Streamlit app started successfully")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            # Check if process is still running
            if self.streamlit_process.poll() is None:
                print("✅ Streamlit app is starting...")
                return True
            else:
                print("❌ Streamlit app failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start Streamlit app: {e}")
            return False
    
    def monitor_processes(self):
        """Monitor running processes"""
        while self.running:
            time.sleep(5)
            
            # Check API process
            if self.api_process and self.api_process.poll() is not None:
                print("⚠️  API server stopped unexpectedly")
                self.running = False
                break
            
            # Check Streamlit process
            if self.streamlit_process and self.streamlit_process.poll() is not None:
                print("⚠️  Streamlit app stopped unexpectedly")
                self.running = False
                break
    
    def stop_all(self):
        """Stop all processes"""
        print("\n🛑 Stopping BharatVerse system...")
        self.running = False
        
        if self.api_process:
            print("   Stopping API server...")
            self.api_process.terminate()
            try:
                self.api_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.api_process.kill()
        
        if self.streamlit_process:
            print("   Stopping Streamlit app...")
            self.streamlit_process.terminate()
            try:
                self.streamlit_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.streamlit_process.kill()
        
        print("✅ System stopped")
    
    def start_system(self):
        """Start the complete system"""
        print("🇮🇳 BharatVerse Enhanced System Startup")
        print("=" * 60)
        
        # Check dependencies
        if not self.check_dependencies():
            return False
        
        # Start API server
        if not self.start_api_server():
            return False
        
        # Start Streamlit app
        if not self.start_streamlit_app():
            self.stop_all()
            return False
        
        self.running = True
        
        # Show access information
        print("\n" + "=" * 60)
        print("🎉 BharatVerse System Started Successfully!")
        print("=" * 60)
        print("\n📱 Access URLs:")
        print("   🎨 Streamlit App: http://localhost:8501")
        print("   🔧 API Server:    http://localhost:8000")
        print("   📚 API Docs:      http://localhost:8000/docs")
        
        print("\n🤖 AI Features:")
        print("   • Toggle 'Use Real Data' in the sidebar to enable AI models")
        print("   • Real-time audio transcription with Whisper")
        print("   • Advanced text analysis and translation")
        print("   • AI-powered image captioning and analysis")
        
        print("\n💡 Tips:")
        print("   • First AI model usage may be slow (models loading)")
        print("   • Ensure microphone permissions for audio recording")
        print("   • Use Ctrl+C to stop the system")
        
        # Start monitoring in background
        monitor_thread = threading.Thread(target=self.monitor_processes)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        return True
    
    def run(self):
        """Run the system with signal handling"""
        def signal_handler(signum, frame):
            print(f"\n\n🛑 Received signal {signum}")
            self.stop_all()
            sys.exit(0)
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        if self.start_system():
            try:
                # Keep the main thread alive
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            finally:
                self.stop_all()
        else:
            print("❌ Failed to start system")
            sys.exit(1)

def main():
    """Main entry point"""
    system = BharatVerseSystem()
    system.run()

if __name__ == "__main__":
    main()