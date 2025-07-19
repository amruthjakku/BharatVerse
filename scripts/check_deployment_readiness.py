#!/usr/bin/env python3
"""
BharatVerse Deployment Readiness Checker
"""

import os
import sys
import subprocess
import requests
from pathlib import Path

def check_docker_services():
    """Check if Docker services are running"""
    print("🐳 Checking Docker Services...")
    
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Docker is not running")
            return False
        
        services = ['postgres', 'redis', 'minio']
        running_services = []
        
        for service in services:
            if service in result.stdout:
                running_services.append(service)
                print(f"   ✅ {service} is running")
            else:
                print(f"   ❌ {service} is not running")
        
        return len(running_services) == len(services)
        
    except FileNotFoundError:
        print("❌ Docker not found")
        return False

def check_local_ports():
    """Check if local services are accessible"""
    print("\n🔌 Checking Local Ports...")
    
    ports = {
        5432: "PostgreSQL",
        6379: "Redis", 
        9000: "MinIO"
    }
    
    accessible_ports = 0
    
    for port, service in ports.items():
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                print(f"   ✅ {service} (port {port}) is accessible")
                accessible_ports += 1
            else:
                print(f"   ❌ {service} (port {port}) is not accessible")
        except Exception as e:
            print(f"   ❌ {service} (port {port}) check failed: {e}")
    
    return accessible_ports == len(ports)

def check_ai_models():
    """Check if AI models are loaded"""
    print("\n🧠 Checking AI Models...")
    
    try:
        # Add project root to path
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        
        from core.enhanced_ai_models import ai_manager
        
        model_info = ai_manager.get_model_info()
        
        print(f"   ✅ Whisper: {model_info.get('whisper_available', False)}")
        print(f"   ✅ Text Analysis: {model_info.get('text_analysis_available', False)}")
        print(f"   ✅ Image Analysis: {model_info.get('image_analysis_available', False)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ AI models check failed: {e}")
        return False

def check_deployment_files():
    """Check if deployment files exist"""
    print("\n📁 Checking Deployment Files...")
    
    required_files = [
        'Home.py',
        'streamlit_cloud_requirements.txt',
        'packages.txt',
        '.streamlit/config.toml',
        'streamlit_secrets_template.toml'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (missing)")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def check_git_status():
    """Check Git repository status"""
    print("\n📚 Checking Git Repository...")
    
    try:
        # Check if git repo exists
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode != 0:
            print("   ❌ Not a git repository")
            return False
        
        print("   ✅ Git repository initialized")
        
        # Check for remote
        result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
        if 'github.com' in result.stdout:
            print("   ✅ GitHub remote configured")
        else:
            print("   ⚠️ No GitHub remote found")
            return False
        
        # Check for uncommitted changes
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if result.stdout.strip():
            print("   ⚠️ Uncommitted changes found")
            print("   💡 Run: git add . && git commit -m 'Deploy to Streamlit Cloud'")
        else:
            print("   ✅ No uncommitted changes")
        
        return True
        
    except FileNotFoundError:
        print("   ❌ Git not found")
        return False

def main():
    print("🚀 BharatVerse - Deployment Readiness Check")
    print("=" * 60)
    
    checks = [
        ("Docker Services", check_docker_services),
        ("Local Ports", check_local_ports),
        ("AI Models", check_ai_models),
        ("Deployment Files", check_deployment_files),
        ("Git Repository", check_git_status)
    ]
    
    passed_checks = 0
    total_checks = len(checks)
    
    for check_name, check_func in checks:
        try:
            if check_func():
                passed_checks += 1
        except Exception as e:
            print(f"❌ {check_name} check failed with error: {e}")
    
    print(f"\n📊 Summary: {passed_checks}/{total_checks} checks passed")
    
    if passed_checks == total_checks:
        print("\n🎉 Ready for Deployment!")
        print("\n🚀 Next Steps:")
        print("1. Set up ngrok tunnels:")
        print("   ngrok tcp 5432  # PostgreSQL")
        print("   ngrok tcp 6379  # Redis") 
        print("   ngrok http 9000 # MinIO")
        print("\n2. Go to https://share.streamlit.io")
        print("3. Connect your GitHub repository")
        print("4. Set main file: Home.py")
        print("5. Add secrets from streamlit_secrets_template.toml")
        print("6. Deploy!")
        
    else:
        print(f"\n⚠️ {total_checks - passed_checks} issues need to be resolved before deployment")
        print("\n🔧 Fix the issues above and run this script again")
    
    return passed_checks == total_checks

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)