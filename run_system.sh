#!/bin/bash

# BharatVerse Enhanced System Startup Script
echo "🤝 BharatVerse Enhanced System Startup"
echo "=================================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check database connectivity
check_database() {
    echo "🔍 Checking database connection..."
    if command_exists pg_isready; then
        pg_isready -h "${POSTGRES_HOST:-localhost}" -p "${POSTGRES_PORT:-5432}" -U "${POSTGRES_USER:-bharatverse_user}" >/dev/null 2>&1
        return $?
    else
        # Fallback to Python check if pg_isready is not available
        python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='${POSTGRES_HOST:-localhost}',
        port='${POSTGRES_PORT:-5432}',
        database='${POSTGRES_DB:-bharatverse}',
        user='${POSTGRES_USER:-bharatverse_user}',
        password='${POSTGRES_PASSWORD:-secretpassword}'
    )
    conn.close()
    exit(0)
except:
    exit(1)
" 2>/dev/null
        return $?
    fi
}

# Load environment configuration
if [ -f .env.local ]; then
    echo "📝 Loading .env.local configuration..."
    set -o allexport
    source .env.local
    set +o allexport
    echo "✅ Local environment loaded"
elif [ -f .env ]; then
    echo "📝 Loading .env configuration..."
    set -o allexport
    source .env
    set +o allexport
    echo "✅ Environment loaded"
else
    echo "⚠️  No environment file found, using defaults"
    # Set default values
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
fi

# Check if we should skip database (for UI-only development)
if [ "$DISABLE_DATABASE" = "true" ]; then
    echo "⚠️  Database disabled - running in UI-only mode"
else
    # Start database services if not running
    echo "\n📊 Checking database services..."
    if ! check_database; then
        echo "🚀 Starting database services..."
        docker compose -f docker-compose-db.yml up -d
        
        # Wait for databases to be ready
        echo "⏳ Waiting for databases to initialize..."
        for i in {1..30}; do
            if check_database; then
                echo "✅ Database is ready!"
                break
            fi
            echo -n "."
            sleep 1
        done
        echo ""
        
        if ! check_database; then
            echo "❌ Database failed to start"
            echo "💡 Try running manually: docker compose -f docker-compose-db.yml up -d"
            exit 1
        fi
    else
        echo "✅ Database is already running"
    fi
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "\n🐍 Activating virtual environment..."
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "⚠️  No virtual environment found"
fi

# Display configuration
echo "\n📋 Current Configuration:"
echo "--------------------------------------------------"
echo "  POSTGRES_HOST: ${POSTGRES_HOST:-localhost}"
echo "  POSTGRES_PORT: ${POSTGRES_PORT:-5432}"
echo "  POSTGRES_DB: ${POSTGRES_DB:-bharatverse}"
echo "  REDIS_HOST: ${REDIS_HOST:-localhost}"
echo "  REDIS_PORT: ${REDIS_PORT:-6379}"
echo "  MINIO_HOST: ${MINIO_HOST:-localhost:9000}"
echo "  API_URL: ${API_URL:-http://localhost:8000}"
echo "--------------------------------------------------"

# Check if API server is needed
if [ -f "api/enhanced_main.py" ] && [ "$DISABLE_API" != "true" ]; then
    echo "\n🔧 Starting Enhanced API Server..."
    uvicorn api.enhanced_main:app --host 0.0.0.0 --port 8000 --reload &
    API_PID=$!
    
    # Wait for API to start
    echo "⏳ Waiting for API server..."
    sleep 5
fi

# Start Streamlit app
echo "\n🎨 Starting Streamlit Application..."
echo "📱 The application will be available at: http://localhost:8501"
echo "🤝 Navigate to the Community page to explore features!"
echo "\nPress Ctrl+C to stop the application"
echo "=================================================="

# Trap to handle cleanup on exit
trap 'echo "\n👋 Shutting down..."; [ ! -z "$API_PID" ] && kill $API_PID 2>/dev/null; exit' INT TERM

# Start Streamlit with the correct main file
if [ -f "Home.py" ]; then
    streamlit run Home.py --server.port=8501 --server.address=0.0.0.0
else
    streamlit run streamlit_app/app.py --server.port=8501 --server.address=0.0.0.0
fi
