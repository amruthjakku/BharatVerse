#!/usr/bin/env python3
"""
Installation script for BharatVerse AI dependencies
This script installs all required AI models and dependencies
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def run_command(command, description=""):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Success!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def check_system_requirements():
    """Check system requirements"""
    print("\n🔍 Checking System Requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"❌ Python {python_version.major}.{python_version.minor} detected. Python 3.8+ required.")
        return False
    else:
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} detected")
    
    # Check platform
    system = platform.system()
    print(f"✅ Platform: {system}")
    
    # Check available disk space (rough estimate)
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        free_gb = free // (1024**3)
        if free_gb < 5:
            print(f"⚠️  Warning: Only {free_gb}GB free space. AI models require ~3-5GB")
        else:
            print(f"✅ Available space: {free_gb}GB")
    except:
        print("⚠️  Could not check disk space")
    
    return True

def install_system_dependencies():
    """Install system-level dependencies"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        print("\n🍎 Installing macOS dependencies...")
        
        # Check if Homebrew is installed
        if run_command("which brew", "Checking for Homebrew"):
            # Install PortAudio for audio processing
            run_command("brew install portaudio", "Installing PortAudio")
            # Install FFmpeg for audio/video processing
            run_command("brew install ffmpeg", "Installing FFmpeg")
        else:
            print("⚠️  Homebrew not found. Please install manually:")
            print("   - PortAudio: for audio recording")
            print("   - FFmpeg: for audio/video processing")
    
    elif system == "Linux":
        print("\n🐧 Installing Linux dependencies...")
        
        # Try different package managers
        if run_command("which apt-get", "Checking for apt-get"):
            run_command("sudo apt-get update", "Updating package list")
            run_command("sudo apt-get install -y portaudio19-dev python3-pyaudio ffmpeg", "Installing audio dependencies")
        elif run_command("which yum", "Checking for yum"):
            run_command("sudo yum install -y portaudio-devel python3-pyaudio ffmpeg", "Installing audio dependencies")
        else:
            print("⚠️  Please install manually:")
            print("   - portaudio19-dev (or portaudio-devel)")
            print("   - python3-pyaudio")
            print("   - ffmpeg")
    
    else:
        print(f"⚠️  Unsupported system: {system}")
        print("Please install audio dependencies manually")

def install_python_dependencies():
    """Install Python dependencies"""
    print("\n🐍 Installing Python Dependencies...")
    
    # Upgrade pip first
    run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip")
    
    # Install core dependencies
    core_deps = [
        "torch>=2.1.0",
        "torchvision>=0.16.0",
        "transformers>=4.36.0",
        "openai-whisper>=20231117",
        "sounddevice>=0.4.6",
        "soundfile>=0.12.1",
        "librosa>=0.10.0",
        "langdetect>=1.0.9",
        "opencv-python>=4.8.0",
        "scikit-image>=0.21.0",
        "Pillow>=10.0.0"
    ]
    
    for dep in core_deps:
        run_command(f"{sys.executable} -m pip install {dep}", f"Installing {dep}")
    
    # Install remaining requirements
    requirements_file = Path(__file__).parent / "requirements.txt"
    if requirements_file.exists():
        run_command(f"{sys.executable} -m pip install -r {requirements_file}", "Installing from requirements.txt")

def download_ai_models():
    """Download and cache AI models"""
    print("\n🤖 Downloading AI Models...")
    
    # Create a test script to download models
    test_script = """
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

try:
    print("Loading Whisper model...")
    import whisper
    model = whisper.load_model("base")
    print("✅ Whisper model loaded successfully")
except Exception as e:
    print(f"❌ Whisper model failed: {e}")

try:
    print("Loading text analysis models...")
    from transformers import pipeline
    sentiment_analyzer = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
    print("✅ Sentiment analysis model loaded successfully")
except Exception as e:
    print(f"❌ Sentiment analysis model failed: {e}")

try:
    print("Loading image captioning model...")
    from transformers import BlipProcessor, BlipForConditionalGeneration
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    print("✅ Image captioning model loaded successfully")
except Exception as e:
    print(f"❌ Image captioning model failed: {e}")

print("\\n🎉 Model download complete!")
"""
    
    # Write and run test script
    test_file = Path(__file__).parent / "test_models.py"
    with open(test_file, 'w') as f:
        f.write(test_script)
    
    run_command(f"{sys.executable} {test_file}", "Testing and downloading AI models")
    
    # Clean up
    if test_file.exists():
        test_file.unlink()

def verify_installation():
    """Verify the installation"""
    print("\n🔍 Verifying Installation...")
    
    verification_script = """
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

try:
    from core.ai_models_enhanced import ai_manager
    status = ai_manager.get_model_status()
    
    print("🤖 AI Models Status:")
    for model, available in status.items():
        if isinstance(available, dict):
            for sub_model, sub_status in available.items():
                print(f"  {sub_model}: {'✅' if sub_status else '❌'}")
        else:
            print(f"  {model}: {'✅' if available else '❌'}")
    
    print("\\n🎉 Installation verification complete!")
    
except Exception as e:
    print(f"❌ Verification failed: {e}")
    print("Some components may not be working correctly.")
"""
    
    # Write and run verification script
    verify_file = Path(__file__).parent / "verify_install.py"
    with open(verify_file, 'w') as f:
        f.write(verification_script)
    
    run_command(f"{sys.executable} {verify_file}", "Verifying installation")
    
    # Clean up
    if verify_file.exists():
        verify_file.unlink()

def main():
    """Main installation process"""
    print("🇮🇳 BharatVerse AI Dependencies Installation")
    print("=" * 60)
    
    # Check system requirements
    if not check_system_requirements():
        print("❌ System requirements not met. Exiting.")
        sys.exit(1)
    
    # Install system dependencies
    install_system_dependencies()
    
    # Install Python dependencies
    install_python_dependencies()
    
    # Download AI models
    download_ai_models()
    
    # Verify installation
    verify_installation()
    
    print("\n" + "=" * 60)
    print("🎉 Installation Complete!")
    print("=" * 60)
    print("\n📝 Next Steps:")
    print("1. Start the enhanced API server:")
    print("   python api/enhanced_main.py")
    print("\n2. Start the Streamlit app:")
    print("   streamlit run streamlit_app/app.py")
    print("\n3. Toggle 'Use Real Data' in the sidebar to use AI models")
    print("\n4. If you encounter issues, check the logs and ensure all dependencies are installed")
    
    print("\n💡 Tips:")
    print("- First AI model usage may be slow as models are loaded")
    print("- Audio recording requires microphone permissions")
    print("- Large models may require significant RAM (4GB+ recommended)")

if __name__ == "__main__":
    main()