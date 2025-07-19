#!/bin/bash

# BharatVerse Environment Setup Script
# Sets up environment variables for immediate performance benefits

echo "🚀 Setting up BharatVerse Performance Environment"
echo "=================================================="

# Performance optimization environment variables
export ENABLE_CACHING=true
export CACHE_TTL_HOURS=24
export MEMORY_THRESHOLD_MB=500
export CLEANUP_INTERVAL_SECONDS=300
export MAX_CONCURRENT_REQUESTS=5

# Rate limiting and batching
export API_CALLS_PER_MINUTE=60
export BATCH_SIZE=10
export PARALLEL_PROCESSING_WORKERS=4

# Monitoring and analytics
export ENABLE_PERFORMANCE_MONITORING=true
export ENABLE_MEMORY_TRACKING=true
export LOG_LEVEL=INFO
export ANALYTICS_BATCH_SIZE=10

# Async operations
export ASYNC_TIMEOUT_SECONDS=30
export CONNECTION_POOL_SIZE=10
export WARMUP_SERVICES_ON_START=true

echo "✅ Performance environment variables set!"
echo ""
echo "🎯 IMMEDIATE BENEFITS ACTIVE:"
echo "   • Streamlit caching enabled"
echo "   • Memory monitoring active"
echo "   • Performance tracking enabled"
echo "   • Parallel processing optimized"
echo ""
echo "🚀 FOR FULL BENEFITS, ALSO SET:"
echo "   export REDIS_URL='redis://your-redis-instance'"
echo "   export POSTGRES_HOST='your-supabase-host'"
echo "   export POSTGRES_PASSWORD='your-password'"
echo ""
echo "📊 READY TO LAUNCH:"
echo "   streamlit run Home.py"
echo "=================================================="