#!/bin/bash

# BharatVerse Enhanced System Stop Script
echo "🛑 Stopping BharatVerse Enhanced System..."

# Stop Streamlit
echo "Stopping Streamlit..."
pkill -f "streamlit run"

# Stop API server
echo "Stopping API server..."
pkill -f "uvicorn.*enhanced_main"

# Stop database services
echo "Stopping database services..."
cd /Users/jakkuamruth/Downloads/bharatverse
docker compose -f docker-compose-db.yml down

echo "✅ System stopped successfully!"