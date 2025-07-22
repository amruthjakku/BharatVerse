#!/usr/bin/env python3
"""
Test Redis connection specifically
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def test_redis_connection():
    """Test Redis connection with different methods"""
    print("🔍 Testing Redis Connection")
    print("=" * 40)
    
    try:
        import redis
        print("✅ Redis library available")
    except ImportError:
        print("❌ Redis library not installed")
        print("Run: pip install redis")
        return
    
    # Test with environment variables
    redis_url = os.getenv("REDIS_URL", "https://lasting-moose-46409.upstash.io")
    redis_token = os.getenv("REDIS_TOKEN", "AbVJAAIjcDFlMGY0YmM4YTgyMTI0MmJjOTVlOTMxY2RiNWJlMTg1YnAxMA")
    
    print(f"Redis URL: {redis_url}")
    print(f"Redis Token: {redis_token[:10]}...")
    
    # Test connection methods
    test_methods = [
        {
            "name": "Direct URL Connection",
            "method": lambda: redis.from_url(
                f"redis://:{redis_token}@lasting-moose-46409.upstash.io:6379",
                decode_responses=True
            )
        },
        {
            "name": "HTTPS Connection",
            "method": lambda: redis.Redis(
                host="lasting-moose-46409.upstash.io",
                port=6379,
                password=redis_token,
                decode_responses=True,
                ssl=True
            )
        },
        {
            "name": "Upstash REST API",
            "method": lambda: test_upstash_rest_api(redis_token)
        }
    ]
    
    for test in test_methods:
        print(f"\n🧪 Testing: {test['name']}")
        try:
            client = test["method"]()
            if hasattr(client, 'ping'):
                client.ping()
                print("✅ Connection successful")
                
                # Test basic operations
                client.set("test_key", "test_value")
                value = client.get("test_key")
                if value == "test_value":
                    print("✅ Read/Write operations working")
                else:
                    print("⚠️ Read/Write operations failed")
                client.delete("test_key")
            else:
                print("✅ REST API connection successful")
                
        except Exception as e:
            print(f"❌ Failed: {e}")

def test_upstash_rest_api(token):
    """Test Upstash REST API"""
    import requests
    
    url = "https://lasting-moose-46409.upstash.io"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test ping
    response = requests.post(f"{url}/ping", headers=headers)
    if response.status_code == 200:
        return "REST API working"
    else:
        raise Exception(f"REST API failed: {response.status_code}")

def test_streamlit_secrets():
    """Test if Streamlit secrets work"""
    print("\n🔍 Testing Streamlit Secrets")
    print("=" * 40)
    
    try:
        import streamlit as st
        
        # Try to access secrets
        redis_config = st.secrets.get("redis", {})
        if redis_config:
            print("✅ Redis secrets found in Streamlit")
            print(f"URL: {redis_config.get('url', 'Not set')}")
            print(f"Token: {redis_config.get('token', 'Not set')[:10]}...")
        else:
            print("❌ No Redis secrets found in Streamlit")
            
    except Exception as e:
        print(f"❌ Error accessing Streamlit secrets: {e}")

if __name__ == "__main__":
    test_redis_connection()
    test_streamlit_secrets()
    
    print("\n🎯 Summary:")
    print("If Redis connection fails:")
    print("1. Check if Redis URL and token are correct")
    print("2. Verify Streamlit Cloud secrets are properly set")
    print("3. Try using REST API instead of direct Redis connection")
    print("4. Check Upstash dashboard for connection issues")