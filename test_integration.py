#!/usr/bin/env python3
"""
Test script for BharatVerse integration
Tests database connections, AI models, and API endpoints
"""

import sys
import os
import requests
import time
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_connections():
    """Test database connections"""
    print("=" * 60)
    print("Testing Database Connections...")
    print("=" * 60)
    
    try:
        from core.database import db_manager
        
        # Test PostgreSQL
        try:
            conn = db_manager.get_postgres_connection()
            db_manager.release_postgres_connection(conn)
            print("✅ PostgreSQL: Connected")
        except Exception as e:
            print(f"❌ PostgreSQL: {e}")
        
        # Test Redis
        try:
            db_manager.redis.ping()
            print("✅ Redis: Connected")
        except Exception as e:
            print(f"❌ Redis: {e}")
        
        # Test MinIO
        try:
            buckets = db_manager.minio.list_buckets()
            print(f"✅ MinIO: Connected ({len(buckets)} buckets)")
        except Exception as e:
            print(f"❌ MinIO: {e}")
            
    except Exception as e:
        print(f"❌ Failed to import database module: {e}")
    
    print()


def test_ai_models():
    """Test AI models"""
    print("=" * 60)
    print("Testing AI Models...")
    print("=" * 60)
    
    try:
        from core.ai_models import ai_manager
        
        # Check Whisper
        if ai_manager.whisper_model:
            print("✅ Whisper model: Loaded")
        else:
            print("❌ Whisper model: Not loaded")
        
        # Check Text Processor
        if ai_manager.text_processor:
            print("✅ Text processor: Loaded")
            
            # Test text analysis
            result = ai_manager.analyze_text("Hello, this is a test.", "en")
            print(f"   Sample analysis: {result.get('sentiment', 'N/A')}")
        else:
            print("❌ Text processor: Not loaded")
        
        # Check Image Captioner
        if ai_manager.image_captioner:
            print("✅ Image captioner: Loaded")
        else:
            print("❌ Image captioner: Not loaded")
            
    except Exception as e:
        print(f"❌ Failed to test AI models: {e}")
    
    print()


def test_api_endpoints():
    """Test API endpoints"""
    print("=" * 60)
    print("Testing API Endpoints...")
    print("=" * 60)
    
    api_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print("✅ API Health Check:")
            print(f"   - API: {health.get('api', 'unknown')}")
            print(f"   - Database: {health.get('database', 'unknown')}")
            print(f"   - MinIO: {health.get('minio', 'unknown')}")
            print(f"   - Redis: {health.get('redis', 'unknown')}")
            print(f"   - AI Models: {health.get('ai_models', {})}")
        else:
            print(f"❌ API Health Check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ API not running. Start it with: python -m core.api_service")
    except Exception as e:
        print(f"❌ API Health Check error: {e}")
    
    print()


def test_sample_workflow():
    """Test a sample workflow"""
    print("=" * 60)
    print("Testing Sample Workflow...")
    print("=" * 60)
    
    api_url = "http://localhost:8000"
    
    try:
        # Test text analysis
        response = requests.post(
            f"{api_url}/api/v1/text/analyze",
            json={
                "text": "This is a beautiful traditional story from India.",
                "language": "en",
                "translate": False
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Text Analysis:")
            analysis = result.get('analysis', {})
            print(f"   - Language: {analysis.get('language', 'unknown')}")
            print(f"   - Sentiment: {analysis.get('sentiment', 'unknown')}")
            print(f"   - Word count: {analysis.get('word_count', 0)}")
        else:
            print(f"❌ Text Analysis failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Workflow test error: {e}")
    
    print()


def main():
    """Run all tests"""
    print("\n" + "🧪 BharatVerse Integration Test Suite 🧪".center(60) + "\n")
    
    # Test components
    test_database_connections()
    test_ai_models()
    test_api_endpoints()
    test_sample_workflow()
    
    print("=" * 60)
    print("Test suite completed!")
    print("=" * 60)
    
    print("\n📝 Next steps:")
    print("1. If database connections failed, ensure Docker services are running:")
    print("   docker-compose up -d")
    print("\n2. If API tests failed, start the API server:")
    print("   python -m core.api_service")
    print("\n3. To run the Streamlit app:")
    print("   streamlit run streamlit_app/app.py")
    print("\n4. If AI models failed to load, they will download on first use.")
    print("   This may take some time depending on your internet connection.")


if __name__ == "__main__":
    main()
