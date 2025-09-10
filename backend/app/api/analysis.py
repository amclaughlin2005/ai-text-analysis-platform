"""
NLTK Analysis API endpoints
Provides sentiment analysis, topic modeling, entity extraction, and classification
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from ..core.database import get_db
from ..core.logging import get_logger

logger = get_logger(__name__)

# Import analysis modules with error handling for missing dependencies
try:
    from ..analysis.nltk_processor import get_nltk_processor
    NLTK_AVAILABLE = True
except ImportError as e:
    logger.warning(f"NLTK processor not available: {e}")
    NLTK_AVAILABLE = False
    get_nltk_processor = None

try:
    from ..analysis.llm_processor import get_llm_processor
    LLM_AVAILABLE = True
except ImportError as e:
    logger.warning(f"LLM processor not available: {e}")
    LLM_AVAILABLE = False
    get_llm_processor = None

try:
    from ..tasks.analysis_tasks import test_nltk_processing, analyze_sentiment_batch
    TASKS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Analysis tasks not available: {e}")
    TASKS_AVAILABLE = False
    test_nltk_processing = None
    analyze_sentiment_batch = None
router = APIRouter()

# Request/Response models
class TextAnalysisRequest(BaseModel):
    text: str
    include_entities: bool = True
    include_keywords: bool = True
    include_readability: bool = True

class BatchAnalysisRequest(BaseModel):
    texts: List[str]
    include_topics: bool = True
    include_entities: bool = True

class SentimentAnalysisResponse(BaseModel):
    compound_score: float
    positive: float
    negative: float
    neutral: float
    label: str
    confidence: float

class EntityExtractionResponse(BaseModel):
    persons: List[str]
    organizations: List[str]
    locations: List[str]
    misc: List[str]

# Test endpoints (working immediately)
@router.get("/test")
async def test_analysis_engine():
    """Test the analysis engine functionality"""
    if not NLTK_AVAILABLE:
        return {"status": "warning", "message": "NLTK processor not available - some dependencies missing"}
    
    try:
        processor = get_nltk_processor()
        
        # Test with sample text
        test_text = "I am very happy with the excellent customer service provided by your team!"
        
        results = {
            'sentiment': processor.sentiment_analysis(test_text),
            'entities': processor.entity_extraction(test_text),
            'keywords': processor.keyword_extraction(test_text, method='tfidf'),
            'readability': processor.readability_analysis(test_text),
            'classification': processor.question_classification(test_text)
        }
        
        return {
            'status': 'success',
            'message': 'Analysis engine is working correctly',
            'test_results': results
        }
        
    except Exception as e:
        logger.error(f"Analysis engine test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis engine test failed: {str(e)}")

@router.post("/sentiment", response_model=Dict[str, Any])
async def analyze_sentiment(request: TextAnalysisRequest):
    """Analyze sentiment of provided text"""
    try:
        processor = get_nltk_processor()
        result = processor.sentiment_analysis(request.text)
        
        return {
            'status': 'success',
            'data': result
        }
        
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")

@router.post("/entities")
async def extract_entities(request: TextAnalysisRequest):
    """Extract named entities from provided text"""
    try:
        processor = get_nltk_processor()
        entities = processor.entity_extraction(request.text)
        
        return {
            'status': 'success',
            'data': entities
        }
        
    except Exception as e:
        logger.error(f"Entity extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Entity extraction failed: {str(e)}")

@router.post("/keywords")
async def extract_keywords(request: TextAnalysisRequest):
    """Extract keywords from provided text"""
    try:
        processor = get_nltk_processor()
        keywords = processor.keyword_extraction(request.text, method='all')
        
        return {
            'status': 'success',
            'data': keywords
        }
        
    except Exception as e:
        logger.error(f"Keyword extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Keyword extraction failed: {str(e)}")

@router.post("/classification")
async def classify_question(request: TextAnalysisRequest):
    """Classify question type and intent"""
    try:
        processor = get_nltk_processor()
        classification = processor.question_classification(request.text)
        
        return {
            'status': 'success',
            'data': classification
        }
        
    except Exception as e:
        logger.error(f"Question classification failed: {e}")
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

@router.post("/batch")
async def analyze_batch(request: BatchAnalysisRequest):
    """Batch analysis of multiple texts"""
    try:
        processor = get_nltk_processor()
        
        # Limit batch size for safety
        if len(request.texts) > 100:
            raise HTTPException(status_code=400, detail="Batch size limited to 100 texts")
        
        results = processor.analyze_batch(request.texts, include_topics=request.include_topics)
        summary = processor.get_analysis_summary(results)
        
        return {
            'status': 'success',
            'data': {
                'detailed_results': results,
                'summary': summary
            }
        }
        
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

@router.post("/topics")
async def analyze_topics(request: BatchAnalysisRequest):
    """Topic modeling analysis"""
    try:
        processor = get_nltk_processor()
        
        if len(request.texts) < 2:
            raise HTTPException(status_code=400, detail="Topic modeling requires at least 2 texts")
        
        topics = processor.topic_modeling(request.texts, num_topics=5)
        
        return {
            'status': 'success',
            'data': topics
        }
        
    except Exception as e:
        logger.error(f"Topic modeling failed: {e}")
        raise HTTPException(status_code=500, detail=f"Topic modeling failed: {str(e)}")

@router.post("/similarity")
async def analyze_similarity(text1: str, text2: str):
    """Analyze similarity between two texts"""
    try:
        processor = get_nltk_processor()
        similarity = processor.text_similarity(text1, text2, method='all')
        
        return {
            'status': 'success',
            'data': similarity
        }
        
    except Exception as e:
        logger.error(f"Similarity analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Similarity analysis failed: {str(e)}")

# Background job endpoints
@router.post("/jobs/test-nltk")
async def start_nltk_test(background_tasks: BackgroundTasks):
    """Start background test of NLTK processing"""
    try:
        task = test_nltk_processing.delay()
        
        return {
            'status': 'started',
            'task_id': task.id,
            'message': 'NLTK test job started'
        }
        
    except Exception as e:
        logger.error(f"Failed to start NLTK test: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start test: {str(e)}")

@router.get("/jobs/{task_id}")
async def get_task_status(task_id: str):
    """Get status of a background analysis task"""
    try:
        from celery_config import celery_app
        
        task_result = celery_app.AsyncResult(task_id)
        
        if task_result.state == 'PENDING':
            response = {
                'state': task_result.state,
                'status': 'Task is waiting to be processed'
            }
        elif task_result.state == 'PROGRESS':
            response = {
                'state': task_result.state,
                'current': task_result.info.get('current', 0),
                'total': task_result.info.get('total', 1),
                'status': task_result.info.get('status', 'Processing...')
            }
        elif task_result.state == 'SUCCESS':
            response = {
                'state': task_result.state,
                'result': task_result.result
            }
        else:  # FAILURE
            response = {
                'state': task_result.state,
                'error': str(task_result.info)
            }
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to get task status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")
