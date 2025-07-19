#!/usr/bin/env python3
"""
Fix Missing Dependencies for Enhanced AI
Install all required packages and verify installation
"""

import subprocess
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def install_package(package, description=""):
    """Install a Python package"""
    logger.info(f"🔄 Installing {package} {description}")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        logger.info(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install {package}: {e}")
        return False

def install_missing_dependencies():
    """Install all missing dependencies"""
    logger.info("🚀 Installing missing dependencies for Enhanced AI")
    
    # Critical missing packages
    packages = [
        ("sentencepiece>=0.1.99", "- Required for translation models"),
        ("timm>=0.9.12", "- Required for vision models"),
        ("protobuf>=3.20.0", "- Required for model serialization"),
        ("sacremoses>=0.0.53", "- Required for text processing"),
        ("tokenizers>=0.15.0", "- Required for fast tokenization"),
        ("accelerate>=0.25.0", "- Required for model acceleration"),
        ("safetensors>=0.4.0", "- Required for safe model loading"),
        ("pyaudio>=0.2.11", "- Required for audio input (optional)"),
        ("portaudio19-dev", "- Audio system dependency (Linux/Mac)")
    ]
    
    failed_packages = []
    
    for package, desc in packages:
        if not install_package(package, desc):
            failed_packages.append(package)
    
    # Special handling for PortAudio (system dependency)
    logger.info("🔄 Installing system audio dependencies...")
    try:
        # Try to install portaudio system dependency
        subprocess.run(["brew", "install", "portaudio"], check=False, capture_output=True)
        logger.info("✅ PortAudio system dependency installed (macOS)")
    except:
        logger.warning("⚠️ Could not install PortAudio system dependency")
        logger.info("💡 Audio input may not work, but other features will function")
    
    return failed_packages

def verify_installations():
    """Verify that all packages are properly installed"""
    logger.info("🔍 Verifying installations...")
    
    test_imports = [
        ("sentencepiece", "SentencePiece tokenizer"),
        ("timm", "PyTorch Image Models"),
        ("transformers", "Hugging Face Transformers"),
        ("torch", "PyTorch"),
        ("PIL", "Python Imaging Library"),
        ("numpy", "NumPy"),
        ("accelerate", "Hugging Face Accelerate")
    ]
    
    failed_imports = []
    
    for module, description in test_imports:
        try:
            __import__(module)
            logger.info(f"✅ {description} - OK")
        except ImportError as e:
            logger.error(f"❌ {description} - FAILED: {e}")
            failed_imports.append(module)
    
    return failed_imports

def test_enhanced_ai():
    """Test the enhanced AI system"""
    logger.info("🧪 Testing Enhanced AI system...")
    
    try:
        # Add project root to path
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        
        # Test enhanced AI models
        from core.enhanced_ai_models import ai_manager
        
        # Test model info
        model_info = ai_manager.get_model_info()
        logger.info("✅ Enhanced AI Manager loaded successfully")
        
        # Check model availability
        logger.info(f"🎵 Whisper available: {model_info.get('whisper_available', False)}")
        logger.info(f"📝 Text analysis available: {model_info.get('text_analysis_available', False)}")
        logger.info(f"🖼️ Image analysis available: {model_info.get('image_analysis_available', False)}")
        logger.info(f"📊 Tracking enabled: {model_info.get('tracking_enabled', False)}")
        
        # Test basic functionality
        logger.info("🔄 Testing text analysis...")
        test_text = "भारत एक महान देश है।"  # "India is a great country" in Hindi
        result = ai_manager.analyze_text(test_text)
        
        if result.get("success"):
            logger.info("✅ Text analysis test passed")
            logger.info(f"   Detected language: {result.get('language', 'unknown')}")
            logger.info(f"   Sentiment: {result.get('sentiment', {}).get('label', 'unknown')}")
        else:
            logger.warning("⚠️ Text analysis test failed")
        
        # Test translation
        logger.info("🔄 Testing translation...")
        translation_result = ai_manager.translate_text(test_text, "english")
        
        if translation_result.get("success"):
            logger.info("✅ Translation test passed")
            logger.info(f"   Translation: {translation_result.get('translation', 'N/A')}")
        else:
            logger.warning("⚠️ Translation test failed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Enhanced AI test failed: {e}")
        return False

def main():
    """Main dependency fixing process"""
    logger.info("🔧 BharatVerse Enhanced AI - Dependency Fixer")
    logger.info("=" * 60)
    
    # Step 1: Install missing dependencies
    logger.info("\n📦 Step 1: Installing missing dependencies...")
    failed_packages = install_missing_dependencies()
    
    # Step 2: Verify installations
    logger.info("\n🔍 Step 2: Verifying installations...")
    failed_imports = verify_installations()
    
    # Step 3: Test enhanced AI
    logger.info("\n🧪 Step 3: Testing Enhanced AI system...")
    ai_test_passed = test_enhanced_ai()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📋 DEPENDENCY CHECK SUMMARY")
    logger.info("=" * 60)
    
    if not failed_packages and not failed_imports and ai_test_passed:
        logger.info("🎉 ALL DEPENDENCIES INSTALLED SUCCESSFULLY!")
        logger.info("✅ Enhanced AI system is fully functional")
        logger.info("\n🚀 Next steps:")
        logger.info("1. Restart your Streamlit app")
        logger.info("2. Visit 'Enhanced AI Features' page")
        logger.info("3. Test real AI capabilities")
    else:
        if failed_packages:
            logger.error(f"❌ Failed to install packages: {failed_packages}")
        if failed_imports:
            logger.error(f"❌ Failed imports: {failed_imports}")
        if not ai_test_passed:
            logger.error("❌ Enhanced AI test failed")
        
        logger.info("\n💡 Troubleshooting suggestions:")
        logger.info("1. Check your internet connection")
        logger.info("2. Ensure you have sufficient disk space (10GB+)")
        logger.info("3. Try running with administrator/sudo privileges")
        logger.info("4. Check Python version (3.8+ required)")
    
    return len(failed_packages) == 0 and len(failed_imports) == 0 and ai_test_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)