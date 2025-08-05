#!/usr/bin/env python3
"""
Test script to check if audio recording dependencies are properly installed
"""

import sys

def test_audio_dependencies():
    """Test if audio recording dependencies are available"""
    print("🔍 Testing audio recording dependencies...")
    
    # Test 1: Import sounddevice
    try:
        import sounddevice as sd
        print("✅ sounddevice imported successfully")
        
        # Test device listing
        devices = sd.query_devices()
        print(f"✅ Found {len(devices)} audio devices")
        
        # Show default devices
        try:
            default_input = sd.default.device[0]
            default_output = sd.default.device[1]
            print(f"✅ Default input device: {devices[default_input]['name']}")
            print(f"✅ Default output device: {devices[default_output]['name']}")
        except Exception as e:
            print(f"⚠️  Could not get default devices: {e}")
            
    except ImportError as e:
        print(f"❌ sounddevice import failed: {e}")
        return False
    except OSError as e:
        print(f"❌ sounddevice system error: {e}")
        print("💡 This usually means PortAudio is not installed")
        return False
    
    # Test 2: Import soundfile
    try:
        import soundfile as sf
        print("✅ soundfile imported successfully")
    except ImportError as e:
        print(f"❌ soundfile import failed: {e}")
        return False
    
    # Test 3: Test basic recording capability (without actually recording)
    try:
        # Just test if we can query recording parameters
        sample_rate = 44100
        channels = 1
        duration = 0.1  # Very short test
        
        # This should work if PortAudio is properly installed
        sd.check_input_settings(device=None, channels=channels, samplerate=sample_rate)
        print("✅ Audio input settings check passed")
        
    except Exception as e:
        print(f"❌ Audio input test failed: {e}")
        return False
    
    print("\n🎉 All audio dependencies are working correctly!")
    print("🎤 Audio recording should be available in BharatVerse")
    return True

def show_installation_help():
    """Show installation instructions"""
    print("\n🔧 To fix audio recording issues:")
    print("\n📦 Install system dependencies:")
    print("  macOS:     brew install portaudio")
    print("  Ubuntu:    sudo apt-get install portaudio19-dev python3-pyaudio")
    print("  CentOS:    sudo yum install portaudio-devel")
    print("  Windows:   conda install portaudio")
    
    print("\n🐍 Install Python packages:")
    print("  uv pip install sounddevice soundfile")
    
    print("\n☁️  For Streamlit Cloud, add to packages.txt:")
    print("  portaudio19-dev")
    print("  python3-pyaudio")
    print("  libportaudio2")
    print("  libasound2-dev")

if __name__ == "__main__":
    print("🎵 BharatVerse Audio Dependency Test")
    print("=" * 40)
    
    success = test_audio_dependencies()
    
    if not success:
        show_installation_help()
        sys.exit(1)
    else:
        print("\n✨ Ready to preserve India's audio heritage!")
        sys.exit(0)