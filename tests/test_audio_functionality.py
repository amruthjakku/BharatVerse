#!/usr/bin/env python3
"""
Test script for audio functionality
"""

import numpy as np
import soundfile as sf
import tempfile
import os
from pathlib import Path

def test_audio_processing():
    """Test basic audio processing functionality"""
    print("🧪 Testing Audio Processing Functionality")
    print("=" * 50)
    
    try:
        # Test 1: Create dummy audio data
        print("1. Creating test audio data...")
        sample_rate = 44100
        duration = 2  # seconds
        t = np.linspace(0, duration, int(sample_rate * duration))
        frequency = 440  # A4 note
        audio_data = 0.3 * np.sin(2 * np.pi * frequency * t)
        print("✅ Test audio data created")
        
        # Test 2: Save audio file
        print("2. Testing audio file saving...")
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            sf.write(tmp_file.name, audio_data, sample_rate)
            file_size = os.path.getsize(tmp_file.name)
            print(f"✅ Audio file saved: {file_size} bytes")
            
            # Test 3: Read audio file back
            print("3. Testing audio file reading...")
            read_audio, read_sr = sf.read(tmp_file.name)
            print(f"✅ Audio file read: {len(read_audio)} samples at {read_sr} Hz")
            
            # Clean up
            os.unlink(tmp_file.name)
        
        # Test 4: Test audio processor
        print("4. Testing AudioProcessor...")
        try:
            from streamlit_app.audio_processor import AudioProcessor
            processor = AudioProcessor()
            
            # Test processing
            result = processor.process_audio_file(audio_data, sample_rate, {
                'title': 'Test Audio',
                'language': 'English',
                'category': 'Test'
            })
            
            if result['success']:
                print("✅ AudioProcessor working correctly")
                print(f"   - File saved to: {result['filepath']}")
                print(f"   - Duration: {result['metadata']['duration']:.2f}s")
                print(f"   - Features extracted: {len(result['metadata']['features'])} features")
                
                # Clean up test file
                if os.path.exists(result['filepath']):
                    os.unlink(result['filepath'])
            else:
                print(f"❌ AudioProcessor failed: {result['error']}")
                
        except ImportError as e:
            print(f"⚠️  AudioProcessor import failed: {e}")
        
        # Test 5: Test audio recorder component
        print("5. Testing audio libraries...")
        try:
            import sounddevice as sd
            import librosa
            print("✅ sounddevice available")
            print("✅ librosa available")
            
            # Test librosa features
            features = {}
            features['rms_energy'] = float(np.sqrt(np.mean(audio_data**2)))
            features['zero_crossing_rate'] = float(np.mean(librosa.feature.zero_crossing_rate(audio_data)))
            print(f"✅ Feature extraction working (RMS: {features['rms_energy']:.4f})")
            
        except ImportError as e:
            print(f"⚠️  Audio libraries not fully available: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Audio functionality tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_audio_processing()