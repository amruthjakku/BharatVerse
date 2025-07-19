#!/bin/bash
# Run BharatVerse in demo mode (without database services)

echo "🚀 Starting BharatVerse in Demo Mode..."
echo "ℹ️  This mode runs without database services (PostgreSQL, MinIO, Redis)"
echo ""

# Set environment variable to disable database
export DISABLE_DATABASE=true

# Run the application
streamlit run Home.py

echo "✅ BharatVerse demo stopped"
