#!/usr/bin/env python3
"""
Working FastAPI server for the AI-Powered Text Analysis Platform
Simplified version that works without complex import issues
"""

import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    print("✅ FastAPI and dependencies imported successfully")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("Run: pip3 install fastapi uvicorn pydantic")
    sys.exit(1)

# Create FastAPI app
app = FastAPI(
    title="AI-Powered Text Analysis Platform",
    description="Text analysis API with NLTK and LLM integration",
    version="1.0.0-working",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Request models
class TextAnalysisRequest(BaseModel):
    text: str

class WordCloudRequest(BaseModel):
    dataset_id: str
    mode: str = "all"
    filters: Dict[str, Any] = {}

# Basic endpoints
@app.get("/")
async def root():
    return {
        "message": "AI-Powered Text Analysis Platform API",
        "version": "1.0.0-working", 
        "status": "running",
        "features": [
            "Basic sentiment analysis",
            "Simple text processing",
            "Word cloud generation",
            "Mock data for frontend testing"
        ],
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "analysis_test": "/api/analysis/test",
            "word_cloud": "/api/wordcloud/generate"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0-working",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    }

# Analysis endpoints
@app.get("/api/analysis/test")
async def test_analysis_simple():
    """Simple analysis test without NLTK dependencies"""
    test_text = "I am very happy with the excellent customer service!"
    
    # Basic sentiment analysis
    positive_words = ['happy', 'excellent', 'great', 'good', 'love', 'amazing', 'wonderful']
    negative_words = ['sad', 'terrible', 'bad', 'hate', 'awful', 'horrible', 'angry']
    
    text_lower = test_text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        sentiment = 'positive'
        score = 0.8
    elif negative_count > positive_count:
        sentiment = 'negative'
        score = -0.8
    else:
        sentiment = 'neutral'
        score = 0.0
    
    return {
        'status': 'success',
        'test_text': test_text,
        'results': {
            'sentiment': {
                'label': sentiment,
                'score': score,
                'confidence': 0.7,
                'positive_indicators': positive_count,
                'negative_indicators': negative_count
            },
            'basic_stats': {
                'word_count': len(test_text.split()),
                'character_count': len(test_text),
                'sentence_count': len([s for s in test_text.split('.') if s.strip()])
            }
        },
        'message': 'Simple analysis engine working - NLTK integration pending'
    }

@app.post("/api/analysis/sentiment")
async def analyze_sentiment(request: TextAnalysisRequest):
    """Basic sentiment analysis"""
    try:
        text = request.text
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Simple sentiment scoring
        positive_words = ['happy', 'excellent', 'great', 'good', 'love', 'amazing', 'wonderful', 'fantastic', 'pleased', 'satisfied']
        negative_words = ['sad', 'terrible', 'bad', 'hate', 'awful', 'horrible', 'angry', 'frustrated', 'disappointed', 'upset']
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            sentiment_score = 0.0
            sentiment_label = 'neutral'
        else:
            sentiment_score = (positive_count - negative_count) / total_sentiment_words
            if sentiment_score > 0.2:
                sentiment_label = 'positive'
            elif sentiment_score < -0.2:
                sentiment_label = 'negative'
            else:
                sentiment_label = 'neutral'
        
        return {
            'status': 'success',
            'data': {
                'compound_score': sentiment_score,
                'positive': positive_count / len(words) if words else 0,
                'negative': negative_count / len(words) if words else 0,
                'neutral': 1 - ((positive_count + negative_count) / len(words)) if words else 1,
                'label': sentiment_label,
                'confidence': 0.7,
                'method': 'simple_lexicon'
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")

# Word cloud endpoints
@app.post("/api/wordcloud/generate")
async def generate_wordcloud(request: WordCloudRequest):
    """Generate mock word cloud data for frontend testing"""
    try:
        mode = request.mode
        
        # Mock word data based on mode
        word_sets = {
            'all': [
                {'word': 'customer', 'frequency': 85, 'sentiment': 'neutral'},
                {'word': 'support', 'frequency': 72, 'sentiment': 'positive'}, 
                {'word': 'service', 'frequency': 68, 'sentiment': 'positive'},
                {'word': 'help', 'frequency': 65, 'sentiment': 'positive'},
                {'word': 'issue', 'frequency': 58, 'sentiment': 'negative'},
                {'word': 'problem', 'frequency': 45, 'sentiment': 'negative'},
                {'word': 'solution', 'frequency': 42, 'sentiment': 'positive'},
                {'word': 'team', 'frequency': 38, 'sentiment': 'neutral'},
                {'word': 'quality', 'frequency': 35, 'sentiment': 'positive'},
                {'word': 'experience', 'frequency': 32, 'sentiment': 'neutral'},
            ],
            'verbs': [
                {'word': 'help', 'frequency': 65, 'sentiment': 'positive'},
                {'word': 'solve', 'frequency': 45, 'sentiment': 'positive'},
                {'word': 'support', 'frequency': 42, 'sentiment': 'positive'},
                {'word': 'fix', 'frequency': 38, 'sentiment': 'positive'},
                {'word': 'assist', 'frequency': 35, 'sentiment': 'positive'},
                {'word': 'resolve', 'frequency': 32, 'sentiment': 'positive'},
                {'word': 'provide', 'frequency': 28, 'sentiment': 'neutral'},
                {'word': 'understand', 'frequency': 25, 'sentiment': 'neutral'},
                {'word': 'explain', 'frequency': 22, 'sentiment': 'neutral'},
                {'word': 'improve', 'frequency': 20, 'sentiment': 'positive'},
            ],
            'emotions': [
                {'word': 'happy', 'frequency': 45, 'sentiment': 'positive'},
                {'word': 'frustrated', 'frequency': 42, 'sentiment': 'negative'},
                {'word': 'satisfied', 'frequency': 38, 'sentiment': 'positive'},
                {'word': 'confused', 'frequency': 35, 'sentiment': 'negative'},
                {'word': 'pleased', 'frequency': 32, 'sentiment': 'positive'},
                {'word': 'disappointed', 'frequency': 28, 'sentiment': 'negative'},
                {'word': 'grateful', 'frequency': 25, 'sentiment': 'positive'},
                {'word': 'worried', 'frequency': 22, 'sentiment': 'negative'},
                {'word': 'excited', 'frequency': 20, 'sentiment': 'positive'},
                {'word': 'calm', 'frequency': 18, 'sentiment': 'neutral'},
            ],
            'themes': [
                {'word': 'billing', 'frequency': 55, 'sentiment': 'negative'},
                {'word': 'technical', 'frequency': 48, 'sentiment': 'neutral'},
                {'word': 'account', 'frequency': 42, 'sentiment': 'neutral'},
                {'word': 'feature', 'frequency': 38, 'sentiment': 'positive'},
                {'word': 'security', 'frequency': 35, 'sentiment': 'neutral'},
                {'word': 'performance', 'frequency': 32, 'sentiment': 'negative'},
                {'word': 'training', 'frequency': 28, 'sentiment': 'neutral'},
                {'word': 'integration', 'frequency': 25, 'sentiment': 'neutral'},
                {'word': 'mobile', 'frequency': 22, 'sentiment': 'neutral'},
                {'word': 'documentation', 'frequency': 20, 'sentiment': 'negative'},
            ],
            'entities': [
                {'word': 'John Smith', 'frequency': 25, 'sentiment': 'neutral'},
                {'word': 'Microsoft', 'frequency': 22, 'sentiment': 'neutral'},
                {'word': 'Chicago', 'frequency': 20, 'sentiment': 'neutral'},
                {'word': 'Sales Team', 'frequency': 18, 'sentiment': 'positive'},
                {'word': 'Product X', 'frequency': 15, 'sentiment': 'neutral'},
                {'word': 'Support Dept', 'frequency': 12, 'sentiment': 'positive'},
                {'word': 'System Alpha', 'frequency': 10, 'sentiment': 'neutral'},
                {'word': 'Manager', 'frequency': 8, 'sentiment': 'neutral'},
                {'word': 'Customer ID', 'frequency': 5, 'sentiment': 'neutral'},
            ],
            'topics': [
                {'word': 'payment processing', 'frequency': 35, 'sentiment': 'negative'},
                {'word': 'user interface', 'frequency': 32, 'sentiment': 'neutral'},
                {'word': 'data migration', 'frequency': 28, 'sentiment': 'negative'},
                {'word': 'system performance', 'frequency': 25, 'sentiment': 'negative'},
                {'word': 'security features', 'frequency': 22, 'sentiment': 'positive'},
                {'word': 'mobile application', 'frequency': 20, 'sentiment': 'neutral'},
                {'word': 'customer support', 'frequency': 18, 'sentiment': 'positive'},
                {'word': 'integration tools', 'frequency': 15, 'sentiment': 'neutral'},
            ]
        }
        
        # Get words for the requested mode
        words = word_sets.get(mode, word_sets['all'])
        
        # Format for frontend
        formatted_words = []
        for word_data in words:
            formatted_words.append({
                'id': f"{word_data['word'].replace(' ', '_')}_{word_data['frequency']}",
                'word': word_data['word'],
                'frequency': word_data['frequency'],
                'normalized_frequency': word_data['frequency'] / 100,
                'sentiment_association': word_data['sentiment'],
                'word_type': mode,
                'significance_score': word_data['frequency'] / 100,
                'theme_category': mode
            })
        
        return {
            'status': 'success',
            'data': {
                'words': formatted_words,
                'metadata': {
                    'total_words': len(formatted_words),
                    'analysis_mode': mode,
                    'dataset_id': request.dataset_id,
                    'generated_at': datetime.now().isoformat(),
                    'note': 'Mock data - real analysis pending NLTK integration'
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Word cloud generation failed: {str(e)}")

@app.get("/api/wordcloud/modes")
async def get_wordcloud_modes():
    """Get available word cloud analysis modes"""
    return {
        'status': 'success',
        'data': {
            'modes': [
                'all', 'verbs', 'themes', 'emotions', 'entities', 'topics'
            ]
        }
    }

# Dataset endpoints
@app.get("/api/datasets")
async def get_datasets():
    """Get list of datasets (mock data)"""
    return {
        'status': 'success',
        'data': {
            'datasets': [
                {
                    'id': 'demo-dataset-1',
                    'name': 'Customer Support Demo',
                    'status': 'completed',
                    'total_questions': 150,
                    'created_at': '2024-01-15T10:00:00Z',
                    'sentiment_avg': 0.65
                }
            ]
        }
    }

# Analytics endpoints  
@app.get("/api/analytics/sentiment-trends")
async def get_sentiment_trends(dataset_id: str):
    """Get sentiment trends (mock data)"""
    return {
        'status': 'success',
        'data': {
            'trends': [
                {'date': '2024-01-01', 'positive': 0.6, 'negative': 0.2, 'neutral': 0.2},
                {'date': '2024-01-02', 'positive': 0.7, 'negative': 0.15, 'neutral': 0.15},
                {'date': '2024-01-03', 'positive': 0.65, 'negative': 0.25, 'neutral': 0.1},
            ],
            'dataset_id': dataset_id
        }
    }

# Simple NLTK test (if available)
@app.get("/api/analysis/nltk-status") 
async def nltk_status():
    """Check NLTK availability and status"""
    try:
        import nltk
        
        # Try to use NLTK
        try:
            from nltk.sentiment import SentimentIntensityAnalyzer
            analyzer = SentimentIntensityAnalyzer()
            test_result = analyzer.polarity_scores("This is a test sentence.")
            nltk_working = True
            nltk_error = None
        except Exception as e:
            nltk_working = False
            nltk_error = str(e)
        
        return {
            'status': 'success',
            'nltk_available': True,
            'nltk_working': nltk_working,
            'nltk_version': nltk.__version__,
            'error': nltk_error,
            'test_result': test_result if nltk_working else None
        }
        
    except ImportError:
        return {
            'status': 'success',
            'nltk_available': False,
            'message': 'NLTK not installed - using fallback methods'
        }

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting AI-Powered Text Analysis Platform Backend")
    print("=" * 60)
    print(f"📍 URL: http://localhost:8001")
    print(f"📚 API Docs: http://localhost:8001/docs")
    print(f"🔍 Health Check: http://localhost:8001/health")
    print(f"🧪 Analysis Test: http://localhost:8001/api/analysis/test")
    print(f"☁️  Word Cloud API: http://localhost:8001/api/wordcloud/generate")
    print("=" * 60)
    print("Note: Using port 8001 instead of 8000 to avoid conflicts")
    print("Update frontend NEXT_PUBLIC_API_URL to http://localhost:8001")
    
    try:
        uvicorn.run(
            "working_server:app",
            host="0.0.0.0",
            port=8001,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server failed: {e}")
        import traceback
        traceback.print_exc()
