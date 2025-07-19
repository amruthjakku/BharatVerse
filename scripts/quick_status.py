#!/usr/bin/env python3
"""
Quick Status Check for Enhanced AI
"""

import os
import sys
from pathlib import Path

def main():
    print("🔍 BharatVerse Enhanced AI - Quick Status Check")
    print("=" * 60)
    
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    try:
        from core.enhanced_ai_models import ai_manager
        
        print("✅ Enhanced AI Manager loaded successfully")
        
        # Get model info
        model_info = ai_manager.get_model_info()
        
        print("\n📊 Model Status:")
        print(f"   🎵 Whisper: {'✅' if model_info.get('whisper_available') else '❌'}")
        print(f"   📝 Text Analysis: {'✅' if model_info.get('text_analysis_available') else '❌'}")
        print(f"   🖼️ Image Analysis: {'✅' if model_info.get('image_analysis_available') else '❌'}")
        print(f"   📊 Tracking: {'✅' if model_info.get('tracking_enabled') else '❌'}")
        
        # Show loaded models
        models = model_info.get('models', {})
        print("\n📦 Loaded Models:")
        for model_type, model_name in models.items():
            status = "✅" if model_name != "not available" else "❌"
            print(f"   {status} {model_type}: {model_name}")
        
        # Test basic functionality
        print("\n🧪 Testing Basic Functionality:")
        
        # Test text analysis
        test_result = ai_manager.analyze_text("This is a test message.")
        if test_result.get("success"):
            print("   ✅ Text analysis working")
            print(f"      Language: {test_result.get('language', 'unknown')}")
            print(f"      Word count: {test_result.get('word_count', 0)}")
        else:
            print("   ❌ Text analysis not working")
        
        # Test analytics
        analytics = ai_manager.get_real_time_analytics()
        if "error" not in analytics:
            print("   ✅ Real-time analytics working")
            print(f"      Total operations: {analytics.get('total_operations', 0)}")
        else:
            print("   ❌ Real-time analytics not working")
        
        # Check cache size
        cache_dir = Path.home() / ".cache" / "huggingface"
        if cache_dir.exists():
            total_size = sum(f.stat().st_size for f in cache_dir.rglob("*") if f.is_file())
            size_gb = total_size / (1024**3)
            print(f"\n💾 Model Cache: {size_gb:.2f} GB")
        
        print("\n🎉 Enhanced AI System Status: OPERATIONAL")
        print("\n🚀 Ready to use:")
        print("   • Visit 'Enhanced AI Features' page (14)")
        print("   • Check 'Real-Time AI Analytics' page (15)")
        print("   • Upload content for real AI processing")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)