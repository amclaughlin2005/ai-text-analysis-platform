#!/usr/bin/env python3
"""
Railway deployment entry point for AI Text Analysis Platform
Imports and starts the main application with schema endpoints
"""

import os
import logging
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Start the application for Railway deployment"""
    try:
        # Import the main FastAPI app
        from app.main import app
        
        # Get port from Railway environment
        port = int(os.getenv("PORT", 8000))
        
        logger.info("🚀 Starting AI Text Analysis Platform - Railway Deployment")
        logger.info(f"📊 Port: {port}")
        logger.info(f"🌍 Environment: {os.getenv('APP_ENV', 'production')}")
        logger.info(f"🔗 Binding to: 0.0.0.0:{port}")
        
        # Start the server
        uvicorn.run(
            app,
            host="0.0.0.0", 
            port=port,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        raise

if __name__ == "__main__":
    main()
