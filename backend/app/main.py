"""
FastAPI main application for AI-Powered Text Analysis Platform
Provides REST API endpoints, WebSocket connections, and Clerk authentication integration.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import os
from contextlib import asynccontextmanager

from .core.config import get_settings
from .core.database import engine, Base
from .core.logging import setup_logging
from .api import datasets, analysis, wordcloud, analytics, export_router, schema
from .websocket.manager import connection_manager
from .websocket import handlers as websocket_handlers

# Initialize settings
settings = get_settings()

# Setup logging
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting AI-Powered Text Analysis Platform...")
    
    # Create database tables
    try:
        # Import all models to ensure they're registered with Base
        from .models import user, dataset, question, analysis_job, analytics, data_schema
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")
    
    # Initialize NLTK data
    try:
        import nltk
        nltk_downloads = [
            'vader_lexicon', 'punkt', 'stopwords', 'wordnet',
            'averaged_perceptron_tagger', 'maxent_ne_chunker', 'words'
        ]
        for download in nltk_downloads:
            nltk.download(download, quiet=True)
        print("✅ NLTK data initialized")
    except Exception as e:
        print(f"⚠️  NLTK initialization warning: {e}")
    
    # Initialize spaCy model
    try:
        import spacy
        spacy.load("en_core_web_sm")
        print("✅ spaCy model loaded")
    except Exception as e:
        print(f"⚠️  spaCy model warning: {e}")
        print("   Run: python -m spacy download en_core_web_sm")
    
    print("🎯 Application startup complete!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down AI-Powered Text Analysis Platform...")
    # Close WebSocket connections
    await connection_manager.disconnect_all()
    print("✅ Cleanup complete")

# Create FastAPI application
app = FastAPI(
    title="AI-Powered Text Analysis Platform",
    description="Comprehensive text analysis using NLTK and LLM integration with interactive visualizations",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Add security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(datasets.router, prefix="/api/datasets", tags=["datasets"])
app.include_router(schema.router)  # Schema router has its own prefix defined
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(wordcloud.router, prefix="/api/wordcloud", tags=["wordcloud"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(export_router.router, prefix="/api/export", tags=["export"])

# Include WebSocket handlers
app.include_router(websocket_handlers.router, prefix="/ws")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI-Powered Text Analysis Platform API",
        "version": "1.0.0",
        "status": "active",
        "features": [
            "NLTK text analysis",
            "LLM integration", 
            "Flexible JSON/CSV ingestion",
            "Smart schema detection",
            "Interactive word clouds",
            "Real-time processing",
            "Advanced analytics",
            "Multi-format export"
        ],
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "database": "connected",  # TODO: Add actual database health check
        "redis": "connected",     # TODO: Add actual Redis health check
        "version": "1.0.0"
    }

@app.get("/api/status")
async def api_status():
    """Detailed API status information"""
    return {
        "api_version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "database_url": settings.DATABASE_URL.split("@")[-1] if settings.DATABASE_URL else "Not configured",  # Hide credentials
        "redis_connected": True,  # TODO: Add actual Redis check
        "openai_configured": bool(settings.OPENAI_API_KEY),
        "clerk_configured": bool(settings.CLERK_SECRET_KEY),
        "s3_configured": bool(settings.AWS_ACCESS_KEY_ID),
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return HTTPException(
        status_code=404,
        detail={
            "message": "Endpoint not found",
            "path": str(request.url.path),
            "available_endpoints": [
                "/docs", "/health", "/api/status",
                "/api/datasets", "/api/analysis", "/api/wordcloud",
                "/api/analytics", "/api/export", "/ws"
            ]
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler"""
    return HTTPException(
        status_code=500,
        detail={
            "message": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )

# Development server
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )
