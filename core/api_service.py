"""
FastAPI service for BharatVerse
Integrates database operations with AI models
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import io
import uuid
import tempfile
import logging
from datetime import datetime

# Import our core modules
from core.database import db_manager, content_repo
from core.ai_models import ai_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="BharatVerse API",
    description="API for cultural content preservation with AI processing",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:8501").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class AudioTranscriptionRequest(BaseModel):
    language: Optional[str] = None
    translate: bool = False


class TextAnalysisRequest(BaseModel):
    text: str
    language: str = "auto"
    translate: bool = False


class ContentMetadata(BaseModel):
    title: str
    description: Optional[str] = None
    language: Optional[str] = None
    region: Optional[str] = None
    tags: Optional[List[str]] = []
    user_id: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    content_type: Optional[str] = None
    language: Optional[str] = None
    region: Optional[str] = None


# Health check
@app.get("/health")
async def health_check():
    """Check if all services are running"""
    status = {
        "api": "healthy",
        "database": "unknown",
        "minio": "unknown",
        "redis": "unknown",
        "ai_models": {
            "whisper": "not_loaded",
            "text_processor": "not_loaded",
            "image_captioner": "not_loaded"
        }
    }
    
    # Check database connections
    try:
        conn = db_manager.get_postgres_connection()
        db_manager.release_postgres_connection(conn)
        status["database"] = "healthy"
    except:
        status["database"] = "error"
    
    try:
        db_manager.redis.ping()
        status["redis"] = "healthy"
    except:
        status["redis"] = "error"
    
    try:
        db_manager.minio.list_buckets()
        status["minio"] = "healthy"
    except:
        status["minio"] = "error"
    
    # Check AI models
    if ai_manager.whisper_model:
        status["ai_models"]["whisper"] = "loaded"
    if ai_manager.text_processor:
        status["ai_models"]["text_processor"] = "loaded"
    if ai_manager.image_captioner:
        status["ai_models"]["image_captioner"] = "loaded"
    
    return status


# Audio endpoints
@app.post("/api/v1/audio/upload")
async def upload_audio(
    file: UploadFile = File(...),
    metadata: str = Form(...),  # JSON string
):
    """Upload and process audio file"""
    try:
        # Parse metadata
        import json
        meta = json.loads(metadata)
        
        # Validate file type
        allowed_formats = os.getenv("ALLOWED_AUDIO_FORMATS", "mp3,wav,ogg,m4a,flac").split(",")
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in allowed_formats:
            raise HTTPException(400, f"File format {file_extension} not allowed")
        
        # Read file data
        file_data = await file.read()
        
        # Save to temporary file for processing
        with tempfile.NamedTemporaryFile(suffix=f".{file_extension}", delete=False) as tmp_file:
            tmp_file.write(file_data)
            tmp_path = tmp_file.name
        
        # Process with AI models
        ai_results = {}
        
        # Transcribe audio
        if ai_manager.whisper_model:
            transcription = ai_manager.transcribe_audio(tmp_path, meta.get("language"))
            ai_results["transcription"] = transcription.get("text", "")
            ai_results["detected_language"] = transcription.get("language", "unknown")
            ai_results["duration"] = transcription.get("duration", 0)
            
            # Translate if requested
            if meta.get("translate", False):
                translation = ai_manager.translate_audio(tmp_path)
                ai_results["translation"] = translation.get("text", "")
        
        # Analyze transcribed text
        if ai_results.get("transcription") and ai_manager.text_processor:
            text_analysis = ai_manager.analyze_text(
                ai_results["transcription"],
                ai_results.get("detected_language", "auto")
            )
            ai_results["text_analysis"] = text_analysis
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        # Prepare metadata for storage
        content_metadata = {
            "title": meta.get("title", f"Audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            "description": meta.get("description"),
            "language": ai_results.get("detected_language", meta.get("language")),
            "region": meta.get("region"),
            "tags": meta.get("tags", []),
            "file_extension": file_extension,
            "transcription": ai_results.get("transcription"),
            "translation": ai_results.get("translation"),
            "duration_seconds": int(ai_results.get("duration", 0)),
            "ai_analysis": ai_results.get("text_analysis", {}),
            "user_id": meta.get("user_id")
        }
        
        # Save to database
        result = content_repo.save_content("audio", file_data, content_metadata)
        
        return {
            "success": True,
            "content_id": result["id"],
            "metadata": result,
            "ai_results": ai_results
        }
        
    except Exception as e:
        logger.error(f"Audio upload failed: {e}")
        raise HTTPException(500, str(e))


@app.post("/api/v1/audio/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: Optional[str] = Form(None),
    translate: bool = Form(False)
):
    """Transcribe audio file without saving"""
    try:
        # Save to temporary file
        file_data = await file.read()
        file_extension = file.filename.split(".")[-1].lower()
        
        with tempfile.NamedTemporaryFile(suffix=f".{file_extension}", delete=False) as tmp_file:
            tmp_file.write(file_data)
            tmp_path = tmp_file.name
        
        # Transcribe
        result = {"success": True}
        
        if ai_manager.whisper_model:
            transcription = ai_manager.transcribe_audio(tmp_path, language)
            result["transcription"] = transcription.get("text", "")
            result["language"] = transcription.get("language", "unknown")
            result["duration"] = transcription.get("duration", 0)
            
            if translate:
                translation = ai_manager.translate_audio(tmp_path)
                result["translation"] = translation.get("text", "")
        else:
            result["error"] = "Whisper model not available"
        
        # Clean up
        os.unlink(tmp_path)
        
        return result
        
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(500, str(e))


# Text endpoints
@app.post("/api/v1/text/analyze")
async def analyze_text(request: TextAnalysisRequest):
    """Analyze text content"""
    try:
        result = {"success": True}
        
        if ai_manager.text_processor:
            # Analyze text
            analysis = ai_manager.analyze_text(request.text, request.language)
            result["analysis"] = analysis
            
            # Translate if requested
            if request.translate:
                translation = ai_manager.translate_text(request.text)
                result["translation"] = translation
        else:
            result["error"] = "Text processor not available"
        
        return result
        
    except Exception as e:
        logger.error(f"Text analysis failed: {e}")
        raise HTTPException(500, str(e))


@app.post("/api/v1/text/upload")
async def upload_text(
    content: str = Form(...),
    metadata: str = Form(...)  # JSON string
):
    """Upload and process text content"""
    try:
        import json
        meta = json.loads(metadata)
        
        # Analyze text
        ai_results = {}
        if ai_manager.text_processor:
            analysis = ai_manager.analyze_text(content, meta.get("language", "auto"))
            ai_results["analysis"] = analysis
            
            if meta.get("translate", False):
                translation = ai_manager.translate_text(content)
                ai_results["translation"] = translation
        
        # Prepare metadata
        content_metadata = {
            "title": meta.get("title", f"Text_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            "description": meta.get("description"),
            "language": ai_results.get("analysis", {}).get("language", meta.get("language")),
            "region": meta.get("region"),
            "tags": meta.get("tags", []),
            "transcription": content,  # Store original text as transcription
            "translation": ai_results.get("translation"),
            "ai_analysis": ai_results.get("analysis", {}),
            "user_id": meta.get("user_id")
        }
        
        # Save to database (no file data for text)
        result = content_repo.save_content("text", None, content_metadata)
        
        return {
            "success": True,
            "content_id": result["id"],
            "metadata": result,
            "ai_results": ai_results
        }
        
    except Exception as e:
        logger.error(f"Text upload failed: {e}")
        raise HTTPException(500, str(e))


# Image endpoints
@app.post("/api/v1/image/upload")
async def upload_image(
    file: UploadFile = File(...),
    metadata: str = Form(...)  # JSON string
):
    """Upload and process image"""
    try:
        import json
        meta = json.loads(metadata)
        
        # Validate file type
        allowed_formats = os.getenv("ALLOWED_IMAGE_FORMATS", "jpg,jpeg,png,gif,webp,bmp").split(",")
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in allowed_formats:
            raise HTTPException(400, f"File format {file_extension} not allowed")
        
        # Read file data
        file_data = await file.read()
        
        # Save to temporary file for processing
        with tempfile.NamedTemporaryFile(suffix=f".{file_extension}", delete=False) as tmp_file:
            tmp_file.write(file_data)
            tmp_path = tmp_file.name
        
        # Process with AI
        ai_results = {}
        
        if ai_manager.image_captioner:
            caption_result = ai_manager.caption_image(tmp_path)
            ai_results["caption"] = caption_result.get("caption", "")
            ai_results["image_analysis"] = caption_result.get("image_analysis", {})
            ai_results["cultural_elements"] = caption_result.get("cultural_elements", [])
        
        # Clean up
        os.unlink(tmp_path)
        
        # Prepare metadata
        content_metadata = {
            "title": meta.get("title", f"Image_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            "description": meta.get("description", ai_results.get("caption", "")),
            "language": meta.get("language"),
            "region": meta.get("region"),
            "tags": meta.get("tags", []) + ai_results.get("cultural_elements", []),
            "file_extension": file_extension,
            "ai_analysis": ai_results,
            "user_id": meta.get("user_id")
        }
        
        # Save to database
        result = content_repo.save_content("image", file_data, content_metadata)
        
        return {
            "success": True,
            "content_id": result["id"],
            "metadata": result,
            "ai_results": ai_results
        }
        
    except Exception as e:
        logger.error(f"Image upload failed: {e}")
        raise HTTPException(500, str(e))


@app.post("/api/v1/image/caption")
async def caption_image(file: UploadFile = File(...)):
    """Generate caption for image without saving"""
    try:
        # Save to temporary file
        file_data = await file.read()
        file_extension = file.filename.split(".")[-1].lower()
        
        with tempfile.NamedTemporaryFile(suffix=f".{file_extension}", delete=False) as tmp_file:
            tmp_file.write(file_data)
            tmp_path = tmp_file.name
        
        # Generate caption
        result = {"success": True}
        
        if ai_manager.image_captioner:
            caption_result = ai_manager.caption_image(tmp_path)
            result.update(caption_result)
        else:
            result["error"] = "Image captioner not available"
        
        # Clean up
        os.unlink(tmp_path)
        
        return result
        
    except Exception as e:
        logger.error(f"Image captioning failed: {e}")
        raise HTTPException(500, str(e))


# Search and retrieval
@app.post("/api/v1/search")
async def search_content(request: SearchRequest):
    """Search content across all types"""
    try:
        filters = {}
        if request.content_type:
            filters["content_type"] = request.content_type
        if request.language:
            filters["language"] = request.language
        if request.region:
            filters["region"] = request.region
        
        results = content_repo.search_content(request.query, filters)
        
        return {
            "success": True,
            "count": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(500, str(e))


@app.get("/api/v1/content/{content_id}")
async def get_content(content_id: str):
    """Get content by ID"""
    try:
        content = content_repo.get_content(content_id)
        if not content:
            raise HTTPException(404, "Content not found")
        
        return {
            "success": True,
            "content": content
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Content retrieval failed: {e}")
        raise HTTPException(500, str(e))


# Statistics
@app.get("/api/v1/stats")
async def get_statistics():
    """Get platform statistics"""
    try:
        conn = db_manager.get_postgres_connection()
        try:
            with conn.cursor() as cursor:
                # Get content counts
                cursor.execute("""
                    SELECT content_type, COUNT(*) as count
                    FROM content_metadata
                    GROUP BY content_type
                """)
                content_counts = dict(cursor.fetchall())
                
                # Get language distribution
                cursor.execute("""
                    SELECT language, COUNT(*) as count
                    FROM content_metadata
                    WHERE language IS NOT NULL
                    GROUP BY language
                    ORDER BY count DESC
                    LIMIT 10
                """)
                language_dist = dict(cursor.fetchall())
                
                # Get recent activity
                cursor.execute("""
                    SELECT COUNT(*) as today_count
                    FROM content_metadata
                    WHERE created_at >= CURRENT_DATE
                """)
                today_count = cursor.fetchone()[0]
                
                return {
                    "success": True,
                    "stats": {
                        "total_content": sum(content_counts.values()),
                        "content_by_type": content_counts,
                        "language_distribution": language_dist,
                        "uploads_today": today_count
                    }
                }
                
        finally:
            db_manager.release_postgres_connection(conn)
            
    except Exception as e:
        logger.error(f"Statistics retrieval failed: {e}")
        raise HTTPException(500, str(e))


# Community endpoints
@app.get("/api/v1/community/stats")
async def get_community_stats():
    """Get community statistics"""
    try:
        conn = db_manager.get_postgres_connection()
        try:
            with conn.cursor() as cursor:
                # Get total unique contributors
                cursor.execute("""
                    SELECT COUNT(DISTINCT user_id) as contributors
                    FROM content_metadata
                    WHERE user_id IS NOT NULL
                """)
                contributors = cursor.fetchone()[0] or 0
                
                # Get active contributors (last 30 days)
                cursor.execute("""
                    SELECT COUNT(DISTINCT user_id) as active_contributors
                    FROM content_metadata
                    WHERE user_id IS NOT NULL 
                    AND created_at >= NOW() - INTERVAL '30 days'
                """)
                active_contributors = cursor.fetchone()[0] or 0
                
                return {
                    "success": True,
                    "stats": {
                        "total_contributors": contributors,
                        "active_contributors": active_contributors,
                        "total_members": contributors,  # For now, same as contributors
                        "experts": max(1, contributors // 10),  # Estimate
                        "verified_contributors": max(1, contributors // 5),  # Estimate
                        "projects": 0  # Not implemented yet
                    }
                }
        finally:
            db_manager.release_postgres_connection(conn)
    except Exception as e:
        logger.error(f"Community stats failed: {e}")
        raise HTTPException(500, str(e))


@app.get("/api/v1/community/leaderboard")
async def get_leaderboard(limit: int = 10):
    """Get community leaderboard"""
    try:
        conn = db_manager.get_postgres_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        user_id,
                        COUNT(*) as contributions,
                        COUNT(*) * 10 as points
                    FROM content_metadata
                    WHERE user_id IS NOT NULL
                    GROUP BY user_id
                    ORDER BY contributions DESC
                    LIMIT %s
                """, (limit,))
                
                leaderboard = []
                for i, (user_id, contributions, points) in enumerate(cursor.fetchall(), 1):
                    leaderboard.append({
                        "rank": i,
                        "user_id": user_id,
                        "name": f"User {str(user_id)[:8]}",  # Simplified name
                        "contributions": contributions,
                        "points": points
                    })
                
                return {
                    "success": True,
                    "leaderboard": leaderboard
                }
        finally:
            db_manager.release_postgres_connection(conn)
    except Exception as e:
        logger.error(f"Leaderboard failed: {e}")
        raise HTTPException(500, str(e))


@app.get("/api/v1/content/recent")
async def get_recent_content(limit: int = 10):
    """Get recent content contributions"""
    try:
        conn = db_manager.get_postgres_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        id,
                        title,
                        content_type,
                        language,
                        created_at
                    FROM content_metadata
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (limit,))
                
                recent_content = []
                for row in cursor.fetchall():
                    content_id, title, content_type, language, created_at = row
                    
                    # Map content type to emoji
                    type_emoji = {
                        "audio": "🎙️",
                        "text": "📝",
                        "image": "📷",
                        "video": "🎥"
                    }.get(content_type, "📄")
                    
                    # Calculate time ago
                    import datetime
                    now = datetime.datetime.now()
                    if created_at.tzinfo is None:
                        created_at = created_at.replace(tzinfo=datetime.timezone.utc)
                    if now.tzinfo is None:
                        now = now.replace(tzinfo=datetime.timezone.utc)
                    
                    time_diff = now - created_at
                    if time_diff.days > 0:
                        time_ago = f"{time_diff.days} days ago"
                    elif time_diff.seconds > 3600:
                        time_ago = f"{time_diff.seconds // 3600} hours ago"
                    else:
                        time_ago = f"{time_diff.seconds // 60} minutes ago"
                    
                    recent_content.append({
                        "id": str(content_id),
                        "type": type_emoji,
                        "title": title,
                        "lang": language or "Unknown",
                        "time": time_ago,
                        "created_at": created_at.isoformat()
                    })
                
                return {
                    "success": True,
                    "results": recent_content
                }
        finally:
            db_manager.release_postgres_connection(conn)
    except Exception as e:
        logger.error(f"Recent content failed: {e}")
        raise HTTPException(500, str(e))


@app.get("/api/v1/analytics/extended")
async def get_extended_analytics():
    """Get extended analytics data"""
    try:
        conn = db_manager.get_postgres_connection()
        try:
            with conn.cursor() as cursor:
                # Get content by region
                cursor.execute("""
                    SELECT region, COUNT(*) as count
                    FROM content_metadata
                    WHERE region IS NOT NULL
                    GROUP BY region
                    ORDER BY count DESC
                """)
                regions = dict(cursor.fetchall())
                
                # Get daily content creation for last 30 days
                cursor.execute("""
                    SELECT 
                        DATE(created_at) as date,
                        COUNT(*) as count
                    FROM content_metadata
                    WHERE created_at >= NOW() - INTERVAL '30 days'
                    GROUP BY DATE(created_at)
                    ORDER BY date
                """)
                daily_stats = cursor.fetchall()
                
                # Get content quality metrics (simplified)
                cursor.execute("""
                    SELECT 
                        AVG(CASE WHEN description IS NOT NULL THEN 1 ELSE 0 END) * 100 as has_description,
                        AVG(CASE WHEN array_length(tags, 1) > 0 THEN 1 ELSE 0 END) * 100 as has_tags,
                        AVG(CASE WHEN language IS NOT NULL THEN 1 ELSE 0 END) * 100 as has_language
                    FROM content_metadata
                """)
                quality_row = cursor.fetchone()
                
                return {
                    "success": True,
                    "analytics": {
                        "regions": regions,
                        "daily_stats": [{
                            "date": str(date),
                            "count": count
                        } for date, count in daily_stats],
                        "quality_metrics": {
                            "has_description": round(quality_row[0] or 0, 1),
                            "has_tags": round(quality_row[1] or 0, 1),
                            "has_language": round(quality_row[2] or 0, 1)
                        }
                    }
                }
        finally:
            db_manager.release_postgres_connection(conn)
    except Exception as e:
        logger.error(f"Extended analytics failed: {e}")
        raise HTTPException(500, str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
