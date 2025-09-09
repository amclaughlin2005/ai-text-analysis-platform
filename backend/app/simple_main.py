"""
Simplified FastAPI application for testing and development
Minimal setup without complex dependencies to debug issues
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Simple configuration
DEBUG = True
CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]

# Create FastAPI application
app = FastAPI(
    title="AI-Powered Text Analysis Platform - Simple",
    description="Simplified version for testing",
    version="1.0.0-simple",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI-Powered Text Analysis Platform API - Simple Mode",
        "version": "1.0.0-simple",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "test": "/test",
            "analysis": "/api/analysis/test"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0-simple",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "environment": "development"
    }

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify basic functionality"""
    return {
        "status": "success",
        "message": "Backend API is working correctly",
        "timestamp": datetime.now().isoformat(),
        "test_data": {
            "text_analysis": "ready",
            "word_cloud": "ready",
            "analytics": "ready"
        }
    }

# Simple analysis test endpoint
@app.post("/api/analysis/simple-test")
async def simple_analysis_test(text: str = "I love this amazing product!"):
    """Simple analysis test using basic Python"""
    try:
        # Simple sentiment analysis without NLTK
        positive_words = ['love', 'amazing', 'great', 'excellent', 'wonderful', 'fantastic', 'good', 'happy']
        negative_words = ['hate', 'terrible', 'awful', 'bad', 'horrible', 'sad', 'angry', 'frustrated']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            score = 0.7
        elif negative_count > positive_count:
            sentiment = 'negative' 
            score = -0.7
        else:
            sentiment = 'neutral'
            score = 0.0
        
        # Simple entity extraction (basic pattern matching)
        import re
        entities = {
            'emails': re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text),
            'capitalized_words': re.findall(r'\b[A-Z][a-z]+\b', text)
        }
        
        return {
            'status': 'success',
            'input_text': text,
            'analysis': {
                'sentiment': {
                    'label': sentiment,
                    'score': score,
                    'positive_words_found': positive_count,
                    'negative_words_found': negative_count
                },
                'entities': entities,
                'basic_stats': {
                    'word_count': len(text.split()),
                    'character_count': len(text),
                    'sentence_count': len(text.split('.'))
                }
            },
            'note': 'This is a simplified analysis. Full NLTK engine available at /api/analysis/test'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Simple analysis failed: {str(e)}",
            'input_text': text
        }

# Import basic modules for the test
import sys
from datetime import datetime

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Simple FastAPI Server...")
    print("   URL: http://localhost:8000")
    print("   Docs: http://localhost:8000/docs")
    print("   Test: http://localhost:8000/test")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
