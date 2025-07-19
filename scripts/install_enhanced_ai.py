#!/usr/bin/env python3
"""
Install Enhanced AI Models for BharatVerse
Downloads and sets up the latest open-source AI models
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a command and handle errors"""
    logger.info(f"🔄 {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        logger.error("❌ Python 3.8+ is required for enhanced AI models")
        return False
    logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_pytorch():
    """Install PyTorch with appropriate backend"""
    logger.info("🔄 Installing PyTorch...")
    
    # Detect if CUDA is available
    try:
        import torch
        if torch.cuda.is_available():
            logger.info("✅ CUDA detected, PyTorch already installed")
            return True
    except ImportError:
        pass
    
    # Install PyTorch (CPU version for compatibility)
    commands = [
        "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu",
    ]
    
    for cmd in commands:
        if not run_command(cmd, "Installing PyTorch"):
            return False
    
    return True

def install_transformers():
    """Install latest Transformers and related packages"""
    logger.info("🔄 Installing Transformers and NLP packages...")
    
    commands = [
        "pip install transformers>=4.36.0",
        "pip install accelerate>=0.25.0",
        "pip install datasets>=2.15.0",
        "pip install sentence-transformers>=2.2.2",
        "pip install optimum>=1.16.0"
    ]
    
    for cmd in commands:
        if not run_command(cmd, f"Installing {cmd.split()[2]}"):
            return False
    
    return True

def install_audio_packages():
    """Install audio processing packages"""
    logger.info("🔄 Installing audio processing packages...")
    
    commands = [
        "pip install openai-whisper>=20231117",
        "pip install librosa>=0.10.1",
        "pip install soundfile>=0.12.1"
    ]
    
    for cmd in commands:
        if not run_command(cmd, f"Installing {cmd.split()[2]}"):
            return False
    
    return True

def install_vision_packages():
    """Install vision processing packages"""
    logger.info("🔄 Installing vision processing packages...")
    
    commands = [
        "pip install Pillow>=10.1.0",
        "pip install opencv-python>=4.8.1",
        "pip install timm>=0.9.12"
    ]
    
    for cmd in commands:
        if not run_command(cmd, f"Installing {cmd.split()[2]}"):
            return False
    
    return True

def install_language_packages():
    """Install language processing packages"""
    logger.info("🔄 Installing language processing packages...")
    
    commands = [
        "pip install langdetect>=1.0.9",
        "pip install nltk>=3.8.1"
    ]
    
    for cmd in commands:
        if not run_command(cmd, f"Installing {cmd.split()[2]}"):
            return False
    
    return True

def download_models():
    """Download and cache AI models"""
    logger.info("🔄 Downloading AI models (this may take a while)...")
    
    try:
        # Test model loading
        logger.info("📥 Testing Whisper model download...")
        import whisper
        model = whisper.load_model("base")
        logger.info("✅ Whisper base model downloaded successfully")
        
        logger.info("📥 Testing Transformers models...")
        from transformers import pipeline
        
        # Download sentiment analysis model
        sentiment_analyzer = pipeline("sentiment-analysis", 
                                    model="cardiffnlp/twitter-xlm-roberta-base-sentiment")
        logger.info("✅ Sentiment analysis model downloaded")
        
        # Download image captioning model (smaller version for testing)
        try:
            image_captioner = pipeline("image-to-text", 
                                     model="Salesforce/blip-image-captioning-base")
            logger.info("✅ Image captioning model downloaded")
        except Exception as e:
            logger.warning(f"⚠️ Image captioning model download failed: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Model download failed: {e}")
        return False

def verify_installation():
    """Verify that all components are working"""
    logger.info("🔍 Verifying installation...")
    
    try:
        # Test enhanced AI manager
        sys.path.append(str(Path(__file__).parent.parent))
        from core.enhanced_ai_models import ai_manager
        
        # Test model info
        model_info = ai_manager.get_model_info()
        logger.info(f"✅ Enhanced AI Manager loaded successfully")
        logger.info(f"   Whisper available: {model_info['whisper_available']}")
        logger.info(f"   Text analysis available: {model_info['text_analysis_available']}")
        logger.info(f"   Image analysis available: {model_info['image_analysis_available']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        return False

def main():
    """Main installation process"""
    logger.info("🚀 Starting Enhanced AI Models Installation for BharatVerse")
    logger.info("=" * 60)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    # Installation steps
    steps = [
        ("PyTorch", install_pytorch),
        ("Transformers", install_transformers),
        ("Audio packages", install_audio_packages),
        ("Vision packages", install_vision_packages),
        ("Language packages", install_language_packages),
        ("AI models", download_models),
        ("Installation verification", verify_installation)
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        logger.info(f"\n📦 Installing {step_name}...")
        if not step_func():
            failed_steps.append(step_name)
            logger.error(f"❌ {step_name} installation failed")
        else:
            logger.info(f"✅ {step_name} installation completed")
    
    # Summary
    logger.info("\n" + "=" * 60)
    if not failed_steps:
        logger.info("🎉 Enhanced AI Models installation completed successfully!")
        logger.info("You can now use the latest AI features in BharatVerse:")
        logger.info("  • Advanced audio transcription with Whisper Large-v3")
        logger.info("  • Multilingual text analysis and translation")
        logger.info("  • Cultural context-aware image analysis")
        logger.info("  • Real-time sentiment and emotion detection")
        logger.info("\n🚀 Start the application and visit the 'Enhanced AI Features' page!")
    else:
        logger.error(f"❌ Installation completed with {len(failed_steps)} failed steps:")
        for step in failed_steps:
            logger.error(f"  • {step}")
        logger.info("\n💡 You can still use basic features. Try running the installation again.")
    
    return len(failed_steps) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)