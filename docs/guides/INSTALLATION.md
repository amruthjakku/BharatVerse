# 🚀 BharatVerse Installation Guide

## Quick Start (Core Features Only)

For basic functionality without audio/video processing:

```bash
# Clone repository
git clone https://github.com/bharatverse/bharatverse.git
cd bharatverse

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install core dependencies
pip install streamlit pandas numpy plotly matplotlib pillow

# Run the application
streamlit run streamlit_app/app.py
```

## Full Installation (All Features)

### System Dependencies

#### macOS
```bash
# Install PortAudio for audio processing
brew install portaudio

# Install system libraries for OpenCV
brew install opencv
```

#### Ubuntu/Debian
```bash
# Install PortAudio for audio processing
sudo apt-get update
sudo apt-get install portaudio19-dev

# Install system libraries for OpenCV
sudo apt-get install libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1
```

#### Windows
```bash
# Download and install PortAudio from http://www.portaudio.com/
# Or use conda: conda install portaudio
```

### Python Dependencies

#### Core Dependencies (Required)
```bash
pip install streamlit>=1.28.0 pandas>=2.0.0 numpy>=1.24.0 plotly>=5.17.0 matplotlib>=3.7.0 pillow>=10.0.0
```

#### Optional Dependencies

**Audio Processing:**
```bash
pip install sounddevice soundfile librosa pydub
```

**Text Analysis:**
```bash
pip install langdetect textstat spacy
```

**Image Processing:**
```bash
pip install opencv-python scikit-image
```

**Word Cloud Generation:**
```bash
pip install wordcloud
```

**AI/ML Features:**
```bash
pip install transformers torch sentence-transformers whisper
```

**API Backend:**
```bash
pip install fastapi uvicorn sqlalchemy
```

## Feature Availability

| Feature | Core Install | Full Install |
|---------|-------------|-------------|
| 🏠 Home Dashboard | ✅ | ✅ |
| 📝 Text Stories | ✅ | ✅ |
| 📷 Image Upload | ✅ | ✅ |
| 🔍 Search & Discovery | ✅ | ✅ |
| 📊 Analytics Dashboard | ✅ | ✅ |
| 🤝 Community Features | ✅ | ✅ |
| 👥 Collaboration | ✅ | ✅ |
| 🎙️ Audio Recording | ❌ | ✅ |
| 🤖 AI Text Analysis | ❌ | ✅ |
| 📈 Word Clouds | ❌ | ✅ |
| 🔤 Auto Transcription | ❌ | ✅ |
| 🖼️ Image Analysis | ❌ | ✅ |

## Troubleshooting

### Common Issues

**1. PortAudio Library Not Found**
```
OSError: PortAudio library not found
```
**Solution:** Install PortAudio system library (see system dependencies above)

**2. OpenCV Import Error**
```
ImportError: libGL.so.1: cannot open shared object file
```
**Solution:** Install OpenGL libraries or use core installation without OpenCV

**3. Module Not Found Errors**
```
ModuleNotFoundError: No module named 'langdetect'
```
**Solution:** Install optional dependencies as needed

### Cloud Deployment

For deployment on Streamlit Cloud, Heroku, or similar platforms:

1. Use `requirements_core.txt` for minimal dependencies
2. Comment out system-dependent packages
3. The app will gracefully handle missing optional dependencies

### Development Setup

For development with all features:

```bash
# Install all dependencies
pip install -r requirements.txt

# Install development tools
pip install pytest black flake8

# Run tests
pytest tests/

# Format code
black streamlit_app/ api/
```

## Performance Tips

1. **Use Core Installation** for faster startup and deployment
2. **Enable Caching** by installing Redis: `pip install redis`
3. **Install Watchdog** for faster file watching: `pip install watchdog`
4. **Use SSD Storage** for better database performance

## Getting Help

- 📚 [Documentation](https://github.com/bharatverse/bharatverse/wiki)
- 🐛 [Report Issues](https://github.com/bharatverse/bharatverse/issues)
- 💬 [Community Discord](https://discord.gg/bharatverse)
- 📧 [Email Support](mailto:team@bharatverse.org)