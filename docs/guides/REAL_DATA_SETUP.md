# 🚀 BharatVerse Real Data Integration Setup Guide

## Overview
This guide will help you set up the complete BharatVerse system with real data integration. When you enable the "Use Real Data" toggle in the sidebar, the application will fetch data from the API server instead of showing mock data.

## 📋 Prerequisites

### 1. Database Setup
You'll need the following databases running:

#### PostgreSQL
```bash
# Install PostgreSQL
brew install postgresql  # macOS
# or
sudo apt-get install postgresql postgresql-contrib  # Ubuntu

# Start PostgreSQL
brew services start postgresql  # macOS
# or
sudo systemctl start postgresql  # Ubuntu

# Create database and user
createdb bharatverse
createuser -s bharatverse_user
```

#### Redis
```bash
# Install Redis
brew install redis  # macOS
# or
sudo apt-get install redis-server  # Ubuntu

# Start Redis
brew services start redis  # macOS
# or
sudo systemctl start redis-server  # Ubuntu
```

#### MinIO (S3-compatible storage)
```bash
# Install MinIO
brew install minio  # macOS
# or download from https://min.io/download

# Start MinIO
minio server /path/to/data --console-address ":9001"
```

### 2. Environment Variables
Create a `.env` file in the project root:

```env
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=bharatverse
POSTGRES_USER=bharatverse_user
POSTGRES_PASSWORD=your_password_here

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# MinIO Configuration
MINIO_HOST=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=False

# API Configuration
CORS_ORIGINS=http://localhost:8501,http://127.0.0.1:8501
```

## 🔧 Installation Steps

### 1. Install Dependencies
```bash
cd /Users/jakkuamruth/Downloads/bharatverse
pip install -r requirements.txt
```

### 2. Start the System
You have two options:

#### Option A: Use the startup script (Recommended)
```bash
python start_system.py
```

#### Option B: Manual startup
```bash
# Terminal 1: Start API server
uvicorn core.api_service:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Start Streamlit app
streamlit run streamlit_app/app.py --server.port 8501
```

### 3. Access the Application
- **Streamlit App**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

## 🎯 How Real Data Integration Works

### API Endpoints
The system now includes these API endpoints:

#### Core Endpoints
- `GET /api/v1/stats` - Platform statistics
- `GET /api/v1/content/recent` - Recent contributions
- `POST /api/v1/search` - Search content
- `GET /api/v1/content/{id}` - Get specific content

#### Community Endpoints
- `GET /api/v1/community/stats` - Community statistics
- `GET /api/v1/community/leaderboard` - Community leaderboard

#### Analytics Endpoints
- `GET /api/v1/analytics/extended` - Extended analytics data

### Frontend Integration
The Streamlit app checks the "Use Real Data" toggle and:
- **OFF**: Shows mock data for demonstration
- **ON**: Fetches real data from API endpoints

### Data Flow
1. User toggles "Use Real Data" in sidebar
2. Frontend calls utility functions in `mock_data_handler.py`
3. Utility functions make HTTP requests to API endpoints
4. API queries the database and returns real data
5. Frontend displays the real data

## 🛠️ Testing the Integration

### 1. Test API Endpoints
```bash
# Test health check
curl http://localhost:8000/health

# Test statistics
curl http://localhost:8000/api/v1/stats

# Test community stats
curl http://localhost:8000/api/v1/community/stats

# Test recent content
curl http://localhost:8000/api/v1/content/recent
```

### 2. Test Frontend Integration
1. Open the Streamlit app at http://localhost:8501
2. Toggle "Use Real Data" OFF - you should see mock data
3. Toggle "Use Real Data" ON - you should see real data from API

## 🔍 Troubleshooting

### Common Issues

#### API Server Won't Start
- Check if PostgreSQL, Redis, and MinIO are running
- Verify environment variables in `.env`
- Check port 8000 is not in use

#### No Real Data Showing
- Ensure API server is running on port 8000
- Check browser console for network errors
- Verify database contains data

#### Database Connection Errors
- Check PostgreSQL is running: `brew services list | grep postgresql`
- Verify database credentials in `.env`
- Test connection: `psql -h localhost -U bharatverse_user -d bharatverse`

### Adding Sample Data
To test real data integration, you can add sample data:

```bash
# Use the test_integration.py script
python test_integration.py
```

## 🚀 Next Steps

### 1. Upload Content
Use the Streamlit app to upload:
- Audio files (with AI transcription)
- Text stories
- Images (with AI captioning)

### 2. Monitor Real Data
- Check the Analytics page for real usage statistics
- View the Community page for actual contributor data
- Browse real contributions on the Browse page

### 3. Extend the System
- Add more API endpoints as needed
- Implement user authentication
- Add more analytics features

## 📊 Features Available with Real Data

### ✅ Currently Working
- **Statistics**: Total contributions, languages, content types
- **Recent Contributions**: Live feed of uploaded content
- **Community Stats**: Real contributor counts and leaderboard
- **Content Search**: Search through actual uploaded content

### 🔄 In Development
- **Advanced Analytics**: Time series, quality metrics
- **User Profiles**: Detailed contributor information
- **Community Features**: Challenges, discussions, projects

## 🎉 Success!

Your BharatVerse system is now fully integrated with real data! The "Use Real Data" toggle in the sidebar will seamlessly switch between demonstration mode and live data from your API server.

For any issues or questions, refer to the troubleshooting section or check the API documentation at http://localhost:8000/docs.
