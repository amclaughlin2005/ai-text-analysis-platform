"""
Word Cloud API endpoints
Provides multi-mode word cloud generation and interactive features
"""

from fastapi import APIRouter, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from ..core.database import get_db
from ..core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Request models
class WordCloudRequest(BaseModel):
    dataset_id: str
    mode: str = "all"
    analysis_mode: Optional[str] = None  # Alternative name
    max_words: int = 50
    limit: Optional[int] = None  # Alternative name
    selected_columns: Optional[List[int]] = None
    exclude_words: Optional[List[str]] = None
    filters: Optional[dict] = None

# Word cloud generation endpoints
@router.post("/generate")
async def generate_wordcloud(
    request: WordCloudRequest,
    db: Session = Depends(get_db)
):
    """Generate word cloud data from dataset questions"""
    try:
        from sqlalchemy import text
        from collections import Counter
        import re
        
        # Extract parameters from request
        dataset_id = request.dataset_id
        analysis_mode = request.analysis_mode or request.mode
        limit = request.limit or request.max_words
        exclude_words = request.exclude_words or []
        
        logger.info(f"🎨 Generating word cloud for dataset {dataset_id} with mode {analysis_mode}")
        
        # Verify dataset exists
        dataset_sql = text("SELECT name FROM datasets WHERE id = :dataset_id")
        dataset_result = db.execute(dataset_sql, {"dataset_id": dataset_id}).fetchone()
        
        if not dataset_result:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        # Get questions from dataset
        questions_sql = text("SELECT question_text, answer_text FROM questions WHERE dataset_id = :dataset_id")
        questions_result = db.execute(questions_sql, {"dataset_id": dataset_id}).fetchall()
        
        if not questions_result:
            logger.warning(f"No questions found for dataset {dataset_id}")
            return {
                "dataset_id": dataset_id,
                "analysis_mode": analysis_mode,
                "words": [],
                "word_count": 0,
                "message": "No questions found in dataset"
            }
        
        # Extract text from questions and answers
        all_text = ""
        for row in questions_result:
            if row.question_text:
                all_text += " " + str(row.question_text)
            if row.answer_text:
                all_text += " " + str(row.answer_text)
        
        # Basic text processing
        # Remove common words and punctuation
        excluded_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'our', 'their',
            # User specified exclusions
            'details', 'page', 'https', 'filevineapp', 'docviewer', 'view', 'source', 'embedding'
        }
        
        # Add custom excluded words from request
        if exclude_words:
            excluded_words.update(word.lower() for word in exclude_words)
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
        filtered_words = [word for word in words if word not in excluded_words and len(word) >= 3]
        
        # Count word frequencies
        word_counts = Counter(filtered_words)
        
        # Convert to word cloud format
        word_cloud_data = [
            {
                "text": word,
                "value": count,
                "weight": count
            }
            for word, count in word_counts.most_common(limit)
        ]
        
        logger.info(f"✅ Generated word cloud with {len(word_cloud_data)} words for dataset {dataset_id}")
        
        return {
            "dataset_id": dataset_id,
            "analysis_mode": analysis_mode,
            "words": word_cloud_data,
            "word_count": len(word_cloud_data),
            "total_questions": len(questions_result),
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Word cloud generation failed for dataset {dataset_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Word cloud generation failed: {str(e)}"
        )

@router.post("/interactive")
async def interactive_wordcloud(db: Session = Depends(get_db)):
    """Interactive word cloud exploration"""
    return {"message": "Interactive word cloud endpoint not yet implemented"}

@router.post("/export")
async def export_wordcloud(db: Session = Depends(get_db)):
    """Export word cloud in multiple formats"""
    return {"message": "Word cloud export endpoint not yet implemented"}

@router.get("/modes")
async def get_wordcloud_modes():
    """Get available word cloud analysis modes"""
    return {"modes": ["all", "verbs", "themes", "emotions", "entities", "topics"]}
