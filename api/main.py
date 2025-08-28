"""
BharatVerse API Server
Handles search and other API requests for the Streamlit application
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="BharatVerse API",
    description="API for BharatVerse Cultural Heritage Platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class SearchRequest(BaseModel):
    query: str = ""
    content_types: List[str] = []
    languages: List[str] = []
    regions: List[str] = []
    categories: List[str] = []
    limit: int = 20
    offset: int = 0

class SearchResult(BaseModel):
    id: str
    title: str
    description: str
    type: str
    language: str
    region: str
    quality: int
    tags: List[str]
    created_at: Optional[str] = None
    author: Optional[str] = None

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total: int
    query: str

# Mock data generator for development
def generate_mock_results(request: SearchRequest) -> List[Dict[str, Any]]:
    """Generate mock search results for development"""
    mock_results = []
    
    # Sample data templates
    templates = [
        {
            "type": "Audio",
            "titles": ["Traditional Bengali Folk Song", "Rabindra Sangeet Collection", "Baul Songs of Bengal"],
            "languages": ["Bengali"],
            "regions": ["East India"],
            "tags": ["folk", "traditional", "music", "heritage"]
        },
        {
            "type": "Text",
            "titles": ["Ancient Tamil Poetry", "Thirukkural Verses", "Sangam Literature"],
            "languages": ["Tamil"],
            "regions": ["South India"],
            "tags": ["poetry", "literature", "classical", "ancient"]
        },
        {
            "type": "Recipe",
            "titles": ["Traditional Punjabi Recipes", "Makki di Roti Recipe", "Sarson da Saag"],
            "languages": ["Punjabi", "Hindi"],
            "regions": ["North India"],
            "tags": ["food", "recipe", "traditional", "cuisine"]
        },
        {
            "type": "Story",
            "titles": ["Panchatantra Tales", "Jataka Stories", "Folk Tales of India"],
            "languages": ["Hindi", "Sanskrit"],
            "regions": ["Central India"],
            "tags": ["story", "folklore", "moral", "children"]
        }
    ]
    
    # Filter templates based on request
    filtered_templates = templates
    if request.content_types:
        filtered_templates = [t for t in filtered_templates if t["type"] in request.content_types]
    if request.languages:
        filtered_templates = [t for t in filtered_templates 
                             if any(lang in request.languages for lang in t["languages"])]
    if request.regions:
        filtered_templates = [t for t in filtered_templates 
                             if any(region in request.regions for region in t["regions"])]
    
    # Generate results from filtered templates
    for i, template in enumerate(filtered_templates[:request.limit]):
        for j, title in enumerate(template["titles"][:3]):
            if len(mock_results) >= request.limit:
                break
            
            # Add query relevance if query exists
            if request.query and request.query.lower() not in title.lower():
                continue
                
            mock_results.append({
                "id": f"result_{i}_{j}",
                "title": title,
                "description": f"A beautiful example of {template['type'].lower()} content from {template['regions'][0]}. "
                              f"This {template['languages'][0]} piece represents the rich cultural heritage of India.",
                "type": template["type"],
                "language": template["languages"][0],
                "region": template["regions"][0],
                "quality": 85 + (i * 3) % 15,  # Random quality between 85-100
                "tags": template["tags"],
                "created_at": datetime.now().isoformat(),
                "author": f"Contributor_{i+1}"
            })
    
    # If no results match filters, return empty list
    if not mock_results and (request.query or request.content_types or request.languages or request.regions):
        return []
    
    # If still no results, add some default ones
    if not mock_results:
        mock_results = [
            {
                "id": "default_1",
                "title": "Welcome to BharatVerse",
                "description": "Start exploring India's rich cultural heritage. Upload your own content to see it appear in search results!",
                "type": "Text",
                "language": "English",
                "region": "All India",
                "quality": 100,
                "tags": ["welcome", "introduction", "platform"],
                "created_at": datetime.now().isoformat(),
                "author": "BharatVerse Team"
            }
        ]
    
    return mock_results

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to BharatVerse API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "search": "/api/v1/search",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Search for cultural content
    """
    try:
        logger.info(f"Search request: query='{request.query}', types={request.content_types}, languages={request.languages}")
        
        # For now, return mock data
        # In production, this would query the actual database
        results = generate_mock_results(request)
        
        return SearchResponse(
            results=results,
            total=len(results),
            query=request.query
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/content")
async def create_content(content: Dict[str, Any]):
    """
    Create new content (placeholder)
    """
    return {
        "success": True,
        "message": "Content created successfully",
        "id": "new_content_123"
    }

@app.get("/api/v1/content/{content_id}")
async def get_content(content_id: str):
    """
    Get specific content (placeholder)
    """
    return {
        "id": content_id,
        "title": "Sample Content",
        "type": "Text",
        "description": "This is a placeholder for content retrieval"
    }

# Run the server if executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
