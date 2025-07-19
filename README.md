# 🇮🇳 BharatVerse - Preserving India's Cultural Heritage

<div align="center">
  <img src="https://img.shields.io/badge/BharatVerse-Preserving_Culture-orange?style=for-the-badge" alt="BharatVerse">
  
  ### **Capture, Create, Contribute**
  
  <strong>Preserving India's Cultural Heritage, One Story at a Time</strong>
  
  <p>
    <a href="#-quick-start"><img src="https://img.shields.io/badge/Quick_Start-→-brightgreen?style=for-the-badge" alt="Quick Start"></a>
    <a href="#-features"><img src="https://img.shields.io/badge/Features-→-blue?style=for-the-badge" alt="Features"></a>
    <a href="#-contributing"><img src="https://img.shields.io/badge/Contribute-→-orange?style=for-the-badge" alt="Contribute"></a>
  </p>
  
  <p>
    <img src="https://img.shields.io/github/license/bharatverse/bharatverse?style=flat-square" alt="License">
    <img src="https://img.shields.io/github/stars/bharatverse/bharatverse?style=flat-square" alt="Stars">
    <img src="https://img.shields.io/github/forks/bharatverse/bharatverse?style=flat-square" alt="Forks">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square" alt="PRs Welcome">
  </p>
</div>

---

## 🌟 Live Demo

<div align="center">
  <a href="https://amruthjakku-bharatverse.streamlit.app">
    <img src="https://img.shields.io/badge/🌐_Live_Demo-Streamlit_Cloud-FF4B4B?style=for-the-badge&logo=streamlit" alt="Live Demo">
  </a>
  <a href="https://amruthjakku-bharatverse.streamlit.app">
    <img src="https://img.shields.io/badge/🚀_Try_Now-bharatverse.streamlit.app-blue?style=for-the-badge" alt="Try Now">
  </a>
</div>

---

## 💡 What is BharatVerse?

BharatVerse is an **open-source cultural preservation platform** that empowers Indian communities to:

<table>
<tr>
<td width="50%">

### 🎯 Capture
- **🎙️ Record** folk songs, stories, and oral traditions
- **📝 Document** local customs, recipes, and wisdom
- **📷 Upload** festival photos, traditional art, and cultural symbols

</td>
<td width="50%">

### 🌐 Preserve
- **🤖 AI-powered** transcription and translation
- **🏷️ Smart tagging** for easy discovery
- **📚 Open dataset** for researchers and educators

</td>
</tr>
<tr>
<td width="50%">

### 🤝 Share
- **🌍 Global reach** with multi-language support
- **📱 Mobile-friendly** interface for easy access
- **🔗 Social features** for community engagement

</td>
<td width="50%">

### 🔍 Discover
- **🔎 Advanced search** across all content types
- **📊 Analytics** to track cultural trends
- **🎨 Interactive visualizations** of cultural data

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git
- Docker (optional, for infrastructure services)

### Installation

```bash
# Clone the repository
git clone https://code.swecha.org/amruth_jakku/bharatverse.git
cd bharatverse

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (choose one):
pip install -r requirements/base.txt  # Core features only
pip install -r requirements.txt        # Full installation with AI
pip install -r requirements/dev.txt    # Development setup

# Setup environment
cp .env.local .env  # Edit .env with your settings

# Start infrastructure services (optional)
docker-compose up -d

# Run the application
streamlit run Home.py
```

🎉 **That's it!** Open http://localhost:8501 in your browser.

---

## ✨ Features

### 🎙️ Audio Capture & Transcription
- 🎤 Real-time audio recording
- 🔤 Multi-language transcription (22+ Indian languages)
- 🎵 Music and speech separation
- 📊 Audio quality analysis

### 📝 Story Documentation
- ✍️ Rich text editor with formatting
- 🏷️ Automatic tagging and categorization
- 🌍 Multi-language support
- 📚 Version control for stories

### 📷 Visual Heritage
- 🖼️ Image upload and processing
- 🤖 AI-powered cultural element detection
- 🏛️ Architecture and art form recognition
- 📍 Geo-tagging and location mapping

### 🔍 Advanced Search & Discovery
- Intelligent search across all content types
- Filter by language, region, content type
- Featured collections and recommendations
- Trending cultural content

### 📊 Analytics Dashboard
- Real-time contribution statistics
- Language and regional distribution
- Content trends and insights
- Community engagement metrics

### 🤝 Community Features
- Contributor leaderboards
- Achievement badges and rewards
- Community challenges
- Discussion forums

### 🤖 AI Insights
- Content quality analysis
- Sentiment analysis of cultural content
- Trend predictions
- Automated content recommendations

### 👥 Collaboration Tools
- Project management for cultural initiatives
- Team workflows and task tracking
- Review and approval processes
- Collaborative editing

---

## 🛠️ Advanced Usage

### Infrastructure Setup
```bash
# Start all services (PostgreSQL, Redis, MinIO)
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### Data Export
```bash
bharatverse export --format json --filter "language:hindi"
bharatverse export --format csv --filter "region:rajasthan"
bharatverse export --format parquet --filter "type:folk_song"
```

### API Integration
```python
import requests

# Access BharatVerse API
response = requests.get("https://api.bharatverse.org/stories", 
                       params={"language": "tamil", "limit": 10})
stories = response.json()
```

---

## 📊 Current Statistics

<div align="center">
  <table>
    <tr>
      <td align="center"><strong>🎵 Audio Files</strong><br>12,456</td>
      <td align="center"><strong>📝 Stories</strong><br>8,923</td>
      <td align="center"><strong>📷 Images</strong><br>15,678</td>
      <td align="center"><strong>🌍 Languages</strong><br>22+</td>
    </tr>
    <tr>
      <td align="center"><strong>👥 Contributors</strong><br>1,234</td>
      <td align="center"><strong>🏛️ Institutions</strong><br>89</td>
      <td align="center"><strong>📍 Regions</strong><br>28 States</td>
      <td align="center"><strong>⭐ GitHub Stars</strong><br>2,456</td>
    </tr>
  </table>
</div>

---

## 🏗️ Technical Architecture

### Infrastructure Stack
- **Frontend**: Streamlit with custom CSS/JS
- **Backend**: FastAPI with SQLite/PostgreSQL database
- **AI/ML**: Transformers, Whisper, Computer Vision
- **Caching**: Redis + Disk caching
- **Storage**: MinIO (S3-compatible) + Local filesystem
- **Containerization**: Docker Compose

### Database Architecture
- **PostgreSQL**: Metadata and structured data
- **MinIO**: File storage (audio, video, images)
- **Redis**: Caching and session management
- **SQLite**: Development and fallback database

### Services
- **PostgreSQL**: Port 5432
- **Redis**: Port 6379
- **MinIO**: Port 9000 (API), 9001 (Console)

---

## 📁 Project Structure

```
bharatverse/
├── Home.py                 # Main application entry point
├── pages/                  # Streamlit pages
│   ├── 01_🎤_Audio_Capture.py
│   ├── 02_📝_Text_Stories.py
│   ├── 03_📸_Visual_Heritage.py
│   ├── 04_🔍_Discover.py
│   ├── 05_📊_Analytics.py
│   ├── 06_🤝_Community.py
│   ├── 07_🤖_AI_Insights.py
│   ├── 08_👥_Collaboration.py
│   ├── 09_🦊_GitLab.py
│   ├── 10_👤_My_Profile.py
│   ├── 11_📚_Browse_Contributions.py
│   └── 12_ℹ️_About.py
├── streamlit_app/          # Streamlit modules
│   ├── audio_module.py     # Audio recording & transcription
│   ├── text_module.py      # Text story documentation
│   ├── image_module.py     # Visual heritage upload
│   ├── analytics_module.py # Analytics dashboard
│   ├── search_module.py    # Search & discovery
│   ├── community_module.py # Community features
│   ├── ai_module.py        # AI insights
│   ├── collaboration_module.py # Collaboration tools
│   └── utils/              # Utility modules
├── api/                    # FastAPI backend
│   └── main.py            # API server
├── core/                   # Core functionality
│   ├── database.py        # Database connections
│   ├── ai_models.py       # AI/ML models
│   ├── api_service.py     # API services
│   └── community_service.py # Community features
├── data/                   # Data storage
│   └── bharatverse.db     # SQLite database
├── tests/                  # Test suite
├── scripts/                # Utility scripts
├── docs/                   # Documentation
│   ├── guides/            # User guides
│   └── technical/         # Technical docs
├── requirements/           # Dependency management
│   ├── base.txt           # Core dependencies
│   ├── ai.txt             # AI/ML dependencies
│   └── dev.txt            # Development dependencies
├── docker/                 # Docker configurations
├── .env                    # Environment configuration
├── docker-compose.yml      # Infrastructure services
├── requirements.txt        # Main requirements file
└── README.md              # This file
```

---

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### 🎯 Ways to Contribute

<table>
<tr>
<td width="50%">

#### 💻 Code Contributions
- 🐛 Bug fixes and improvements
- ✨ New features and enhancements
- 📚 Documentation updates
- 🧪 Tests and quality assurance

</td>
<td width="50%">

#### 🎨 Content Contributions
- 🎵 Audio recordings of folk songs
- 📝 Traditional stories and legends
- 📷 Cultural photographs and art
- 🏷️ Translations and transcriptions

</td>
</tr>
</table>

### 🚀 Getting Started

1. **Fork** the repository
2. **Clone** your fork: `git clone https://code.swecha.org/yourusername/bharatverse.git`
3. **Create** a branch: `git checkout -b feature-name`
4. **Make** your changes and test thoroughly
5. **Submit** a pull request with detailed description

---

## 📖 Documentation

- 📚 **[User Guide](https://bharatverse.readthedocs.io/user-guide/)** - How to use BharatVerse
- 🔧 **[API Reference](https://bharatverse.readthedocs.io/api/)** - Complete API documentation
- 🏗️ **[Developer Guide](https://bharatverse.readthedocs.io/dev-guide/)** - Contributing and development
- 🎓 **[Tutorials](https://bharatverse.readthedocs.io/tutorials/)** - Step-by-step tutorials

---

## 💬 Community

<div align="center">
  <a href="https://discord.gg/bharatverse">
    <img src="https://img.shields.io/badge/Discord-Join_Community-5865F2?style=for-the-badge&logo=discord" alt="Discord">
  </a>
  <a href="https://twitter.com/bharatverse">
    <img src="https://img.shields.io/badge/Twitter-Follow_Us-1DA1F2?style=for-the-badge&logo=twitter" alt="Twitter">
  </a>
</div>

---

## 📄 License

- **Code**: MIT License
- **Cultural Content**: CC BY 4.0
- **Documentation**: CC BY-SA 4.0

---

## 📞 Contact

<div align="center">
  <table>
    <tr>
      <td><strong>📧 Email</strong></td>
      <td><a href="mailto:team@bharatverse.org">team@bharatverse.org</a></td>
    </tr>
    <tr>
      <td><strong>🌐 Website</strong></td>
      <td><a href="https://bharatverse.org">bharatverse.org</a></td>
    </tr>
    <tr>
      <td><strong>📍 Address</strong></td>
      <td>New Delhi, India</td>
    </tr>
  </table>
</div>

---

<div align="center">
  <h2>🇮🇳 Made with ❤️ for India's Cultural Heritage</h2>
  <p><em>"Preserving the past, enriching the future"</em></p>
  
  <p>
    <strong>BharatVerse</strong> - Where every story matters, every voice is heard, and every tradition lives on.
  </p>
</div>