#!/usr/bin/env python3
"""
Check AI Models Status
Verify all required models are downloaded and working
"""

import os
import sys
import logging
from pathlib import Path
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_huggingface_cache():
    """Check Hugging Face model cache"""
    logger.info("🔍 Checking Hugging Face model cache...")
    
    # Common cache locations
    cache_locations = [
        Path.home() / ".cache" / "huggingface",
        Path.home() / ".cache" / "torch",
        Path("./data/ai_models"),
        Path("./models")
    ]
    
    total_size = 0
    model_count = 0
    
    for cache_dir in cache_locations:
        if cache_dir.exists():
            logger.info(f"📁 Found cache directory: {cache_dir}")
            
            # Count models and calculate size
            for item in cache_dir.rglob("*"):
                if item.is_file():
                    size = item.stat().st_size
                    total_size += size
                    if any(ext in item.name for ext in ['.bin', '.safetensors', '.pt', '.pth']):
                        model_count += 1
                        logger.info(f"   📦 Model file: {item.name} ({size / (1024**3):.2f} GB)")
    
    logger.info(f"📊 Total cache size: {total_size / (1024**3):.2f} GB")
    logger.info(f"📦 Model files found: {model_count}")
    
    return total_size, model_count

def check_whisper_models():
    """Check Whisper model availability"""
    logger.info("🎵 Checking Whisper models...")
    
    try:
        import whisper
        
        # Check available models
        available_models = whisper.available_models()
        logger.info(f"✅ Whisper available models: {available_models}")
        
        # Try to load base model
        try:
            model = whisper.load_model("base")
            logger.info("✅ Whisper base model loaded successfully")
            
            # Check if large-v3 is available
            try:
                large_model = whisper.load_model("large-v3")
                logger.info("✅ Whisper large-v3 model loaded successfully")
                return True, "large-v3"
            except Exception as e:
                logger.warning(f"⚠️ Whisper large-v3 not available: {e}")
                return True, "base"
                
        except Exception as e:
            logger.error(f"❌ Failed to load Whisper base model: {e}")
            return False, None
            
    except ImportError:
        logger.error("❌ Whisper not installed")
        return False, None

def check_transformers_models():
    """Check Transformers models"""
    logger.info("📝 Checking Transformers models...")
    
    try:
        from transformers import pipeline, AutoTokenizer, AutoModel
        
        models_to_check = [
            ("cardiffnlp/twitter-xlm-roberta-base-sentiment", "sentiment-analysis"),
            ("j-hartmann/emotion-english-distilroberta-base", "text-classification"),
            ("Salesforce/blip-image-captioning-base", "image-to-text"),
            ("facebook/nllb-200-distilled-600M", "translation")
        ]
        
        working_models = []
        failed_models = []
        
        for model_name, task in models_to_check:
            try:
                logger.info(f"🔄 Testing {model_name}...")
                
                if task == "translation":
                    # Special handling for translation model
                    try:
                        tokenizer = AutoTokenizer.from_pretrained(model_name)
                        model = AutoModel.from_pretrained(model_name)
                        logger.info(f"✅ {model_name} - OK")
                        working_models.append(model_name)
                    except Exception as e:
                        logger.error(f"❌ {model_name} - FAILED: {e}")
                        failed_models.append(model_name)
                else:
                    # Regular pipeline test
                    pipe = pipeline(task, model=model_name)
                    logger.info(f"✅ {model_name} - OK")
                    working_models.append(model_name)
                    
            except Exception as e:
                logger.error(f"❌ {model_name} - FAILED: {e}")
                failed_models.append(model_name)
        
        return working_models, failed_models
        
    except ImportError:
        logger.error("❌ Transformers not installed")
        return [], []

def check_enhanced_ai_system():
    """Check the enhanced AI system"""
    logger.info("🤖 Checking Enhanced AI system...")
    
    try:
        # Add project root to path
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        
        from core.enhanced_ai_models import ai_manager
        
        # Get model info
        model_info = ai_manager.get_model_info()
        
        logger.info("📊 Enhanced AI System Status:")
        logger.info(f"   🎵 Whisper available: {model_info.get('whisper_available', False)}")
        logger.info(f"   📝 Text analysis available: {model_info.get('text_analysis_available', False)}")
        logger.info(f"   🖼️ Image analysis available: {model_info.get('image_analysis_available', False)}")
        logger.info(f"   📊 Tracking enabled: {model_info.get('tracking_enabled', False)}")
        
        # Show loaded models
        models = model_info.get('models', {})
        logger.info("📦 Loaded models:")
        for model_type, model_name in models.items():
            status = "✅" if model_name != "not available" else "❌"
            logger.info(f"   {status} {model_type}: {model_name}")
        
        # Test functionality
        logger.info("🧪 Testing AI functionality...")
        
        # Test text analysis
        test_result = ai_manager.analyze_text("This is a test message.")
        if test_result.get("success"):
            logger.info("✅ Text analysis working")
        else:
            logger.warning("⚠️ Text analysis not working")
        
        # Test analytics
        analytics = ai_manager.get_real_time_analytics()
        if "error" not in analytics:
            logger.info("✅ Real-time analytics working")
        else:
            logger.warning("⚠️ Real-time analytics not working")
        
        return model_info
        
    except Exception as e:
        logger.error(f"❌ Enhanced AI system check failed: {e}")
        return None

def generate_status_report():
    """Generate comprehensive status report"""
    logger.info("📋 Generating comprehensive status report...")
    
    report = {
        "timestamp": str(Path(__file__).stat().st_mtime),
        "cache_info": {},
        "whisper_status": {},
        "transformers_status": {},
        "enhanced_ai_status": {},
        "recommendations": []
    }
    
    # Check cache
    total_size, model_count = check_huggingface_cache()
    report["cache_info"] = {
        "total_size_gb": round(total_size / (1024**3), 2),
        "model_files_count": model_count
    }
    
    # Check Whisper
    whisper_working, whisper_model = check_whisper_models()
    report["whisper_status"] = {
        "available": whisper_working,
        "model": whisper_model
    }
    
    # Check Transformers
    working_models, failed_models = check_transformers_models()
    report["transformers_status"] = {
        "working_models": working_models,
        "failed_models": failed_models,
        "success_rate": len(working_models) / (len(working_models) + len(failed_models)) if (working_models or failed_models) else 0
    }
    
    # Check Enhanced AI
    enhanced_ai_info = check_enhanced_ai_system()
    if enhanced_ai_info:
        report["enhanced_ai_status"] = enhanced_ai_info
    
    # Generate recommendations
    recommendations = []
    
    if total_size < 1:  # Less than 1GB
        recommendations.append("⚠️ Very few models downloaded. Run: python scripts/fix_dependencies.py")
    
    if not whisper_working:
        recommendations.append("❌ Whisper not working. Install with: uv pip install openai-whisper")
    
    if len(failed_models) > len(working_models):
        recommendations.append("❌ Most Transformers models failed. Check internet connection and disk space")
    
    if not enhanced_ai_info:
        recommendations.append("❌ Enhanced AI system not working. Check module imports")
    
    if not recommendations:
        recommendations.append("✅ All systems operational!")
    
    report["recommendations"] = recommendations
    
    return report

def main():
    """Main model checking process"""
    logger.info("🔍 BharatVerse AI Models - Status Checker")
    logger.info("=" * 60)
    
    # Generate comprehensive report
    report = generate_status_report()
    
    # Display summary
    logger.info("\n📋 STATUS SUMMARY")
    logger.info("=" * 40)
    
    cache_info = report["cache_info"]
    logger.info(f"💾 Cache size: {cache_info['total_size_gb']} GB")
    logger.info(f"📦 Model files: {cache_info['model_files_count']}")
    
    whisper_status = report["whisper_status"]
    whisper_icon = "✅" if whisper_status["available"] else "❌"
    logger.info(f"{whisper_icon} Whisper: {whisper_status.get('model', 'Not available')}")
    
    transformers_status = report["transformers_status"]
    success_rate = transformers_status["success_rate"] * 100
    logger.info(f"📝 Transformers: {success_rate:.0f}% models working")
    
    enhanced_ai_status = report.get("enhanced_ai_status", {})
    if enhanced_ai_status:
        ai_icon = "✅" if enhanced_ai_status.get("whisper_available") else "❌"
        logger.info(f"{ai_icon} Enhanced AI: System loaded")
    else:
        logger.info("❌ Enhanced AI: System not loaded")
    
    # Show recommendations
    logger.info("\n💡 RECOMMENDATIONS")
    logger.info("=" * 40)
    for rec in report["recommendations"]:
        logger.info(rec)
    
    # Save report
    report_file = Path(__file__).parent.parent / "data" / "model_status_report.json"
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"\n📄 Detailed report saved to: {report_file}")
    
    # Return success status
    all_good = (
        cache_info["total_size_gb"] > 1 and
        whisper_status["available"] and
        transformers_status["success_rate"] > 0.5 and
        enhanced_ai_status
    )
    
    if all_good:
        logger.info("\n🎉 ALL MODELS ARE READY!")
        logger.info("🚀 Your Enhanced AI system is fully operational")
    else:
        logger.info("\n⚠️ Some issues detected. Follow the recommendations above.")
    
    return all_good

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)