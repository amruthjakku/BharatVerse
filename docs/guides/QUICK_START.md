# 🚀 Quick Start - Real Data Integration Testing

## Overview
This is a simplified setup to test the real data integration without requiring database setup.

## ⚡ Quick Start

### 1. Start the System
```bash
cd /Users/jakkuamruth/Downloads/bharatverse
python start_test.py
```

### 2. Test the Integration
1. Open your browser to: http://localhost:8501
2. In the left sidebar, toggle **"Use Real Data"** to **ON**
3. You should see real data from the API instead of mock data

### 3. Verify Real Data is Working
When "Use Real Data" is enabled, you should see:
- **Home Page**: Real recent contributions from the API
- **Community Page**: Real community statistics and leaderboard
- **Analytics Page**: Real analytics data
- **Error messages**: If API is down, you'll see connection errors

## 🔍 What's Different?

### Demo Mode (Toggle OFF) 🟡
- Shows rich mock data
- No API calls made
- Perfect for demonstrations

### Real Data Mode (Toggle ON) 🟢
- Fetches data from API at http://localhost:8000
- Shows actual API responses
- Displays "N/A" or "0" when no real data exists

## 🧪 Testing Scenarios

### Test 1: Basic Integration
1. Start with "Use Real Data" OFF
2. Navigate to different pages - should see mock data
3. Toggle "Use Real Data" ON
4. Same pages should now show real data from API

### Test 2: API Connection
1. Enable "Use Real Data"
2. Stop the API server: `pkill -f simple_api_server.py`
3. Refresh pages - should see connection error messages
4. Restart API server: `python simple_api_server.py &`

### Test 3: Data Comparison
1. Compare the Recent Contributions section:
   - **Mock**: Shows hardcoded "Baul Song", "Pongal Recipe", etc.
   - **Real**: Shows "Traditional Bharatanatyam Dance", "Bengali Folk Song", etc.

## 📊 API Endpoints Available

The simple API server provides these endpoints:
- `GET /health` - Health check
- `GET /api/v1/stats` - Platform statistics
- `GET /api/v1/content/recent` - Recent contributions
- `GET /api/v1/community/stats` - Community statistics
- `GET /api/v1/community/leaderboard` - Community leaderboard

## 🛠️ Manual Testing

You can also test the API directly:

```bash
# Test API health
curl http://localhost:8000/health

# Test statistics
curl http://localhost:8000/api/v1/stats | python -m json.tool

# Test recent content
curl http://localhost:8000/api/v1/content/recent | python -m json.tool

# Test community stats
curl http://localhost:8000/api/v1/community/stats | python -m json.tool
```

## 🔧 Troubleshooting

### API Server Not Starting
- Check if port 8000 is available: `lsof -i :8000`
- Kill existing processes: `pkill -f simple_api_server.py`
- Restart: `python simple_api_server.py &`

### Streamlit Not Connecting to API
- Verify API is running: `curl http://localhost:8000/health`
- Check browser console for network errors
- Ensure both services are on the same network

### Still Seeing Mock Data
- Verify the toggle is ON (should show "🟢 Using Real Data")
- Check browser console for API errors
- Refresh the page after toggling

## 🎯 Success Criteria

✅ **Working Real Data Integration**:
- Toggle switches data sources instantly
- Recent contributions show different content in real vs mock mode
- Community stats change when switching modes
- Error messages appear when API is unavailable

## 🚀 Next Steps

Once you've verified the integration works:
1. Set up the full database system (PostgreSQL, Redis, MinIO)
2. Switch to using `core/api_service.py` for the full API
3. Upload real content through the Streamlit interface
4. Monitor real analytics and community data

## 📝 Notes

- This is a simplified setup for testing only
- The simple API server uses in-memory data
- For production, use the full database-backed API
- All data resets when the API server restarts
