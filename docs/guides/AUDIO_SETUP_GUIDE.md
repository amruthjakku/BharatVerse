# 🎤 Audio Recording Setup Guide for BharatVerse

## ✅ Current Status
Your local development environment has audio recording **working correctly**! 🎉

## 🚀 Deployment Setup

### 1. **Streamlit Cloud Deployment**

**Files already configured:**
- ✅ `requirements.txt` - Contains `sounddevice>=0.4.6` and `soundfile>=0.12.1`
- ✅ `packages.txt` - Contains system dependencies:
  ```
  ffmpeg
  libsndfile1
  portaudio19-dev
  python3-pyaudio
  libportaudio2
  libasound2-dev
  ```

**Deploy steps:**
1. Push your code to GitHub
2. Connect to Streamlit Cloud
3. The system dependencies will be automatically installed
4. Audio recording should work in production

### 2. **Local Development Setup**

**For macOS (your current setup):**
```bash
# System dependency (if not already installed)
brew install portaudio

# Python packages (already in requirements.txt)
pip install sounddevice soundfile
```

**For Ubuntu/Debian:**
```bash
# System dependencies
sudo apt-get update
sudo apt-get install portaudio19-dev python3-pyaudio libportaudio2 libasound2-dev

# Python packages
pip install sounddevice soundfile
```

**For CentOS/RHEL:**
```bash
# System dependencies
sudo yum install portaudio-devel alsa-lib-devel

# Python packages
pip install sounddevice soundfile
```

**For Windows:**
```bash
# Using conda (recommended)
conda install portaudio
pip install sounddevice soundfile

# Or download PortAudio from: https://www.portaudio.com/
```

### 3. **Docker Deployment**

Add to your Dockerfile:
```dockerfile
# Install system dependencies
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    python3-pyaudio \
    libportaudio2 \
    libasound2-dev \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install -r requirements.txt
```

### 4. **Heroku Deployment**

Create `Aptfile`:
```
portaudio19-dev
python3-pyaudio
libportaudio2
libasound2-dev
```

## 🧪 Testing Audio Setup

Run the test script to verify everything works:
```bash
python test_audio.py
```

**Expected output:**
```
🎵 BharatVerse Audio Dependency Test
========================================
🔍 Testing audio recording dependencies...
✅ sounddevice imported successfully
✅ Found X audio devices
✅ Default input device: [Device Name]
✅ Default output device: [Device Name]
✅ soundfile imported successfully
✅ Audio input settings check passed

🎉 All audio dependencies are working correctly!
🎤 Audio recording should be available in BharatVerse
```

## 🔧 Troubleshooting

### Common Issues:

**1. "OSError: PortAudio library not found"**
- **Solution**: Install PortAudio system dependency
- **macOS**: `brew install portaudio`
- **Ubuntu**: `sudo apt-get install portaudio19-dev`

**2. "ImportError: No module named 'sounddevice'"**
- **Solution**: Install Python packages
- `pip install sounddevice soundfile`

**3. "No audio devices found"**
- **Solution**: Check system audio settings
- Ensure microphone permissions are granted
- Test with other audio applications

**4. "Permission denied" on microphone**
- **Solution**: Grant microphone permissions
- **macOS**: System Preferences → Security & Privacy → Microphone
- **Linux**: Check PulseAudio/ALSA configuration

### Fallback Options:

If audio recording still doesn't work:
1. ✅ **Audio file upload** is always available
2. ✅ **Text stories module** for written content
3. ✅ **Visual heritage module** for images
4. ✅ **All other BharatVerse features** work independently

## 🌟 Features Available

**When audio recording works:**
- 🎤 Live audio recording
- 🔤 Real-time transcription
- 🌍 Multi-language support
- 🎵 Audio analysis and insights

**Always available (fallback):**
- 📁 Audio file upload
- 🔤 File transcription
- 📝 Manual text entry
- 🎯 All other app features

## 📞 Support

If you encounter issues:
1. Run `python test_audio.py` to diagnose
2. Check the error messages in the app
3. Refer to this guide for solutions
4. Use the fallback upload feature

**Your BharatVerse app is ready to preserve India's rich audio heritage!** 🇮🇳✨