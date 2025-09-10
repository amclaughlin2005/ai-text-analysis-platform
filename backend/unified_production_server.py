"""
Unified production server for Railway deployment
Uses the main FastAPI application with proper database configuration
"""

import os
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Set environment for production
os.environ.setdefault("APP_ENV", "production")

# Add backend directory to Python path for proper imports
import sys
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import the main application
from app.main import app
from app.core.config import get_settings

settings = get_settings()

def configure_production_middleware(application: FastAPI):
    """Configure middleware for production deployment"""
    
    # Production CORS configuration
    production_origins = [
        "https://ai-text-analysis-platform.vercel.app",
        "https://ai-text-analysis-platform-git-main.vercel.app", 
        "https://ai-text-analysis-platform-amclaughlin2005.vercel.app",
        "https://wordcloud-six-eta.vercel.app",  # Alternative domain
    ]
    
    # Add development origins if debug is enabled
    if settings.DEBUG:
        production_origins.extend([
            "http://localhost:3000",
            "http://localhost:3001", 
            "http://127.0.0.1:3000"
        ])
    
    # Get origins from environment
    env_origins = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else []
    all_origins = production_origins + [origin.strip() for origin in env_origins if origin.strip()]
    
    logger.info(f"🌐 CORS origins configured: {all_origins}")
    
    # Configure CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=all_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Trusted hosts
    trusted_hosts = ["*"]  # Railway handles host validation
    application.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=trusted_hosts
    )

def ensure_upload_directory():
    """Ensure upload directory exists"""
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(exist_ok=True, parents=True)
    logger.info(f"📁 Upload directory ensured: {upload_dir.absolute()}")

# Configure the application
configure_production_middleware(app)
ensure_upload_directory()

# Add production-specific endpoints
@app.get("/health")
async def basic_health():
    """Basic health check for Railway"""
    return {"status": "healthy", "service": "unified-server"}

@app.get("/production/health")
async def production_health():
    """Production health check with detailed information"""
    try:
        from app.core.database import DatabaseHealthCheck
        
        # Check database connection
        db_healthy = DatabaseHealthCheck.check_connection()
        db_info = DatabaseHealthCheck.get_connection_info()
        
        upload_dir = Path(settings.UPLOAD_DIR)
        
        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "database": {
                "healthy": db_healthy,
                "info": db_info
            },
            "storage": {
                "upload_dir": str(upload_dir.absolute()),
                "upload_dir_exists": upload_dir.exists(),
                "upload_dir_writable": upload_dir.is_dir() and os.access(upload_dir, os.W_OK)
            },
            "features": {
                "dataset_upload": True,
                "word_cloud_generation": True,
                "nltk_analysis": True,
                "csv_processing": True,
                "database_persistence": db_healthy
            },
            "version": "2.0.0-unified"
        }
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }

@app.get("/production/info")
async def production_info():
    """Production environment information"""
    return {
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "version": "2.0.0-unified",
        "features": [
            "Unified FastAPI architecture",
            "Robust file upload validation", 
            "PostgreSQL persistence",
            "NLTK text analysis",
            "Interactive word clouds",
            "Background job processing",
            "Comprehensive error handling"
        ],
        "api_docs": "/docs" if settings.DEBUG else None,
        "upload_config": {
            "max_file_size_mb": settings.MAX_FILE_SIZE / (1024 * 1024),
            "upload_directory": settings.UPLOAD_DIR,
            "supported_encodings": ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]
        }
    }

# Production startup
if __name__ == "__main__":
    # Get port from Railway environment
    port = int(os.getenv("PORT", 8000))
    
    logger.info("🚀 Starting AI Text Analysis Platform - Unified Production Server")
    logger.info(f"📊 Port: {port}")
    logger.info(f"🌍 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔗 Binding to: 0.0.0.0:{port}")
    logger.info(f"📋 Database: {settings.DATABASE_URL.split('@')[-1] if settings.DATABASE_URL else 'Not configured'}")
    logger.info(f"📁 Upload directory: {settings.UPLOAD_DIR}")
    
    # Production server configuration
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True,
        # Production optimizations
        loop="asyncio",
        http="auto", 
        ws="auto",
        lifespan="on",
        use_colors=False,
        server_header=False,
        date_header=True,
    )
