#!/bin/bash

# BharatVerse Enhanced System Startup Script
echo "🚀 Starting BharatVerse Enhanced System..."

# Navigate to project directory
cd /Users/jakkuamruth/Downloads/bharatverse

# Start database services
echo "📊 Starting database services..."
docker compose -f docker-compose-db.yml up -d

# Wait for databases to be ready
echo "⏳ Waiting for databases to initialize..."
sleep 10

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=bharatverse
export POSTGRES_USER=bharatverse_user
export POSTGRES_PASSWORD=secretpassword
export REDIS_HOST=localhost
export REDIS_PORT=6379
export MINIO_HOST=localhost:9000
export MINIO_ACCESS_KEY=minioadmin
export MINIO_SECRET_KEY=minioadmin
export MINIO_SECURE=False
export API_URL=http://localhost:8000

# Start API server in background
echo "🔧 Starting Enhanced API Server..."
uvicorn api.enhanced_main:app --host 0.0.0.0 --port 8000 --reload &

# Wait for API to start
sleep 5

# Start Streamlit app
echo "🎨 Starting Streamlit Application..."
POSTGRES_HOST=localhost POSTGRES_PORT=5432 POSTGRES_DB=bharatverse POSTGRES_USER=bharatverse_user POSTGRES_PASSWORD=secretpassword REDIS_HOST=localhost REDIS_PORT=6379 MINIO_HOST=localhost:9000 MINIO_ACCESS_KEY=minioadmin MINIO_SECRET_KEY=minioadmin MINIO_SECURE=False API_URL=http://localhost:8000 streamlit run streamlit_app/app.py --server.port=8501 --server.address=0.0.0.0

echo "✅ System started successfully!"
echo "🌐 Access the app at: http://localhost:8501"