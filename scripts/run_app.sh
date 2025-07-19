#!/bin/bash

# BharatVerse - Startup Script
# This script helps you run the BharatVerse application with the new multipage structure

echo "🇮🇳 BharatVerse - Digital Cultural Heritage Platform"
echo "=================================================="
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit is not installed. Installing now..."
    pip install streamlit
    echo "✅ Streamlit installed successfully!"
    echo ""
fi

# Check if we're in the right directory
if [ ! -f "Home.py" ]; then
    echo "❌ Error: Home.py not found. Please run this script from the bharatverse root directory."
    exit 1
fi

echo "🚀 Starting BharatVerse with multipage structure..."
echo "📁 Main page: Home.py"
echo "📂 Additional pages: pages/ directory"
echo ""
echo "🌐 The application will open in your default browser"
echo "🔗 URL: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

# Run the application
streamlit run Home.py