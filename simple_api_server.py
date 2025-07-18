#!/usr/bin/env python3
"""
Simple API Server for BharatVerse Testing
This server provides mock API endpoints without requiring database setup
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from datetime import datetime, timedelta
import random
from typing import Dict, Any, List

# Initialize FastAPI app
app = FastAPI(
    title="BharatVerse Simple API",
    description="Simple API server for testing without database dependencies",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data storage
MOCK_CONTENT = []
MOCK_USERS = []

# Initialize some sample data
def initialize_sample_data():
    """Initialize some sample data for testing"""
    global MOCK_CONTENT, MOCK_USERS
    
    # Sample content
    MOCK_CONTENT = [
        {
            "id": "1",
            "title": "Traditional Bharatanatyam Dance",
            "content_type": "video",
            "language": "Tamil",
            "region": "South India",
            "created_at": datetime.now() - timedelta(hours=2),
            "user_id": "user1"
        },
        {
            "id": "2",
            "title": "Bengali Folk Song - Baul Tradition",
            "content_type": "audio",
            "language": "Bengali",
            "region": "East India",
            "created_at": datetime.now() - timedelta(hours=5),
            "user_id": "user2"
        },
        {
            "id": "3",
            "title": "Traditional Pongal Recipe",
            "content_type": "text",
            "language": "Tamil",
            "region": "South India",
            "created_at": datetime.now() - timedelta(days=1),
            "user_id": "user3"
        },
        {
            "id": "4",
            "title": "Rajasthani Miniature Painting",
            "content_type": "image",
            "language": "Hindi",
            "region": "North India",
            "created_at": datetime.now() - timedelta(days=2),
            "user_id": "user1"
        }
    ]
    
    # Sample users
    MOCK_USERS = [
        {"id": "user1", "name": "Priya Sharma", "contributions": 15},
        {"id": "user2", "name": "Rajesh Kumar", "contributions": 12},
        {"id": "user3", "name": "Meera Nair", "contributions": 8},
        {"id": "user4", "name": "Arjun Singh", "contributions": 6},
    ]

# Initialize data on startup
initialize_sample_data()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Simple API server is running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/stats")
async def get_statistics():
    """Get platform statistics"""
    content_by_type = {}
    language_dist = {}
    
    for content in MOCK_CONTENT:
        # Count by content type
        content_type = content["content_type"]
        content_by_type[content_type] = content_by_type.get(content_type, 0) + 1
        
        # Count by language
        language = content["language"]
        language_dist[language] = language_dist.get(language, 0) + 1
    
    return {
        "success": True,
        "stats": {
            "total_content": len(MOCK_CONTENT),
            "content_by_type": content_by_type,
            "language_distribution": language_dist,
            "uploads_today": len([c for c in MOCK_CONTENT if c["created_at"].date() == datetime.now().date()])
        }
    }

@app.get("/api/v1/content/recent")
async def get_recent_content(limit: int = 10):
    """Get recent content contributions"""
    # Sort by created_at descending
    sorted_content = sorted(MOCK_CONTENT, key=lambda x: x["created_at"], reverse=True)
    
    recent_content = []
    for content in sorted_content[:limit]:
        # Map content type to emoji
        type_emoji = {
            "audio": "🎙️",
            "text": "📝",
            "image": "📷",
            "video": "🎥"
        }.get(content["content_type"], "📄")
        
        # Calculate time ago
        now = datetime.now()
        time_diff = now - content["created_at"]
        
        if time_diff.days > 0:
            time_ago = f"{time_diff.days} days ago"
        elif time_diff.seconds > 3600:
            time_ago = f"{time_diff.seconds // 3600} hours ago"
        else:
            time_ago = f"{time_diff.seconds // 60} minutes ago"
        
        recent_content.append({
            "id": content["id"],
            "type": type_emoji,
            "title": content["title"],
            "lang": content["language"],
            "time": time_ago,
            "created_at": content["created_at"].isoformat()
        })
    
    return {
        "success": True,
        "results": recent_content
    }

@app.get("/api/v1/community/stats")
async def get_community_stats():
    """Get community statistics"""
    total_contributors = len(MOCK_USERS)
    active_contributors = max(1, total_contributors // 2)  # Simulate active users
    
    return {
        "success": True,
        "stats": {
            "total_contributors": total_contributors,
            "active_contributors": active_contributors,
            "total_members": total_contributors + random.randint(10, 50),
            "experts": max(1, total_contributors // 3),
            "verified_contributors": max(1, total_contributors // 2),
            "projects": random.randint(3, 8)
        }
    }

@app.get("/api/v1/community/leaderboard")
async def get_leaderboard(limit: int = 10):
    """Get community leaderboard"""
    # Sort users by contributions
    sorted_users = sorted(MOCK_USERS, key=lambda x: x["contributions"], reverse=True)
    
    leaderboard = []
    for i, user in enumerate(sorted_users[:limit], 1):
        leaderboard.append({
            "rank": i,
            "user_id": user["id"],
            "name": user["name"],
            "contributions": user["contributions"],
            "points": user["contributions"] * 10
        })
    
    return {
        "success": True,
        "leaderboard": leaderboard
    }

@app.get("/api/v1/content/{content_id}")
async def get_content(content_id: str):
    """Get content by ID"""
    for content in MOCK_CONTENT:
        if content["id"] == content_id:
            return {
                "success": True,
                "content": content
            }
    
    raise HTTPException(status_code=404, detail="Content not found")

@app.post("/api/v1/search")
async def search_content(request: Dict[str, Any]):
    """Search content"""
    query = request.get("query", "").lower()
    content_type = request.get("content_type")
    language = request.get("language")
    region = request.get("region")
    
    results = []
    for content in MOCK_CONTENT:
        # Simple text search
        if query in content["title"].lower():
            # Apply filters
            if content_type and content["content_type"] != content_type:
                continue
            if language and content["language"] != language:
                continue
            if region and content["region"] != region:
                continue
            
            results.append(content)
    
    return {
        "success": True,
        "count": len(results),
        "results": results
    }

@app.get("/api/v1/analytics/extended")
async def get_extended_analytics():
    """Get extended analytics data"""
    regions = {}
    for content in MOCK_CONTENT:
        region = content["region"]
        regions[region] = regions.get(region, 0) + 1
    
    # Generate sample daily stats for last 7 days
    daily_stats = []
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        daily_stats.append({
            "date": date.strftime("%Y-%m-%d"),
            "count": random.randint(1, 5)
        })
    
    return {
        "success": True,
        "analytics": {
            "regions": regions,
            "daily_stats": daily_stats,
            "quality_metrics": {
                "has_description": 85.5,
                "has_tags": 72.3,
                "has_language": 95.2
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Simple BharatVerse API Server...")
    print("📡 API will be available at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("💡 This is a simplified server for testing without database dependencies")
    uvicorn.run(app, host="0.0.0.0", port=8000)
