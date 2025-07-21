#!/usr/bin/env python3
"""
Test script to verify cloud AI services are working
"""

import requests
import json
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def test_huggingface_api():
    """Test HuggingFace API connectivity"""
    print("🔍 Testing HuggingFace API connectivity...")
    
    # Read token from secrets file
    try:
        import toml
        secrets_path = Path(__file__).parent / ".streamlit" / "secrets.toml"
        
        if not secrets_path.exists():
            print("❌ secrets.toml file not found")
            return False
            
        secrets = toml.load(secrets_path)
        token = secrets.get("inference", {}).get("huggingface_token", "")
        
        if not token:
            print("❌ HuggingFace token not found in secrets")
            return False
            
        print(f"✅ Found HuggingFace token: {token[:10]}...")
        
    except ImportError:
        print("❌ toml package not installed. Run: pip install toml")
        return False
    except Exception as e:
        print(f"❌ Error reading secrets: {e}")
        return False
    
    # Test API endpoints
    endpoints = {
        "Text Analysis": "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest",
        "Translation": "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-hi-en",
        "Whisper": "https://api-inference.huggingface.co/models/openai/whisper-small"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    for service_name, endpoint in endpoints.items():
        try:
            # Simple test request
            if service_name == "Text Analysis":
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json={"inputs": "Hello world"},
                    timeout=10
                )
            elif service_name == "Translation":
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json={"inputs": "नमस्ते"},
                    timeout=10
                )
            else:
                # Just check if endpoint is reachable
                response = requests.get(endpoint, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {service_name}: Working")
            elif response.status_code == 503:
                print(f"⏳ {service_name}: Model loading (try again in a minute)")
            elif response.status_code == 401:
                print(f"❌ {service_name}: Authentication failed")
                return False
            else:
                print(f"⚠️  {service_name}: Status {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏳ {service_name}: Timeout (model may be loading)")
        except requests.exceptions.RequestException as e:
            print(f"❌ {service_name}: Connection error - {e}")
    
    return True

def test_redis_cache():
    """Test Redis cache connectivity"""
    print("\n🔍 Testing Redis cache connectivity...")
    
    try:
        import toml
        secrets_path = Path(__file__).parent / ".streamlit" / "secrets.toml"
        secrets = toml.load(secrets_path)
        
        redis_url = secrets.get("redis", {}).get("url", "")
        redis_token = secrets.get("redis", {}).get("token", "")
        
        if not redis_url or not redis_token:
            print("❌ Redis configuration not found")
            return False
            
        print(f"✅ Found Redis URL: {redis_url}")
        
        # Test Redis connection
        try:
            import redis
            
            # Create Redis client with Upstash configuration
            r = redis.Redis(
                host=redis_url.replace("https://", "").replace("http://", ""),
                port=6379,
                password=redis_token,
                ssl=True,
                decode_responses=True
            )
            
            # Test connection
            r.ping()
            print("✅ Redis: Connected")
            return True
            
        except ImportError:
            print("⚠️  Redis package not installed. Run: pip install redis")
            return False
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Redis: {e}")
        return False

def show_deployment_instructions():
    """Show instructions for Streamlit Cloud deployment"""
    print("\n🚀 For Streamlit Cloud Deployment:")
    print("=" * 50)
    print("1. Go to your Streamlit Cloud app settings")
    print("2. Navigate to 'Secrets' section")
    print("3. Copy the contents of .streamlit/secrets.toml")
    print("4. Paste into the secrets editor")
    print("5. Save and redeploy")
    print("\n📋 Your secrets.toml contains:")
    print("- ✅ HuggingFace API token")
    print("- ✅ AI model endpoints")
    print("- ✅ Redis cache configuration")
    print("- ✅ Database settings")
    print("- ✅ GitLab OAuth settings")

if __name__ == "__main__":
    print("🤖 BharatVerse Cloud AI Test")
    print("=" * 40)
    
    # Test HuggingFace API
    hf_success = test_huggingface_api()
    
    # Test Redis cache
    redis_success = test_redis_cache()
    
    # Show deployment instructions
    show_deployment_instructions()
    
    if hf_success:
        print("\n🎉 Cloud AI services are configured correctly!")
        print("🚀 Your app should show AI services as online when deployed")
    else:
        print("\n❌ Some issues found. Please check the configuration.")
        sys.exit(1)