#!/usr/bin/env python3
"""
Test script to verify all API endpoints are working
"""

import requests
import json

API_BASE = "http://localhost:8000"

def test_endpoint(method, endpoint, description):
    """Test a single API endpoint"""
    try:
        url = f"{API_BASE}{endpoint}"
        if method.upper() == "GET":
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ {description}: {endpoint}")
            return True
        else:
            print(f"❌ {description}: {endpoint} (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ {description}: {endpoint} (Error: {e})")
        return False

def main():
    print("🧪 Testing BharatVerse API Endpoints")
    print("=" * 50)
    
    endpoints = [
        ("GET", "/", "Root endpoint"),
        ("GET", "/health", "Health check"),
        ("GET", "/api/v1/community/stats", "Community stats"),
        ("GET", "/api/v1/community/leaderboard", "Community leaderboard"),
        ("GET", "/api/v1/content/recent", "Recent content"),
        ("GET", "/api/v1/analytics", "Analytics"),
        ("GET", "/api/v1/models/status", "Model status"),
    ]
    
    passed = 0
    total = len(endpoints)
    
    for method, endpoint, description in endpoints:
        if test_endpoint(method, endpoint, description):
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} endpoints working")
    
    if passed == total:
        print("🎉 All API endpoints are working correctly!")
    else:
        print("⚠️  Some endpoints need attention")

if __name__ == "__main__":
    main()