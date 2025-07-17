from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
from datetime import datetime
import uuid
import sqlite3
from pathlib import Path

# Initialize FastAPI app
app = FastAPI(
    title="TeluguVerse API",
    description="API for preserving and accessing Telugu cultural heritage",
    version="1.0.0",
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

# Pydantic models
class ContributionBase(BaseModel):
    title: str
    description: str
    content_type: str
    language: str
    region: str
    tags: List[str]
    metadata: Optional[Dict[str, Any]] = {}

class ContributionCreate(ContributionBase):
    pass

class ContributionResponse(ContributionBase):
    id: str
    contributor_id: str
    created_at: datetime
    updated_at: datetime
    status: str
    quality_score: Optional[float] = None

class SearchQuery(BaseModel):
    query: str
    content_types: Optional[List[str]] = []
    languages: Optional[List[str]] = []
    regions: Optional[List[str]] = []
    tags: Optional[List[str]] = []
    limit: Optional[int] = 20
    offset: Optional[int] = 0

class AnalyticsResponse(BaseModel):
    total_contributions: int
    unique_languages: int
    unique_regions: int
    content_distribution: Dict[str, int]
    recent_activity: List[Dict[str, Any]]

# Database helper functions
def get_db_connection():
    """Get database connection"""
    db_path = Path(__file__).parent.parent / "data" / "teluguverse.db"
    db_path.parent.mkdir(exist_ok=True)
    return sqlite3.connect(str(db_path))

def init_api_db():
    """Initialize API database tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # API keys table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id TEXT PRIMARY KEY,
            key_hash TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            permissions TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # API usage logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_usage (
            id TEXT PRIMARY KEY,
            api_key_id TEXT,
            endpoint TEXT NOT NULL,
            method TEXT NOT NULL,
            status_code INTEGER,
            response_time REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (api_key_id) REFERENCES api_keys (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_api_db()

# API key validation (simplified for demo)
async def validate_api_key(api_key: str = None):
    """Validate API key (simplified implementation)"""
    # In production, implement proper API key validation
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    return {"api_key": api_key, "permissions": ["read", "write"]}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to TeluguVerse API",
        "version": "1.0.0",
        "documentation": "/docs",
        "status": "active"
    }

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Contributions endpoints
@app.post("/api/v1/contributions", response_model=ContributionResponse)
async def create_contribution(
    contribution: ContributionCreate,
    api_key: dict = Depends(validate_api_key)
):
    """Create a new cultural contribution"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        contribution_id = str(uuid.uuid4())
        now = datetime.now()
        
        cursor.execute('''
            INSERT INTO contributions (
                id, title, description, content_type, language, region, 
                tags, metadata, contributor_id, created_at, updated_at, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            contribution_id,
            contribution.title,
            contribution.description,
            contribution.content_type,
            contribution.language,
            contribution.region,
            json.dumps(contribution.tags),
            json.dumps(contribution.metadata),
            "api_user",  # In production, get from API key
            now,
            now,
            "pending"
        ))
        
        conn.commit()
        conn.close()
        
        return ContributionResponse(
            id=contribution_id,
            contributor_id="api_user",
            created_at=now,
            updated_at=now,
            status="pending",
            **contribution.dict()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/contributions", response_model=List[ContributionResponse])
async def get_contributions(
    limit: int = 20,
    offset: int = 0,
    content_type: Optional[str] = None,
    language: Optional[str] = None,
    region: Optional[str] = None,
    api_key: dict = Depends(validate_api_key)
):
    """Get list of contributions with optional filters"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM contributions WHERE 1=1"
        params = []
        
        if content_type:
            query += " AND content_type = ?"
            params.append(content_type)
        
        if language:
            query += " AND language = ?"
            params.append(language)
        
        if region:
            query += " AND region = ?"
            params.append(region)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        contributions = []
        for row in rows:
            contributions.append(ContributionResponse(
                id=row[0],
                title=row[1],
                description=row[2],
                content_type=row[3],
                language=row[4],
                region=row[5],
                tags=json.loads(row[6]) if row[6] else [],
                metadata=json.loads(row[7]) if row[7] else {},
                contributor_id=row[8],
                created_at=datetime.fromisoformat(row[9]),
                updated_at=datetime.fromisoformat(row[10]),
                status=row[11],
                quality_score=row[12] if row[12] else None
            ))
        
        return contributions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/contributions/{contribution_id}", response_model=ContributionResponse)
async def get_contribution(
    contribution_id: str,
    api_key: dict = Depends(validate_api_key)
):
    """Get a specific contribution by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM contributions WHERE id = ?", (contribution_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Contribution not found")
        
        return ContributionResponse(
            id=row[0],
            title=row[1],
            description=row[2],
            content_type=row[3],
            language=row[4],
            region=row[5],
            tags=json.loads(row[6]) if row[6] else [],
            metadata=json.loads(row[7]) if row[7] else {},
            contributor_id=row[8],
            created_at=datetime.fromisoformat(row[9]),
            updated_at=datetime.fromisoformat(row[10]),
            status=row[11],
            quality_score=row[12] if row[12] else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Search endpoint
@app.post("/api/v1/search")
async def search_contributions(
    search_query: SearchQuery,
    api_key: dict = Depends(validate_api_key)
):
    """Search contributions with advanced filters"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM contributions WHERE 1=1"
        params = []
        
        # Text search
        if search_query.query:
            query += " AND (title LIKE ? OR description LIKE ? OR tags LIKE ?)"
            search_term = f"%{search_query.query}%"
            params.extend([search_term, search_term, search_term])
        
        # Content type filter
        if search_query.content_types:
            placeholders = ",".join(["?" for _ in search_query.content_types])
            query += f" AND content_type IN ({placeholders})"
            params.extend(search_query.content_types)
        
        # Language filter
        if search_query.languages:
            placeholders = ",".join(["?" for _ in search_query.languages])
            query += f" AND language IN ({placeholders})"
            params.extend(search_query.languages)
        
        # Region filter
        if search_query.regions:
            placeholders = ",".join(["?" for _ in search_query.regions])
            query += f" AND region IN ({placeholders})"
            params.extend(search_query.regions)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([search_query.limit, search_query.offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "content_type": row[3],
                "language": row[4],
                "region": row[5],
                "tags": json.loads(row[6]) if row[6] else [],
                "created_at": row[9],
                "quality_score": row[12] if row[12] else None
            })
        
        return {
            "results": results,
            "total": len(results),
            "query": search_query.query,
            "filters_applied": {
                "content_types": search_query.content_types,
                "languages": search_query.languages,
                "regions": search_query.regions
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Analytics endpoint
@app.get("/api/v1/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    api_key: dict = Depends(validate_api_key)
):
    """Get platform analytics and statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total contributions
        cursor.execute("SELECT COUNT(*) FROM contributions")
        total_contributions = cursor.fetchone()[0]
        
        # Unique languages
        cursor.execute("SELECT COUNT(DISTINCT language) FROM contributions")
        unique_languages = cursor.fetchone()[0]
        
        # Unique regions
        cursor.execute("SELECT COUNT(DISTINCT region) FROM contributions")
        unique_regions = cursor.fetchone()[0]
        
        # Content distribution
        cursor.execute("SELECT content_type, COUNT(*) FROM contributions GROUP BY content_type")
        content_dist = dict(cursor.fetchall())
        
        # Recent activity
        cursor.execute("""
            SELECT title, content_type, language, created_at 
            FROM contributions 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        recent_rows = cursor.fetchall()
        recent_activity = [
            {
                "title": row[0],
                "content_type": row[1],
                "language": row[2],
                "created_at": row[3]
            }
            for row in recent_rows
        ]
        
        conn.close()
        
        return AnalyticsResponse(
            total_contributions=total_contributions,
            unique_languages=unique_languages,
            unique_regions=unique_regions,
            content_distribution=content_dist,
            recent_activity=recent_activity
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# File upload endpoint
@app.post("/api/v1/upload")
async def upload_file(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(...),
    content_type: str = Form(...),
    language: str = Form(...),
    region: str = Form(...),
    tags: str = Form(""),
    api_key: dict = Depends(validate_api_key)
):
    """Upload a file with metadata"""
    try:
        # Create uploads directory
        upload_dir = Path(__file__).parent.parent / "uploads"
        upload_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = upload_dir / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Create contribution record
        conn = get_db_connection()
        cursor = conn.cursor()
        
        contribution_id = str(uuid.uuid4())
        now = datetime.now()
        tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        cursor.execute('''
            INSERT INTO contributions (
                id, title, description, content_type, language, region, 
                tags, metadata, contributor_id, created_at, updated_at, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            contribution_id,
            title,
            description,
            content_type,
            language,
            region,
            json.dumps(tags_list),
            json.dumps({
                "filename": file.filename,
                "file_path": str(file_path),
                "file_size": len(content),
                "mime_type": file.content_type
            }),
            "api_user",
            now,
            now,
            "pending"
        ))
        
        conn.commit()
        conn.close()
        
        return {
            "message": "File uploaded successfully",
            "contribution_id": contribution_id,
            "filename": file.filename,
            "file_size": len(content),
            "status": "pending"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Languages endpoint
@app.get("/api/v1/languages")
async def get_languages(api_key: dict = Depends(validate_api_key)):
    """Get list of available languages"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT language, COUNT(*) as count FROM contributions GROUP BY language ORDER BY count DESC")
        languages = [{"language": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        conn.close()
        return {"languages": languages}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Regions endpoint
@app.get("/api/v1/regions")
async def get_regions(api_key: dict = Depends(validate_api_key)):
    """Get list of available regions"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT region, COUNT(*) as count FROM contributions GROUP BY region ORDER BY count DESC")
        regions = [{"region": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        conn.close()
        return {"regions": regions}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Tags endpoint
@app.get("/api/v1/tags")
async def get_popular_tags(api_key: dict = Depends(validate_api_key)):
    """Get popular tags"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT tags FROM contributions WHERE tags IS NOT NULL AND tags != '[]'")
        all_tags = []
        
        for row in cursor.fetchall():
            tags = json.loads(row[0])
            all_tags.extend(tags)
        
        # Count tag frequency
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Sort by frequency
        popular_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:50]
        
        conn.close()
        return {"tags": [{"tag": tag, "count": count} for tag, count in popular_tags]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)