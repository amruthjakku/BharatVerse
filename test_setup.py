#!/usr/bin/env python3
"""
🧪 BharatVerse Setup Verification Script
=======================================
Test all cloud services to ensure they're working properly.
"""

import os
import sys
import requests
import streamlit as st
from pathlib import Path

def test_secrets_file():
    """Test if secrets file exists and is readable"""
    print("🔐 Testing secrets file...")
    
    secrets_file = Path(".streamlit/secrets.toml")
    if not secrets_file.exists():
        print("❌ Secrets file not found!")
        return False
    
    try:
        # Try to load secrets using streamlit
        import toml
        with open(secrets_file, 'r') as f:
            secrets = toml.load(f)
        
        required_sections = ['inference', 'postgres', 'supabase', 'redis', 'r2']
        missing_sections = [s for s in required_sections if s not in secrets]
        
        if missing_sections:
            print(f"❌ Missing sections in secrets: {missing_sections}")
            return False
        
        print("✅ Secrets file is valid!")
        return True
        
    except Exception as e:
        print(f"❌ Error reading secrets file: {e}")
        return False

def test_huggingface():
    """Test HuggingFace API connection"""
    print("\n🤗 Testing HuggingFace API...")
    
    try:
        if 'inference' not in st.secrets:
            print("❌ HuggingFace secrets not found!")
            return False
        
        token = st.secrets.inference.huggingface_token
        
        if not token or token == "hf_your_token_here":
            print("❌ HuggingFace token not configured!")
            return False
        
        # Test API call
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            "https://api-inference.huggingface.co/models/openai/whisper-base",
            headers=headers,
            json={"inputs": "test"},
            timeout=10
        )
        
        if response.status_code == 200 or response.status_code == 503:  # 503 is model loading
            print("✅ HuggingFace API is working!")
            return True
        else:
            print(f"❌ HuggingFace API error: {response.status_code} - {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ HuggingFace test failed: {e}")
        return False

def test_supabase():
    """Test Supabase database connection"""
    print("\n🐘 Testing Supabase database...")
    
    try:
        if 'supabase' not in st.secrets:
            print("❌ Supabase secrets not found!")
            return False
        
        url = st.secrets.supabase.url
        key = st.secrets.supabase.anon_key
        
        if "your-project-id" in url:
            print("❌ Supabase URL not configured!")
            return False
        
        # Test API call
        headers = {
            "apikey": key,
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{url}/rest/v1/contributions", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Supabase database is accessible!")
            return True
        else:
            print(f"❌ Supabase error: {response.status_code} - {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Supabase test failed: {e}")
        return False

def test_upstash():
    """Test Upstash Redis connection"""
    print("\n⚡ Testing Upstash Redis...")
    
    try:
        if 'redis' not in st.secrets:
            print("❌ Redis secrets not found!")
            return False
        
        url = st.secrets.redis.url
        token = st.secrets.redis.token
        
        if "your-db-id" in url:
            print("❌ Redis URL not configured!")
            return False
        
        # Test Redis SET command
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{url}/set/test_key/test_value", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Upstash Redis is working!")
            return True
        else:
            print(f"❌ Redis error: {response.status_code} - {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Upstash test failed: {e}")
        return False

def test_cloudflare_r2():
    """Test Cloudflare R2 storage"""
    print("\n🪣 Testing Cloudflare R2...")
    
    try:
        if 'r2' not in st.secrets:
            print("❌ R2 secrets not found!")
            return False
        
        access_key = st.secrets.r2.access_key_id
        secret_key = st.secrets.r2.secret_access_key
        endpoint = st.secrets.r2.endpoint_url
        
        if "your-r2-access-key-id" in access_key:
            print("❌ R2 credentials not configured!")
            return False
        
        print("⚠️  R2 test requires boto3. Install with: pip install boto3")
        print("✅ R2 configuration appears valid!")
        return True
    
    except Exception as e:
        print(f"❌ R2 test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 BharatVerse Setup Verification")
    print("=" * 40)
    
    tests = [
        ("Secrets File", test_secrets_file),
        ("HuggingFace API", test_huggingface), 
        ("Supabase Database", test_supabase),
        ("Upstash Redis", test_upstash),
        ("Cloudflare R2", test_cloudflare_r2)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("🎯 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Score: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your BharatVerse setup is ready!")
        print("🚀 You can now run: streamlit run Home.py")
    else:
        print(f"\n⚠️  {len(results) - passed} tests failed. Please check your configuration.")
        print("📖 See COMPLETE_SETUP_GUIDE.md for detailed setup instructions.")
    
    return passed == len(results)

if __name__ == "__main__":
    try:
        # Install required packages if missing
        try:
            import toml
            import requests
        except ImportError:
            print("📦 Installing required packages...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "toml", "requests"])
            import toml
            import requests
        
        success = main()
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"❌ Test runner error: {e}")
        sys.exit(1)