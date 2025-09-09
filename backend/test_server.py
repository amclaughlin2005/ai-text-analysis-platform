"""
Minimal test server to debug issues
"""

import sys
from datetime import datetime

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    print("✅ FastAPI import successful")
except ImportError as e:
    print(f"❌ FastAPI import failed: {e}")
    sys.exit(1)

# Create minimal app
app = FastAPI(
    title="Test Server",
    description="Minimal test server for debugging",
    version="1.0.0-test"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Test server is running!",
        "timestamp": datetime.now().isoformat(),
        "status": "ok"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "server": "test",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/test-analysis")
def test_analysis():
    """Test basic text analysis without NLTK"""
    test_text = "I love this product!"
    
    # Very basic sentiment
    positive_words = ['love', 'like', 'great', 'good', 'excellent']
    negative_words = ['hate', 'bad', 'terrible', 'awful']
    
    sentiment = "positive" if any(word in test_text.lower() for word in positive_words) else \
               "negative" if any(word in test_text.lower() for word in negative_words) else \
               "neutral"
    
    return {
        "input": test_text,
        "sentiment": sentiment,
        "word_count": len(test_text.split()),
        "status": "basic_analysis_complete"
    }

if __name__ == "__main__":
    print("🚀 Starting minimal test server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    
    try:
        import uvicorn
        uvicorn.run(
            "test_server:app",
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reload for testing
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        import traceback
        traceback.print_exc()
