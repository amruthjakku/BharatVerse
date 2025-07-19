#!/usr/bin/env python3
"""
Simple Docker startup script for BharatVerse
Starts just the database services and runs the enhanced system locally
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

def start_database_services():
    """Start only PostgreSQL, Redis, and MinIO with Docker"""
    print("🐳 Starting database services with Docker...")
    
    # Create a simple docker-compose for just databases
    simple_compose = """
version: '3.9'

services:
  postgres:
    image: postgres:16
    restart: always
    environment:
      POSTGRES_DB: bharatverse
      POSTGRES_USER: bharatverse_user
      POSTGRES_PASSWORD: secretpassword
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./docker/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data
    restart: always
    command: redis-server --appendonly yes

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - miniodata:/data
    restart: always

volumes:
  pgdata:
  redisdata:
  miniodata:
"""
    
    # Write simple compose file
    with open('docker-compose-db.yml', 'w') as f:
        f.write(simple_compose)
    
    try:
        # Start database services
        result = subprocess.run(['docker', 'compose', '-f', 'docker-compose-db.yml', 'up', '-d'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database services started")
            return True
        else:
            print("❌ Failed to start database services")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error starting database services: {e}")
        return False

def wait_for_databases():
    """Wait for database services to be ready"""
    print("⏳ Waiting for database services...")
    
    services = {
        'PostgreSQL': ('localhost', 5432),
        'Redis': ('localhost', 6379),
        'MinIO': ('localhost', 9000)
    }
    
    max_wait = 60  # 1 minute
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        all_ready = True
        
        for service, (host, port) in services.items():
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
            print("🎉 All database services are ready!")
            return True
        
        time.sleep(3)
    
    print("⚠️  Some database services may not be ready")
    return False

def start_local_system():
    """Start the enhanced system locally"""
    print("🚀 Starting BharatVerse Enhanced System locally...")
    
    try:
        # Activate virtual environment and start the system
        cmd = [
            'bash', '-c', 
            'source venv/bin/activate && python start_enhanced_system.py'
        ]
        
        process = subprocess.Popen(cmd, cwd=os.getcwd())
        
        # Wait a bit for the system to start
        time.sleep(10)
        
        # Check if services are running
        try:
            api_response = requests.get('http://localhost:8000/health', timeout=5)
            streamlit_response = requests.get('http://localhost:8501', timeout=5)
            
            if api_response.status_code == 200 and streamlit_response.status_code == 200:
                print("✅ BharatVerse system is running!")
                return process
            else:
                print("⚠️  System may still be starting...")
                return process
                
        except requests.exceptions.RequestException:
            print("⚠️  System is starting...")
            return process
            
    except Exception as e:
        print(f"❌ Error starting local system: {e}")
        return None

def show_access_info():
    """Show access information"""
    print("\n" + "=" * 60)
    print("🎉 BharatVerse Enhanced System is Running!")
    print("=" * 60)
    
    print("\n📱 Access URLs:")
    print("   🎨 Streamlit App:    http://localhost:8501")
    print("   🔧 API Server:       http://localhost:8000")
    print("   📚 API Docs:         http://localhost:8000/docs")
    print("   🗄️  MinIO Console:    http://localhost:9001")
    
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
    print("   • Press Ctrl+C to stop the system")

def stop_services():
    """Stop all services"""
    print("\n🛑 Stopping services...")
    
    # Stop local system
    subprocess.run(['pkill', '-f', 'start_enhanced_system.py'], capture_output=True)
    subprocess.run(['pkill', '-f', 'streamlit'], capture_output=True)
    subprocess.run(['pkill', '-f', 'uvicorn'], capture_output=True)
    
    # Stop database services
    subprocess.run(['docker', 'compose', '-f', 'docker-compose-db.yml', 'down'], 
                  capture_output=True)
    
    print("✅ Services stopped")

def main():
    """Main function"""
    print("🇮🇳 BharatVerse Enhanced System - Simple Docker Start")
    print("=" * 60)
    
    try:
        # Start database services
        if not start_database_services():
            return False
        
        # Wait for databases
        if not wait_for_databases():
            print("⚠️  Continuing anyway...")
        
        # Start local system
        process = start_local_system()
        if not process:
            return False
        
        # Show access info
        show_access_info()
        
        # Wait for user interrupt
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping system...")
            process.terminate()
            
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    finally:
        stop_services()
    
    return True

if __name__ == "__main__":
    main()