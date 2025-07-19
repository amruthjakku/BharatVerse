# 🇮🇳 BharatVerse Enhanced - Real AI-Powered Cultural Heritage Platform

<div align="center">
  <img src="https://img.shields.io/badge/BharatVerse-Enhanced_AI-orange?style=for-the-badge" alt="BharatVerse Enhanced">
  
  ### **🤖 Real AI Models • 🎙️ Live Transcription • 🌐 Multi-language • 📊 Advanced Analytics**
  
  <strong>Preserving India's Cultural Heritage with Cutting-Edge AI Technology</strong>
</div>

---

## 🚀 **What's New in Enhanced Version**

### **🤖 Real AI Models**
- **Whisper Integration**: Real-time audio transcription in 22+ Indian languages
- **Advanced NLP**: Sentiment analysis, cultural element detection, keyword extraction
- **Image AI**: Automatic captioning and cultural artifact recognition
- **Translation**: Multi-language translation with confidence scoring

### **🏗️ Enhanced Architecture**
- **PostgreSQL**: Full-text search, advanced indexing, ACID compliance
- **Redis**: High-performance caching and session management
- **MinIO**: Scalable object storage for media files
- **Real-time Processing**: Background AI processing with queue management

### **📊 Advanced Analytics**
- **Cultural Insights**: AI-powered trend analysis and cultural pattern detection
- **Quality Metrics**: Content quality scoring and recommendation systems
- **Performance Monitoring**: Real-time system health and AI model performance

---

## 🛠️ **Installation & Setup**

### **Prerequisites**
- Python 3.8+
- Docker & Docker Compose
- 4GB+ RAM (for AI models)
- 5GB+ free disk space

### **Quick Start**

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd bharatverse

# 2. Install AI dependencies
python install_ai_dependencies.py

# 3. Start the enhanced system
python start_enhanced_system.py
```

### **Docker Deployment**

```bash
# Start all services (PostgreSQL, Redis, MinIO, API, Streamlit)
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f api
```

---

## 🎯 **Enhanced Features**

### **🎙️ Audio Processing**
- **Real-time Transcription**: Whisper-powered speech-to-text
- **Language Detection**: Automatic language identification
- **Cultural Analysis**: Detection of cultural elements in audio content
- **Quality Assessment**: Confidence scoring and audio quality metrics

### **📝 Text Analysis**
- **Sentiment Analysis**: Advanced emotion and sentiment detection
- **Cultural Indicators**: Automatic identification of cultural references
- **Readability Scoring**: Text complexity and accessibility analysis
- **Keyword Extraction**: Intelligent tag generation

### **📷 Image Intelligence**
- **Auto-Captioning**: AI-generated descriptions of cultural images
- **Cultural Recognition**: Detection of festivals, art, architecture
- **Visual Analysis**: Color, composition, and complexity analysis
- **Metadata Extraction**: Automatic tagging and categorization

### **🔍 Advanced Search**
- **Full-text Search**: PostgreSQL-powered semantic search
- **Multi-modal Queries**: Search across audio, text, and images
- **Cultural Filters**: Search by festivals, regions, languages
- **AI-Enhanced Results**: Relevance scoring and recommendation

---

## 🌐 **API Endpoints**

### **Audio Processing**
```http
POST /api/v1/audio/transcribe
Content-Type: multipart/form-data

{
  "file": "audio_file.wav",
  "language": "hi",
  "translate": true
}
```

### **Text Analysis**
```http
POST /api/v1/text/analyze
Content-Type: application/json

{
  "text": "Your text content",
  "language": "hi",
  "translate": true
}
```

### **Image Analysis**
```http
POST /api/v1/image/analyze
Content-Type: multipart/form-data

{
  "file": "image.jpg"
}
```

### **Advanced Search**
```http
POST /api/v1/search
Content-Type: application/json

{
  "query": "Bengali folk songs",
  "content_types": ["audio", "text"],
  "languages": ["bn", "hi"],
  "limit": 20
}
```

---

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=bharatverse
POSTGRES_USER=bharatverse_user
POSTGRES_PASSWORD=secretpassword

# MinIO Configuration
MINIO_HOST=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# AI Model Configuration
TRANSFORMERS_CACHE=/app/models_cache
TORCH_HOME=/app/models_cache
```

### **AI Model Settings**
```python
# Whisper Model Size (base, small, medium, large)
WHISPER_MODEL_SIZE=base

# Enable/Disable specific AI features
ENABLE_TRANSCRIPTION=true
ENABLE_TRANSLATION=true
ENABLE_IMAGE_ANALYSIS=true
ENABLE_SENTIMENT_ANALYSIS=true
```

---

## 📊 **Performance & Monitoring**

### **System Requirements**
- **Minimum**: 2GB RAM, 2 CPU cores, 3GB storage
- **Recommended**: 4GB RAM, 4 CPU cores, 10GB storage
- **Production**: 8GB RAM, 8 CPU cores, 50GB storage

### **AI Model Performance**
- **Whisper Base**: ~1-2x real-time processing
- **Text Analysis**: ~100ms per document
- **Image Captioning**: ~2-3 seconds per image
- **Translation**: ~500ms per paragraph

### **Monitoring Endpoints**
```http
GET /health                    # System health check
GET /api/v1/models/status     # AI model status
GET /api/v1/analytics         # Usage analytics
```

---

## 🚀 **Usage Examples**

### **Audio Transcription**
```python
import requests

# Upload audio file for transcription
with open('folk_song.wav', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/audio/transcribe',
        files={'file': f},
        data={'language': 'hi', 'translate': 'true'}
    )

result = response.json()
print(f"Transcription: {result['transcription']}")
print(f"Translation: {result['translation']['translation']}")
print(f"Cultural Elements: {result['text_analysis']['cultural_indicators']}")
```

### **Text Analysis**
```python
import requests

response = requests.post(
    'http://localhost:8000/api/v1/text/analyze',
    json={
        'text': 'दीवाली का त्योहार खुशियों का त्योहार है',
        'language': 'hi',
        'translate': True
    }
)

result = response.json()
print(f"Sentiment: {result['sentiment']['label']}")
print(f"Cultural Elements: {result['cultural_indicators']}")
print(f"Translation: {result['translation']['translation']}")
```

---

## 🔍 **Troubleshooting**

### **Common Issues**

**AI Models Not Loading**
```bash
# Check dependencies
python -c "import torch, whisper, transformers; print('All dependencies available')"

# Reinstall AI dependencies
python install_ai_dependencies.py
```

**Database Connection Issues**
```bash
# Check Docker services
docker-compose ps

# Restart services
docker-compose restart postgres redis minio
```

**Memory Issues**
```bash
# Check memory usage
docker stats

# Increase Docker memory limit
# Docker Desktop > Settings > Resources > Memory > 4GB+
```

### **Performance Optimization**

**For Development**
- Use Whisper "base" model for faster processing
- Enable model caching
- Use demo mode for UI testing

**For Production**
- Use Whisper "large" model for better accuracy
- Enable Redis caching
- Use CDN for static assets
- Implement load balancing

---

## 🤝 **Contributing**

### **Development Setup**
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run linting
flake8 .
black .
```

### **Adding New AI Models**
1. Add model to `core/ai_models_enhanced.py`
2. Update API endpoints in `api/enhanced_main.py`
3. Add UI components in respective modules
4. Update tests and documentation

---

## 📈 **Roadmap**

### **Phase 1: Core AI Enhancement** ✅
- [x] Real Whisper integration
- [x] Advanced text analysis
- [x] Image captioning
- [x] Enhanced database schema

### **Phase 2: Advanced Features** 🚧
- [ ] Real-time collaboration
- [ ] Advanced search with embeddings
- [ ] Mobile app integration
- [ ] Multi-modal AI search

### **Phase 3: Scale & Performance** 📋
- [ ] Kubernetes deployment
- [ ] Microservices architecture
- [ ] Advanced caching strategies
- [ ] Global CDN integration

---

## 📞 **Support**

### **Documentation**
- [API Documentation](http://localhost:8000/docs)
- [User Guide](./docs/user-guide.md)
- [Developer Guide](./docs/developer-guide.md)

### **Community**
- [GitHub Issues](https://github.com/bharatverse/bharatverse/issues)
- [Discord Community](https://discord.gg/bharatverse)
- [Email Support](mailto:support@bharatverse.org)

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Cultural Data**: All contributed cultural content is licensed under CC-BY 4.0, ensuring open access while respecting contributors.

---

<div align="center">
  <strong>🇮🇳 Made with ❤️ for India's Cultural Heritage 🇮🇳</strong>
  
  <p>
    <a href="#-bharatverse-enhanced---real-ai-powered-cultural-heritage-platform">⬆️ Back to Top</a>
  </p>
</div>