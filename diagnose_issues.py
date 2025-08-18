#!/usr/bin/env python3
"""
Diagnostic script to test all services and identify issues
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import logging
logging.basicConfig(level=logging.INFO)

def test_imports():
    """Test all critical imports"""
    print("\n🔍 Testing Imports...")
    imports_status = {}
    
    critical_imports = [
        ("streamlit", "Streamlit"),
        ("pandas", "Pandas"),
        ("numpy", "NumPy"),
        ("requests", "Requests"),
        ("plotly", "Plotly"),
        ("PIL", "Pillow"),
        ("redis", "Redis"),
        ("psycopg2", "PostgreSQL"),
        ("sqlalchemy", "SQLAlchemy"),
        ("minio", "MinIO"),
        ("boto3", "AWS SDK"),
    ]
    
    for module_name, display_name in critical_imports:
        try:
            __import__(module_name)
            imports_status[display_name] = "✅ Available"
        except ImportError as e:
            imports_status[display_name] = f"❌ Not available: {e}"
    
    for name, status in imports_status.items():
        print(f"  {name}: {status}")
    
    return imports_status

def test_services():
    """Test all services"""
    print("\n🔧 Testing Services...")
    
    try:
        from core.service_manager import get_service_manager
        service_manager = get_service_manager()
        
        services = service_manager.list_services()
        
        for service_name, status in services.items():
            if status.value == "available":
                print(f"  ✅ {service_name}: Available")
            elif status.value == "error":
                error = service_manager.get_error(service_name)
                print(f"  ❌ {service_name}: Error - {error}")
            else:
                print(f"  ⚠️ {service_name}: Unavailable")
        
        return services
    except Exception as e:
        print(f"  ❌ Service Manager Error: {e}")
        return {}

def test_database_connection():
    """Test database connectivity"""
    print("\n🗄️ Testing Database Connection...")
    
    try:
        from core.service_manager import get_service_manager
        service_manager = get_service_manager()
        
        if service_manager.is_available("database"):
            print("  ✅ Database service available")
            return True
        else:
            error = service_manager.get_error("database")
            print(f"  ❌ Database not available: {error}")
            
            # Check for Supabase as fallback
            if service_manager.is_available("supabase"):
                print("  ✅ Supabase available as fallback")
                return True
            else:
                print("  ❌ No database backend available")
                return False
    except Exception as e:
        print(f"  ❌ Database test error: {e}")
        return False

def test_storage():
    """Test storage services"""
    print("\n💾 Testing Storage Services...")
    
    try:
        from core.service_manager import get_service_manager
        service_manager = get_service_manager()
        
        # Test MinIO
        if service_manager.is_available("minio"):
            print("  ✅ MinIO storage available")
            return "minio"
        else:
            minio_error = service_manager.get_error("minio")
            print(f"  ⚠️ MinIO not available: {minio_error}")
        
        # Test fallback storage
        if service_manager.is_available("storage"):
            print("  ✅ Fallback storage available")
            return "fallback"
        else:
            print("  ❌ No storage service available")
            return None
    except Exception as e:
        print(f"  ❌ Storage test error: {e}")
        return None

def test_ai_services():
    """Test AI services"""
    print("\n🤖 Testing AI Services...")
    
    try:
        from core.service_manager import get_service_manager
        service_manager = get_service_manager()
        
        # Test local AI
        if service_manager.is_available("ai"):
            print("  ✅ Local AI service available")
            return "local"
        else:
            print(f"  ⚠️ Local AI not available: {service_manager.get_error('ai')}")
        
        # Test cloud AI
        if service_manager.is_available("cloud_ai"):
            print("  ✅ Cloud AI service available")
            return "cloud"
        else:
            print(f"  ⚠️ Cloud AI not available: {service_manager.get_error('cloud_ai')}")
        
        print("  ℹ️ AI services not critical for basic functionality")
        return None
    except Exception as e:
        print(f"  ❌ AI service test error: {e}")
        return None

def test_pages():
    """Test page imports"""
    print("\n📄 Testing Pages...")
    
    pages_dir = Path(__file__).parent / "pages"
    page_files = list(pages_dir.glob("*.py"))
    
    page_status = {}
    
    for page_file in page_files:
        page_name = page_file.stem
        try:
            # Try to import the page module
            spec = __import__('importlib.util').util.spec_from_file_location(page_name, page_file)
            if spec and spec.loader:
                module = __import__('importlib.util').util.module_from_spec(spec)
                spec.loader.exec_module(module)
                page_status[page_name] = "✅ OK"
        except Exception as e:
            page_status[page_name] = f"❌ Error: {str(e)[:50]}"
    
    for page, status in sorted(page_status.items()):
        print(f"  {page}: {status}")
    
    return page_status

def test_environment():
    """Test environment variables"""
    print("\n🔐 Testing Environment Configuration...")
    
    critical_vars = [
        "ENABLE_CACHING",
        "DEBUG_MODE",
        "AI_MODE",
        "APP_ENV",
    ]
    
    optional_vars = [
        "GITLAB_CLIENT_ID",
        "GITLAB_CLIENT_SECRET",
        "DATABASE_URL",
        "REDIS_URL",
        "MINIO_ENDPOINT",
    ]
    
    print("  Critical variables:")
    for var in critical_vars:
        value = os.environ.get(var)
        if value:
            print(f"    ✅ {var}: Set")
        else:
            print(f"    ❌ {var}: Not set")
    
    print("  Optional variables:")
    for var in optional_vars:
        value = os.environ.get(var)
        if value:
            print(f"    ✅ {var}: Set")
        else:
            print(f"    ⚠️ {var}: Not set")

def main():
    print("=" * 60)
    print("🏛️ BharatVerse Diagnostic Report")
    print("=" * 60)
    
    # Test imports
    test_imports()
    
    # Test environment
    test_environment()
    
    # Test services
    services = test_services()
    
    # Test specific services
    test_database_connection()
    test_storage()
    test_ai_services()
    
    # Test pages
    test_pages()
    
    print("\n" + "=" * 60)
    print("📊 Diagnostic Summary")
    print("=" * 60)
    
    # Count service statuses
    if services:
        available = sum(1 for s in services.values() if s.value == "available")
        total = len(services)
        print(f"  Services: {available}/{total} available")
    
    print("\n✅ Diagnostic complete!")
    print("\nRecommendations:")
    print("  1. Services marked with ❌ need configuration or dependencies")
    print("  2. Services marked with ⚠️ are optional but enhance functionality")
    print("  3. Check error messages for specific issues")
    print("  4. Run 'streamlit run Home.py' to test the application")

if __name__ == "__main__":
    main()
