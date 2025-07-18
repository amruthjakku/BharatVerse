#!/usr/bin/env python3
"""
Docker startup script for BharatVerse Enhanced System
Manages the complete Docker deployment with all services
"""

import subprocess
import sys
import os
import time
import signal
import requests
import json
from pathlib import Path

class DockerBharatVerseSystem:
    def __init__(self):
        self.running = False
        
    def check_docker(self):
        """Check if Docker is available and running"""
        print("🐳 Checking Docker...")
        
        try:
            # Check if Docker is installed
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Docker is not installed")
                return False
            print(f"✅ {result.stdout.strip()}")
            
            # Check if Docker is running
            result = subprocess.run(['docker', 'info'], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Docker is not running. Please start Docker Desktop.")
                return False
            print("✅ Docker is running")
            
            # Check if Docker Compose is available
            result = subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Docker Compose is not available")
                return False
            print(f"✅ {result.stdout.strip()}")
            
            return True
            
        except FileNotFoundError:
            print("❌ Docker is not installed")
            return False
    
    def create_directories(self):
        """Create necessary directories"""
        print("📁 Creating directories...")
        
        directories = [
            "models_cache",
            "docker"
        ]
        
        for directory in directories:
            dir_path = Path(directory)
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created directory: {directory}")
            else:
                print(f"✅ Directory exists: {directory}")
    
    def build_images(self):
        """Build Docker images"""
        print("\n🔨 Building Docker images...")
        
        try:
            # Build images with Docker Compose
            cmd = ['docker', 'compose', 'build', '--no-cache']
            print(f"Running: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True
            )
            
            # Stream output in real-time
            for line in process.stdout:
                print(line.rstrip())
            
            process.wait()
            
            if process.returncode == 0:
                print("✅ Docker images built successfully")
                return True
            else:
                print("❌ Failed to build Docker images")
                return False
                
        except Exception as e:
            print(f"❌ Error building images: {e}")
            return False
    
    def start_services(self):
        """Start all Docker services"""
        print("\n🚀 Starting Docker services...")
        
        try:
            # Start services with Docker Compose
            cmd = ['docker', 'compose', 'up', '-d']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Docker services started")
                print(result.stdout)
                return True
            else:
                print("❌ Failed to start Docker services")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Error starting services: {e}")
            return False
    
    def wait_for_services(self):
        """Wait for all services to be ready"""
        print("\n⏳ Waiting for services to be ready...")
        
        services = {
            'PostgreSQL': ('localhost', 5432),
            'Redis': ('localhost', 6379),
            'MinIO': ('localhost', 9000),
            'API': ('localhost', 8000),
            'Streamlit': ('localhost', 8501)
        }
        
        max_wait = 120  # 2 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            all_ready = True
            
            for service, (host, port) in services.items():
                if service == 'API':
                    # Check API health endpoint
                    try:
                        response = requests.get(f'http://{host}:{port}/health', timeout=2)
                        if response.status_code == 200:
                            print(f"✅ {service} is ready")
                        else:
                            print(f"⏳ {service} is starting...")
                            all_ready = False
                    except requests.exceptions.RequestException:
                        print(f"⏳ {service} is starting...")
                        all_ready = False
                
                elif service == 'Streamlit':
                    # Check Streamlit
                    try:
                        response = requests.get(f'http://{host}:{port}', timeout=2)
                        if response.status_code == 200:
                            print(f"✅ {service} is ready")
                        else:
                            print(f"⏳ {service} is starting...")
                            all_ready = False
                    except requests.exceptions.RequestException:
                        print(f"⏳ {service} is starting...")
                        all_ready = False
                
                else:
                    # Check port connectivity for other services
                    import socket
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(2)
                        result = sock.connect_ex((host, port))
                        sock.close()
                        
                        if result == 0:
                            print(f"✅ {service} is ready")
                        else:
                            print(f"⏳ {service} is starting...")
                            all_ready = False
                    except Exception:
                        print(f"⏳ {service} is starting...")
                        all_ready = False
            
            if all_ready:
                print("\n🎉 All services are ready!")
                return True
            
            time.sleep(5)
        
        print(f"\n⚠️  Some services may not be ready after {max_wait} seconds")
        return False
    
    def show_status(self):
        """Show service status"""
        print("\n📊 Service Status:")
        
        try:
            result = subprocess.run(['docker', 'compose', 'ps'], capture_output=True, text=True)
            print(result.stdout)
        except Exception as e:
            print(f"❌ Error getting status: {e}")
    
    def show_logs(self, service=None):
        """Show service logs"""
        print(f"\n📋 Logs{' for ' + service if service else ''}:")
        
        try:
            cmd = ['docker', 'compose', 'logs', '-f']
            if service:
                cmd.append(service)
            
            subprocess.run(cmd)
        except KeyboardInterrupt:
            print("\n📋 Log viewing stopped")
        except Exception as e:
            print(f"❌ Error showing logs: {e}")
    
    def stop_services(self):
        """Stop all Docker services"""
        print("\n🛑 Stopping Docker services...")
        
        try:
            result = subprocess.run(['docker', 'compose', 'down'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Docker services stopped")
                print(result.stdout)
            else:
                print("❌ Error stopping services")
                print(result.stderr)
        except Exception as e:
            print(f"❌ Error stopping services: {e}")
    
    def cleanup(self):
        """Clean up Docker resources"""
        print("\n🧹 Cleaning up Docker resources...")
        
        try:
            # Remove containers and networks
            subprocess.run(['docker', 'compose', 'down', '-v'], capture_output=True)
            
            # Remove unused images
            subprocess.run(['docker', 'image', 'prune', '-f'], capture_output=True)
            
            print("✅ Cleanup completed")
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
    
    def run_interactive(self):
        """Run in interactive mode"""
        print("🇮🇳 BharatVerse Enhanced Docker System")
        print("=" * 60)
        
        if not self.check_docker():
            return False
        
        self.create_directories()
        
        while True:
            print("\n📋 Available Commands:")
            print("1. 🔨 Build images")
            print("2. 🚀 Start services")
            print("3. 📊 Show status")
            print("4. 📋 Show logs")
            print("5. 🛑 Stop services")
            print("6. 🧹 Cleanup")
            print("7. 🚪 Exit")
            
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == '1':
                self.build_images()
            elif choice == '2':
                if self.start_services():
                    self.wait_for_services()
                    self.show_access_info()
            elif choice == '3':
                self.show_status()
            elif choice == '4':
                service = input("Enter service name (or press Enter for all): ").strip()
                self.show_logs(service if service else None)
            elif choice == '5':
                self.stop_services()
            elif choice == '6':
                self.cleanup()
            elif choice == '7':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
    
    def run_automated(self):
        """Run in automated mode"""
        print("🇮🇳 BharatVerse Enhanced Docker System - Automated Start")
        print("=" * 60)
        
        if not self.check_docker():
            return False
        
        self.create_directories()
        
        # Build images
        if not self.build_images():
            return False
        
        # Start services
        if not self.start_services():
            return False
        
        # Wait for services
        self.wait_for_services()
        
        # Show access information
        self.show_access_info()
        
        # Set up signal handlers
        def signal_handler(signum, frame):
            print(f"\n\n🛑 Received signal {signum}")
            self.stop_services()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        self.running = True
        
        try:
            print("\n💡 Press Ctrl+C to stop all services")
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_services()
        
        return True
    
    def show_access_info(self):
        """Show access information"""
        print("\n" + "=" * 60)
        print("🎉 BharatVerse Enhanced System is Running!")
        print("=" * 60)
        
        print("\n📱 Access URLs:")
        print("   🎨 Streamlit App:    http://localhost:8501")
        print("   🔧 API Server:       http://localhost:8000")
        print("   📚 API Docs:         http://localhost:8000/docs")
        print("   🗄️  MinIO Console:    http://localhost:9001")
        print("   🐘 PostgreSQL:       localhost:5432")
        print("   🔴 Redis:            localhost:6379")
        
        print("\n🤖 AI Features:")
        print("   • Toggle 'Use Real Data' in Streamlit sidebar")
        print("   • Real-time audio transcription with Whisper")
        print("   • Advanced text analysis and translation")
        print("   • AI-powered image captioning")
        print("   • Full-text search with PostgreSQL")
        
        print("\n🔑 Default Credentials:")
        print("   • MinIO: minioadmin / minioadmin")
        print("   • PostgreSQL: bharatverse_user / secretpassword")
        
        print("\n💡 Tips:")
        print("   • First AI model usage may be slow (models loading)")
        print("   • All data is persisted in Docker volumes")
        print("   • Use 'docker compose logs -f' to view logs")

def main():
    """Main entry point"""
    system = DockerBharatVerseSystem()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        system.run_interactive()
    else:
        system.run_automated()

if __name__ == "__main__":
    main()