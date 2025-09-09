"""
Production FastAPI server for Railway deployment
Optimized for PostgreSQL and production environment
"""

import os
import logging
from typing import List
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Configure production logging
logging.basicConfig(
    level=logging.INFO if os.getenv("DEBUG", "false").lower() != "true" else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import our application
from api_server_db import app

# Production middleware configuration
def configure_production_middleware(application: FastAPI):
    """
    Configure middleware for production deployment
    """
    
    # CORS - Allow your Vercel frontend domain
    cors_origins = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else [
        "http://localhost:3000",  # Development
        "https://your-app-name.vercel.app",  # Production - UPDATE THIS
    ]
    
    application.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Trusted hosts - Prevent host header attacks
    trusted_hosts = ["*"]  # Railway handles this, but you can restrict further
    application.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=trusted_hosts
    )
    
    logger.info(f"✅ Production middleware configured")
    logger.info(f"📊 CORS origins: {cors_origins}")

# Production error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for production
    """
    logger.error(f"❌ Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "request_id": id(request)
        }
    )

# Production health check with enhanced information
@app.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check for monitoring
    """
    try:
        from database import check_database_connection
        from database_service import DatabaseUtilityService
        
        # Check database
        db_healthy = check_database_connection()
        db_stats = DatabaseUtilityService.get_database_stats() if db_healthy else {}
        
        # Environment info
        env_info = {
            "environment": os.getenv("ENVIRONMENT", "unknown"),
            "debug": os.getenv("DEBUG", "false"),
            "port": os.getenv("PORT", "8000"),
            "database_url_set": bool(os.getenv("DATABASE_URL")),
            "upload_dir": os.getenv("UPLOAD_DIR", "/app/uploads"),
        }
        
        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "timestamp": "2025-09-09T18:00:00Z",
            "database": {
                "connected": db_healthy,
                "statistics": db_stats
            },
            "environment": env_info,
            "features": {
                "word_cloud": True,
                "csv_upload": True,
                "column_filtering": True,
                "noise_filtering": True,
                "database_persistence": db_healthy
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": "2025-09-09T18:00:00Z"
            }
        )

# Configure production middleware
configure_production_middleware(app)

# Production startup
if __name__ == "__main__":
    # Get port from Railway environment
    port = int(os.getenv("PORT", 8000))
    
    logger.info("🚀 Starting AI Text Analysis Platform - Production Server")
    logger.info(f"📊 Port: {port}")
    logger.info(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'production')}")
    
    # Production server configuration
    uvicorn.run(
        app,
        host="0.0.0.0",  # Railway requires 0.0.0.0
        port=port,
        log_level="info" if os.getenv("DEBUG", "false").lower() != "true" else "debug",
        access_log=True,
        # Production optimizations
        loop="asyncio",
        http="auto",
        ws="auto",
        lifespan="on",
        use_colors=False,  # Better for production logs
        server_header=False,  # Security
        date_header=True,
    )
