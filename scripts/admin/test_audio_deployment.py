#!/usr/bin/env python3
"""
Test script to verify audio functionality after deployment
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

def test_audio_imports():
    """Test if audio libraries can be imported"""
    print("🧪 Testing Audio Library Imports...")
    
    results = {}
    
    # Test sounddevice
    try:
        import sounddevice as sd
        import soundfile as sf
        results['sounddevice'] = "✅ Available"
        print(f"   sounddevice: ✅ Available (version: {sd.__version__})")
    except (ImportError, OSError) as e:
        results['sounddevice'] = f"❌ Error: {e}"
        print(f"   sounddevice: ❌ Error: {e}")
    
    # Test PyAudio
    try:
        import pyaudio
        results['pyaudio'] = "✅ Available"
        print(f"   pyaudio: ✅ Available")
    except (ImportError, OSError) as e:
        results['pyaudio'] = f"❌ Error: {e}"
        print(f"   pyaudio: ❌ Error: {e}")
    
    # Test wave (built-in)
    try:
        import wave
        results['wave'] = "✅ Available"
        print(f"   wave: ✅ Available (built-in)")
    except ImportError as e:
        results['wave'] = f"❌ Error: {e}"
        print(f"   wave: ❌ Error: {e}")
    
    return results

def test_environment_detection():
    """Test cloud environment detection"""
    print("\n🌐 Testing Environment Detection...")
    
    try:
        from streamlit_app.audio_module import is_cloud_environment
        is_cloud = is_cloud_environment()
        print(f"   Cloud Environment: {'✅ Yes' if is_cloud else '❌ No'}")
        print(f"   Current Path: {os.getcwd()}")
        
        # Check for cloud indicators
        cloud_indicators = [
            ('/mount/src/', 'Streamlit Cloud'),
            ('/app/', 'Heroku'),
            ('/workspace/', 'GitHub Codespaces'),
            ('STREAMLIT_CLOUD' in os.environ, 'Streamlit Cloud Env'),
            ('HEROKU' in os.environ, 'Heroku Env'),
            ('CODESPACE_NAME' in os.environ, 'Codespaces Env')
        ]
        
        for indicator, name in cloud_indicators:
            if isinstance(indicator, bool):
                status = "✅ Detected" if indicator else "❌ Not found"
            else:
                status = "✅ Detected" if indicator in os.getcwd() else "❌ Not found"
            print(f"   {name}: {status}")
        
        return is_cloud
    except Exception as e:
        print(f"   ❌ Error testing environment: {e}")
        return None

def test_audio_module_import():
    """Test if audio module can be imported"""
    print("\n📦 Testing Audio Module Import...")
    
    try:
        from streamlit_app.audio_module import AUDIO_AVAILABLE, AUDIO_BACKEND, AUDIO_IMPORT_ERROR
        print(f"   Audio Available: {AUDIO_AVAILABLE}")
        print(f"   Audio Backend: {AUDIO_BACKEND}")
        if AUDIO_IMPORT_ERROR:
            print(f"   Import Error: {AUDIO_IMPORT_ERROR}")
        return True
    except Exception as e:
        print(f"   ❌ Error importing audio module: {e}")
        return False

def test_system_dependencies():
    """Test if system dependencies are available"""
    print("\n🔧 Testing System Dependencies...")
    
    import subprocess
    
    dependencies = [
        ('portaudio', 'pkg-config --exists portaudio-2.0'),
        ('libsndfile', 'pkg-config --exists sndfile'),
        ('ffmpeg', 'which ffmpeg'),
    ]
    
    results = {}
    for name, command in dependencies:
        try:
            result = subprocess.run(command.split(), capture_output=True, text=True)
            if result.returncode == 0:
                results[name] = "✅ Available"
                print(f"   {name}: ✅ Available")
            else:
                results[name] = "❌ Not found"
                print(f"   {name}: ❌ Not found")
        except Exception as e:
            results[name] = f"❌ Error: {e}"
            print(f"   {name}: ❌ Error: {e}")
    
    return results

def main():
    """Run all audio tests"""
    print("🎵 BharatVerse Audio Deployment Test")
    print("=" * 50)
    
    # Test imports
    import_results = test_audio_imports()
    
    # Test environment
    is_cloud = test_environment_detection()
    
    # Test module import
    module_import = test_audio_module_import()
    
    # Test system dependencies
    system_deps = test_system_dependencies()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    
    audio_working = any("✅" in str(result) for result in import_results.values())
    print(f"Audio Libraries: {'✅ Working' if audio_working else '❌ Not Working'}")
    print(f"Environment: {'☁️ Cloud' if is_cloud else '🖥️ Local'}")
    print(f"Module Import: {'✅ Success' if module_import else '❌ Failed'}")
    
    if audio_working:
        print("\n🎉 Audio functionality should work!")
    else:
        print("\n⚠️ Audio functionality may not work properly.")
        print("   Check the packages.txt file is in the root directory.")
        print("   Ensure all system dependencies are installed.")
    
    return audio_working

if __name__ == "__main__":
    main()