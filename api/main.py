"""
Enhanced FastAPI server for BharatVerse with real AI integration
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import json
import os
import io
import uuid
import logging
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import enhanced AI models and database
try:
    from core.ai_models_enhanced import ai_manager
    AI_MODELS_AVAILABLE = True
except ImportError:
    AI_MODELS_AVAILABLE = False
    ai_manager = None

try:
    from core.database import DatabaseManager, ContentRepository
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="BharatVerse Enhanced API",
    description="Enhanced API for preserving and accessing India's cultural heritage with real AI",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database manager
db_manager = None
content_repo = None

if DATABASE_AVAILABLE:
    try:
        db_manager = DatabaseManager()
        content_repo = ContentRepository(db_manager)
        logger.info("Database connections initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        DATABASE_AVAILABLE = False

# Pydantic models
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    services: Dict[str, str]
    ai_models: Dict[str, bool]

class AudioTranscriptionRequest(BaseModel):
    language: Optional[str] = None
    translate: bool = False

class TextAnalysisRequest(BaseModel):
    text: str
    language: Optional[str] = None
    translate: bool = False

class SearchRequest(BaseModel):
    query: str
    content_types: Optional[List[str]] = []
    languages: Optional[List[str]] = []
    regions: Optional[List[str]] = []
    limit: int = 20
    offset: int = 0

class ContributionResponse(BaseModel):
    id: str
    title: str
    content_type: str
    language: str
    region: str
    created_at: str
    ai_analysis: Optional[Dict[str, Any]] = None

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to BharatVerse Enhanced API",
        "version": "2.0.0",
        "documentation": "/docs",
        "status": "active",
        "features": {
            "ai_models": AI_MODELS_AVAILABLE,
            "database": DATABASE_AVAILABLE,
            "real_time_processing": True
        }
    }

# Enhanced health check
@app.get("/health", response_model=HealthResponse)
async def health_check():
    services = {}
    
    # Check database connections
    if DATABASE_AVAILABLE and db_manager:
        try:
            # Test PostgreSQL
            conn = db_manager.get_postgres_connection()
            db_manager.release_postgres_connection(conn)
            services["postgresql"] = "healthy"
        except Exception:
            services["postgresql"] = "unhealthy"
        
        try:
            # Test Redis
            db_manager.redis.ping()
            services["redis"] = "healthy"
        except Exception:
            services["redis"] = "unhealthy"
        
        try:
            # Test MinIO
            db_manager.minio.list_buckets()
            services["minio"] = "healthy"
        except Exception:
            services["minio"] = "unhealthy"
    else:
        services["database"] = "unavailable"
    
    # Check AI models
    ai_models = {}
    if AI_MODELS_AVAILABLE and ai_manager:
        model_status = ai_manager.get_model_status()
        ai_models = model_status
    else:
        ai_models = {"status": "unavailable"}
    
    return HealthResponse(
        status="healthy" if services and all(v == "healthy" for v in services.values()) else "degraded",
        timestamp=datetime.now().isoformat(),
        version="2.0.0",
        services=services,
        ai_models=ai_models
    )

# Enhanced audio transcription endpoint
@app.post("/api/v1/audio/transcribe")
async def transcribe_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: Optional[str] = Form(None),
    translate: bool = Form(False)
):
    """Transcribe audio using real AI models"""
    
    if not AI_MODELS_AVAILABLE or not ai_manager:
        raise HTTPException(
            status_code=503, 
            detail="AI models not available. Please install required dependencies."
        )
    
    try:
        # Read audio file
        audio_data = await file.read()
        
        # Process with AI manager
        result = ai_manager.process_audio(
            audio_data,
            language=language,
            translate=translate
        )
        
        if result.get('success'):
            # Store in database if available
            if DATABASE_AVAILABLE and content_repo:
                background_tasks.add_task(
                    store_audio_contribution,
                    audio_data,
                    result,
                    file.filename
                )
            
            return JSONResponse(content=result)
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Transcription failed'))
            
    except Exception as e:
        logger.error(f"Audio transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced text analysis endpoint
@app.post("/api/v1/text/analyze")
async def analyze_text(
    request: TextAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Analyze text using real AI models"""
    
    if not AI_MODELS_AVAILABLE or not ai_manager:
        raise HTTPException(
            status_code=503,
            detail="AI models not available. Please install required dependencies."
        )
    
    try:
        # Process with AI manager
        result = ai_manager.process_text(
            request.text,
            language=request.language,
            translate=request.translate
        )
        
        if result.get('success'):
            # Store in database if available
            if DATABASE_AVAILABLE and content_repo:
                background_tasks.add_task(
                    store_text_contribution,
                    request.text,
                    result
                )
            
            return JSONResponse(content=result)
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Analysis failed'))
            
    except Exception as e:
        logger.error(f"Text analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced image analysis endpoint
@app.post("/api/v1/image/analyze")
async def analyze_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Analyze image using real AI models"""
    
    if not AI_MODELS_AVAILABLE or not ai_manager:
        raise HTTPException(
            status_code=503,
            detail="AI models not available. Please install required dependencies."
        )
    
    try:
        # Read image file
        image_data = await file.read()
        
        # Process with AI manager
        result = ai_manager.process_image(image_data)
        
        if result.get('success'):
            # Store in database if available
            if DATABASE_AVAILABLE and content_repo:
                background_tasks.add_task(
                    store_image_contribution,
                    image_data,
                    result,
                    file.filename
                )
            
            return JSONResponse(content=result)
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Analysis failed'))
            
    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced search endpoint
@app.post("/api/v1/search")
async def search_content(request: SearchRequest):
    """Search content using enhanced database queries"""
    
    if not DATABASE_AVAILABLE or not content_repo:
        raise HTTPException(
            status_code=503,
            detail="Database not available. Using fallback search."
        )
    
    try:
        # Use enhanced search with full-text search
        results = content_repo.search_content(
            query=request.query,
            filters={
                'content_type': request.content_types[0] if request.content_types else None,
                'language': request.languages[0] if request.languages else None,
                'region': request.regions[0] if request.regions else None
            }
        )
        
        return {
            "success": True,
            "results": results,
            "total": len(results),
            "query": request.query,
            "filters": {
                "content_types": request.content_types,
                "languages": request.languages,
                "regions": request.regions
            }
        }
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics endpoint
@app.get("/api/v1/analytics")
async def get_analytics():
    """Get comprehensive analytics"""
    
    if not DATABASE_AVAILABLE or not db_manager:
        # Return mock analytics
        return {
            "total_contributions": 0,
            "unique_languages": 0,
            "unique_regions": 0,
            "content_distribution": {},
            "recent_activity": [],
            "ai_processing_stats": {
                "transcriptions_today": 0,
                "translations_today": 0,
                "image_analyses_today": 0
            }
        }
    
    try:
        conn = db_manager.get_postgres_connection()
        try:
            with conn.cursor() as cursor:
                # Total contributions
                cursor.execute("SELECT COUNT(*) FROM content_metadata")
                total_contributions = cursor.fetchone()[0]
                
                # Unique languages
                cursor.execute("SELECT COUNT(DISTINCT language) FROM content_metadata")
                unique_languages = cursor.fetchone()[0]
                
                # Unique regions
                cursor.execute("SELECT COUNT(DISTINCT region) FROM content_metadata")
                unique_regions = cursor.fetchone()[0]
                
                # Content distribution
                cursor.execute("SELECT content_type, COUNT(*) FROM content_metadata GROUP BY content_type")
                content_dist = dict(cursor.fetchall())
                
                # Recent activity
                cursor.execute("""
                    SELECT title, content_type, language, created_at 
                    FROM content_metadata 
                    ORDER BY created_at DESC 
                    LIMIT 10
                """)
                recent_rows = cursor.fetchall()
                recent_activity = [
                    {
                        "title": row[0],
                        "content_type": row[1],
                        "language": row[2],
                        "created_at": row[3].isoformat() if row[3] else None
                    }
                    for row in recent_rows
                ]
                
                return {
                    "total_contributions": total_contributions,
                    "unique_languages": unique_languages,
                    "unique_regions": unique_regions,
                    "content_distribution": content_dist,
                    "recent_activity": recent_activity,
                    "ai_processing_stats": {
                        "models_loaded": AI_MODELS_AVAILABLE,
                        "processing_available": True
                    }
                }
                
        finally:
            db_manager.release_postgres_connection(conn)
            
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background task functions
async def store_audio_contribution(audio_data: bytes, analysis_result: dict, filename: str):
    """Store audio contribution in background"""
    if not content_repo:
        return
    
    try:
        metadata = {
            'title': f"Audio: {filename}",
            'description': analysis_result.get('transcription', ''),
            'language': analysis_result.get('language', 'unknown'),
            'region': 'Unknown',
            'tags': analysis_result.get('text_analysis', {}).get('keywords', []),
            'file_extension': filename.split('.')[-1] if '.' in filename else 'wav',
            'transcription': analysis_result.get('transcription', ''),
            'translation': analysis_result.get('translation', {}).get('translation', ''),
            'ai_analysis': analysis_result,
            'user_id': 'api_user'
        }
        
        content_repo.save_content('audio', audio_data, metadata)
        logger.info(f"Stored audio contribution: {filename}")
        
    except Exception as e:
        logger.error(f"Failed to store audio contribution: {e}")

async def store_text_contribution(text: str, analysis_result: dict):
    """Store text contribution in background"""
    if not content_repo:
        return
    
    try:
        metadata = {
            'title': f"Text: {text[:50]}...",
            'description': text,
            'language': analysis_result.get('language', 'unknown'),
            'region': 'Unknown',
            'tags': analysis_result.get('keywords', []),
            'file_extension': 'txt',
            'ai_analysis': analysis_result,
            'user_id': 'api_user'
        }
        
        content_repo.save_content('text', text.encode('utf-8'), metadata)
        logger.info("Stored text contribution")
        
    except Exception as e:
        logger.error(f"Failed to store text contribution: {e}")

async def store_image_contribution(image_data: bytes, analysis_result: dict, filename: str):
    """Store image contribution in background"""
    if not content_repo:
        return
    
    try:
        metadata = {
            'title': f"Image: {filename}",
            'description': analysis_result.get('caption', ''),
            'language': 'visual',
            'region': 'Unknown',
            'tags': analysis_result.get('cultural_elements', []),
            'file_extension': filename.split('.')[-1] if '.' in filename else 'jpg',
            'ai_analysis': analysis_result,
            'user_id': 'api_user'
        }
        
        content_repo.save_content('image', image_data, metadata)
        logger.info(f"Stored image contribution: {filename}")
        
    except Exception as e:
        logger.error(f"Failed to store image contribution: {e}")

# Model management endpoints
@app.get("/api/v1/models/status")
async def get_model_status():
    """Get status of all AI models"""
    if not AI_MODELS_AVAILABLE or not ai_manager:
        return {"status": "unavailable", "models": {}}
    
    return ai_manager.get_model_status()

@app.post("/api/v1/models/reload")
async def reload_models():
    """Reload AI models (admin endpoint)"""
    if not AI_MODELS_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI models not available")
    
    try:
        # Reinitialize AI manager
        global ai_manager
        from core.ai_models_enhanced import AIManager
        ai_manager = AIManager()
        
        return {"status": "success", "message": "Models reloaded successfully"}
        
    except Exception as e:
        logger.error(f"Model reload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Community endpoints
@app.get("/api/v1/community/stats")
async def get_community_stats():
    """Get community statistics"""
    if not DATABASE_AVAILABLE or not content_repo:
        # Return empty stats for fresh start
        return {
            "total_contributions": 0,
            "total_users": 0,
            "content_by_type": {
                "audio": 0,
                "text": 0,
                "image": 0
            },
            "content_by_language": {},
            "recent_activity": 0,
            "top_regions": []
        }
    
    try:
        # Get real stats from database
        stats = content_repo.get_community_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Community stats error: {e}")
        # Return empty stats on error
        return {
            "total_contributions": 0,
            "total_users": 0,
            "content_by_type": {
                "audio": 0,
                "text": 0,
                "image": 0
            },
            "content_by_language": {},
            "recent_activity": 0,
            "top_regions": []
        }

@app.get("/api/v1/community/leaderboard")
async def get_community_leaderboard():
    """Get community leaderboard"""
    if not DATABASE_AVAILABLE or not content_repo:
        # Return empty leaderboard for fresh start
        return {
            "top_contributors": [],
            "recent_contributors": [],
            "most_active_regions": []
        }
    
    try:
        # Get real leaderboard from database
        leaderboard = content_repo.get_community_leaderboard()
        return leaderboard
        
    except Exception as e:
        logger.error(f"Community leaderboard error: {e}")
        # Return empty leaderboard on error
        return {
            "top_contributors": [],
            "recent_contributors": [],
            "most_active_regions": []
        }

@app.get("/api/v1/content/recent")
async def get_recent_content():
    """Get recent content contributions"""
    if not DATABASE_AVAILABLE or not content_repo:
        # Return empty results for fresh start
        return {
            "results": [],
            "total": 0
        }
    
    try:
        # Get recent content from database
        recent_content = content_repo.get_recent_content(limit=20)
        return {
            "results": recent_content,
            "total": len(recent_content)
        }
        
    except Exception as e:
        logger.error(f"Recent content error: {e}")
        # Return empty results on error
        return {
            "results": [],
            "total": 0
        }

if __name__ == "__main__":
    import uvicorn
    
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    logger.info(f"Starting BharatVerse Enhanced API on {host}:{port}")
    logger.info(f"AI Models Available: {AI_MODELS_AVAILABLE}")
    logger.info(f"Database Available: {DATABASE_AVAILABLE}")
    
    uvicorn.run(
        "enhanced_main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )