#!/usr/bin/env python3
"""
FastAPI server for Social Companionship Agent - News API Integration
Provides top news stories for the ElevenLabs agent.
"""

from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from loguru import logger
from serpapi_service import SerpAPIService
from config import settings
import httpx

# Configure logging
logger.add(
    "logs/news_api.log",
    rotation="500 MB",
    compression="zip",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    enqueue=True
)

# Initialize FastAPI app
app = FastAPI(
    title="Social Companionship API",
    description="News and Audiobook API for Social Companionship Agent",
    version="1.0.0",
    redirect_slashes=False  # disables 301 redirect for missing or extra trailing slash
)

# Initialize services
serpapi_service = SerpAPIService()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Log the raw request body for POST requests
    if request.method == "POST" and request.url.path == "/api/v1/news/top":
        try:
            body = await request.body()
            logger.info(f"🔍 Raw POST body: {body.decode('utf-8')}")
        except Exception as e:
            logger.error(f"❌ Error reading request body: {e}")
    
    response = await call_next(request)
    return response

# Add validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"❌ Validation Error on {request.method} {request.url.path}")
    logger.error(f"📄 Request body: {await request.body()}")
    logger.error(f"🔍 Validation errors: {exc.errors()}")
    
    return JSONResponse(
        status_code=422,
        content={"detail": f"Validation error: {exc.errors()}"}
    )

# Request models
from pydantic import field_validator

class NewsRequest(BaseModel):
    q: str  # Direct search query for SerpAPI (required)
    limit: Optional[int] = 3
    
    class Config:
        # Allow extra fields that might be sent by the agent
        extra = "ignore"
    
    @field_validator('limit', mode='before')
    @classmethod
    def validate_limit(cls, v):
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                return 3
        return v

class NewsResponse(BaseModel):
    success: bool
    stories: List[dict]
    total_count: int
    language: str
    locale: Optional[str] = None
    categories: Optional[List[str]] = None



@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Social Companionship News API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "news": "/api/v1/news/top",
            "audiobooks": "/api/v1/audiobooks/search",
            "player": "/player",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "news-api"}

@app.post("/api/v1/news/top", response_model=NewsResponse)
async def get_top_news(request: NewsRequest):
    """
    Get top news stories filtered for positive, senior-friendly content.
    
    Args:
        request: News request with locale, language, categories, and limit
        
    Returns:
        NewsResponse with filtered news stories
    """
    # Log incoming request
    logger.info(f"📥 POST /api/v1/news/top - Incoming request: {request.model_dump()}")
    
    try:
        # Always use direct query approach
        limit = request.limit or 3
        
        # Validate limit
        if limit < 1 or limit > 50:
            logger.warning(f"❌ POST /api/v1/news/top - Invalid limit: {limit}")
            raise HTTPException(
                status_code=400,
                detail="Limit must be between 1 and 50"
            )
        
        logger.info(f"🔍 POST /api/v1/news/top - Fetching stories with query: '{request.q}', limit={limit}")
        
        # Always use direct query approach
        logger.info(f"🎯 Using direct query: '{request.q}'")
        
        stories = await serpapi_service.get_latest_news(
            country=None,  # Let the query handle location
            category=None,  # Let the query handle category
            language="en",  # Default to English, agent can specify in query
            size=limit,
            q=request.q  # Direct query from agent
        )
        
        if not stories:
            logger.warning(f"⚠️ POST /api/v1/news/top - No stories found for request: {request.model_dump()}")
            # Return successful response with empty stories instead of error
            response = NewsResponse(
                success=True,
                stories=[],
                total_count=0,
                language="en",
                locale=None,
                categories=None
            )
            
            # Log outgoing response
            logger.info(f"📤 POST /api/v1/news/top - Response sent: success={response.success}, total_count={response.total_count}")
            logger.info(f"📋 Empty response - no stories found for the requested criteria")
            
            return response
        
        logger.info(f"✅ POST /api/v1/news/top - Found {len(stories)} stories")
        
        # Format the response to match our expected format
        stories_data = []
        for story in stories:
            # Map SerpAPI fields to our expected format
            formatted_story = {
                "title": story.get("title", "No title"),
                "description": story.get("description", "No description available"),
                "source": story.get("source", "Unknown source"),
                "published_at": story.get("published_at", ""),
                "language": "en"
            }
            stories_data.append(formatted_story)
        
        response = NewsResponse(
            success=True,
            stories=stories_data,
            total_count=len(stories),
            language="en",
            locale=None,
            categories=None
        )
        
        # Log outgoing response with story details
        logger.info(f"📤 POST /api/v1/news/top - Response sent: success={response.success}, total_count={response.total_count}")
        for i, story in enumerate(response.stories, 1):
            logger.info(f"📰 Story {i}: {story['title']} | Source: {story['source']} | Published: {story['published_at']}")
        
        return response
        
    except HTTPException as e:
        logger.error(f"❌ POST /api/v1/news/top - HTTP Exception: {e.status_code} - {e.detail}")
        raise
    except Exception as e:
        logger.error(f"❌ POST /api/v1/news/top - Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/api/v1/news/top")
async def get_top_news_get(
    q: str,  # Direct search query for SerpAPI (required)
    limit: int = 3
):
    """
    Get top news stories (GET version for easy testing).
    
    Args:
        q: Direct search query for SerpAPI (required)
        limit: Number of stories to return (1-50)
        
    Returns:
        NewsResponse with filtered news stories
    """
    # Log incoming request
    logger.info(f"📥 GET /api/v1/news/top - Incoming request: q='{q}', limit={limit}")
    
    try:
        # Validate limit
        if limit < 1 or limit > 50:
            logger.warning(f"❌ GET /api/v1/news/top - Invalid limit: {limit}")
            raise HTTPException(
                status_code=400,
                detail="Limit must be between 1 and 50"
            )
        
        logger.info(f"🔍 GET /api/v1/news/top - Fetching stories with query: '{q}', limit={limit}")
        
        # Always use direct query approach
        logger.info(f"🎯 Using direct query: '{q}'")
        
        stories = await serpapi_service.get_latest_news(
            country=None,  # Let the query handle location
            category=None,  # Let the query handle category
            language="en",  # Default to English, agent can specify in query
            size=limit,
            q=q  # Direct query from agent
        )
        
        if not stories:
            logger.warning(f"⚠️ GET /api/v1/news/top - No stories found for request: q='{q}', limit={limit}")
            # Return successful response with empty stories instead of error
            response = NewsResponse(
                success=True,
                stories=[],
                total_count=0,
                language="en",
                locale=None,
                categories=None
            )
            
            # Log outgoing response
            logger.info(f"📤 GET /api/v1/news/top - Response sent: success={response.success}, total_count={response.total_count}")
            logger.info(f"📋 Empty response - no stories found for the requested criteria")
            
            return response
        
        logger.info(f"✅ GET /api/v1/news/top - Found {len(stories)} stories")
        
        # Format the response to match our expected format
        stories_data = []
        for story in stories:
            # Map SerpAPI fields to our expected format
            formatted_story = {
                "title": story.get("title", "No title"),
                "description": story.get("description", "No description available"),
                "source": story.get("source", "Unknown source"),
                "published_at": story.get("published_at", ""),
                "language": "en"
            }
            stories_data.append(formatted_story)
        
        response = NewsResponse(
            success=True,
            stories=stories_data,
            total_count=len(stories),
            language="en",
            locale=None,
            categories=None
        )
        
        # Log outgoing response with story details
        logger.info(f"📤 GET /api/v1/news/top - Response sent: success={response.success}, total_count={response.total_count}")
        for i, story in enumerate(response.stories, 1):
            logger.info(f"📰 Story {i}: {story['title']} | Source: {story['source']} | Published: {story['published_at']}")
        
        return response
        
    except HTTPException as e:
        logger.error(f"❌ GET /api/v1/news/top - HTTP Exception: {e.status_code} - {e.detail}")
        raise
    except Exception as e:
        logger.error(f"❌ GET /api/v1/news/top - Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


import urllib.parse


@app.get("/search_audiobooks")
async def search_audiobooks(
    title: str | None = Query(default=None),
    genre: str | None = Query(default=None),
):
    if not title and not genre:
        raise HTTPException(status_code=400, detail="Please provide title or genre")

    api_url = settings.librivox_api
    if title:
        api_url += f"&title={urllib.parse.quote(title)}"
    if genre:
        api_url += f"&genre={urllib.parse.quote(genre)}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch audiobooks: {str(e)}")

    books = data.get("books", [])

    # If a genre was specified but no books were found, raise an error
    if genre and not books:
        raise HTTPException(status_code=404, detail=f"No books found for genre: {genre}")

    results = []
    for book in books:
        authors = []
        for a in book.get("authors", []):
            if "name" in a:
                authors.append(a["name"])
            else:
                full_name = f"{a.get('first_name', '')} {a.get('last_name', '')}".strip()
                if full_name:
                    authors.append(full_name)
        if not authors:
            authors = ["Unknown Author"]

        genres_list = [g.get("name", "Unknown Genre") for g in book.get("genres", [])] or ["Unknown Genre"]

        results.append({
            "id": book.get("id"),
            "title": book.get("title"),
            "authors": authors,
            "genres": genres_list,
        })

    return {"results": results}

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    logger.info("🚀 Starting Social Companionship News API Server")
    logger.info("📡 Server will be available at: http://0.0.0.0:8000")
    logger.info("📋 API Documentation available at: http://0.0.0.0:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

