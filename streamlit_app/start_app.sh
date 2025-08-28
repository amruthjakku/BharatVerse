#!/bin/bash

# BharatVerse Optimized Startup Script
# Ensures all services are ready and app runs smoothly

echo "🏛️ Starting BharatVerse..."
echo "=============================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Creating virtual environment with uv..."
    uv venv
fi

# Activate virtual environment (for display purposes)
echo "✅ Using uv-managed environment"

# Check dependencies
echo "📦 Checking dependencies..."
uv pip list > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    uv pip install -r requirements.txt
fi

# Check for secrets file
if [ ! -f ".streamlit/secrets.toml" ]; then
    echo "⚠️ Warning: secrets.toml not found!"
    echo "Some services may not be available."
fi

# Set environment variables for optimization
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=localhost
export STREAMLIT_SERVER_FILE_WATCHER_TYPE=none
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_THEME_BASE=light

# Memory optimization
export STREAMLIT_SERVER_MAX_MESSAGE_SIZE=200
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=100
export STREAMLIT_GLOBAL_DEVELOPMENT_MODE=false

# Clear any cache issues
echo "🧹 Clearing cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null

# Run diagnostics
echo ""
echo "🔍 Running quick diagnostics..."
python diagnose_issues.py 2>/dev/null | grep -E "Services:|OK|Available" | head -5

echo ""
echo "=============================="
echo "🚀 Launching BharatVerse..."
echo "=============================="
echo ""
echo "📌 Access the app at: http://localhost:8501"
echo "📌 Press Ctrl+C to stop the server"
echo ""

# Start the Streamlit app
streamlit run Home.py \
    --server.port 8501 \
    --server.address localhost \
    --server.fileWatcherType none \
    --browser.gatherUsageStats false \
    --theme.base light
