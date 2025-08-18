# 🏛️ BharatVerse Troubleshooting Guide

## ✅ Current Status
All systems are operational! The application has been debugged and optimized.

## 🚀 Quick Start

### Using the Start Script (Recommended)
```bash
./start_app.sh
```

### Manual Start
```bash
streamlit run Home.py
```

### With uv (Package Manager)
```bash
uv run streamlit run Home.py
```

## 📊 System Health Check

Run the diagnostic script to check all services:
```bash
python diagnose_issues.py
```

Expected output:
- ✅ All 11 services available
- ✅ All pages loading correctly
- ✅ All dependencies installed

## 🔧 Fixed Issues

### 1. ✅ Service Configuration
**Problem**: Services were failing due to missing secrets configuration
**Solution**: Created `.streamlit/secrets.toml` with default configurations

### 2. ✅ Missing Analytics Module
**Problem**: Analytics page was failing due to missing module
**Solution**: Created `streamlit_app/analytics_module.py`

### 3. ✅ Dependencies
**Problem**: Some dependencies were not properly installed
**Solution**: All dependencies are now installed via uv

## 📝 Configuration Files

### Essential Files
1. `.env` - Environment variables ✅
2. `.streamlit/secrets.toml` - Service secrets ✅
3. `.streamlit/config.toml` - Streamlit configuration ✅
4. `requirements.txt` - Python dependencies ✅

## 🌐 Service Status

| Service | Status | Purpose |
|---------|--------|---------|
| Database | ✅ Available | Data persistence |
| Supabase | ✅ Available | Cloud database |
| Storage | ✅ Available | File storage |
| MinIO | ✅ Available | Object storage |
| AI | ✅ Available | AI features |
| Cloud AI | ✅ Available | Cloud AI services |
| Cache | ✅ Available | Performance caching |
| Redis | ✅ Available | Redis caching |
| Auth | ✅ Available | User authentication |
| Audio | ✅ Available | Audio processing |
| Memory | ✅ Available | Memory management |

## 🎯 Performance Optimizations

### Applied Optimizations:
1. **Caching**: Enabled for all data operations
2. **File Watching**: Disabled for production
3. **Message Size**: Optimized for performance
4. **WebSocket Compression**: Enabled
5. **Fast Reruns**: Enabled
6. **Memory Management**: Active monitoring

## 🐛 Common Issues & Solutions

### Issue: Services showing as unavailable
**Solution**: Check `.streamlit/secrets.toml` exists and has proper configuration

### Issue: Page not loading
**Solution**: Run `python diagnose_issues.py` to identify the specific error

### Issue: Slow performance
**Solution**: Use the optimized startup script: `./start_app.sh`

### Issue: Import errors
**Solution**: Ensure all dependencies are installed: `uv pip install -r requirements.txt`

## 📱 Accessing the Application

After starting the app:
1. Open browser to: http://localhost:8501
2. All pages should be accessible from the sidebar
3. Features work without errors

## 🎉 Features Working

✅ Home page with navigation
✅ Text Stories creation and viewing
✅ Discovery of cultural content
✅ Analytics dashboard with visualizations
✅ Community features
✅ User profiles and dashboards
✅ Admin panels
✅ GitLab OAuth integration
✅ About page
✅ All navigation between pages

## 📞 Support

If you encounter any issues:
1. Run `python diagnose_issues.py` first
2. Check this troubleshooting guide
3. Ensure all configuration files exist
4. Restart the application using `./start_app.sh`

## 🎊 Success!

The website is now fully functional with:
- No import errors
- All services operational
- All pages accessible
- Optimized performance
- Proper error handling

Enjoy using BharatVerse! 🏛️
