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
        
        # Get questions from dataset (using correct Railway column names)
        questions_sql = text("SELECT original_question, ai_response FROM questions WHERE dataset_id = :dataset_id")
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
            if row.original_question:
                all_text += " " + str(row.original_question)
            if row.ai_response:
                all_text += " " + str(row.ai_response)
        
        # Different analysis modes
        if analysis_mode == "all":
            # Basic text processing for all words
            excluded_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
                'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
                'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can',
                'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
                'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'our', 'their',
                'details', 'page', 'https', 'filevineapp', 'docviewer', 'view', 'source', 'embedding'
            }
            
            if exclude_words:
                excluded_words.update(word.lower() for word in exclude_words)
            
            words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
            filtered_words = [word for word in words if word not in excluded_words and len(word) >= 3]
            word_counts = Counter(filtered_words)
            
        elif analysis_mode == "action" or analysis_mode == "verbs":
            # Action words - focus on verbs and action-oriented language
            action_words = {
                'see', 'try', 'use', 'find', 'show', 'get', 'make', 'take', 'give', 'work', 'call',
                'tell', 'ask', 'come', 'go', 'know', 'think', 'look', 'want', 'put', 'say', 'need',
                'move', 'run', 'turn', 'start', 'stop', 'help', 'play', 'change', 'open', 'close',
                'build', 'create', 'write', 'read', 'send', 'receive', 'buy', 'sell', 'pay', 'check',
                'test', 'review', 'analyze', 'examine', 'investigate', 'determine', 'establish',
                'provide', 'require', 'request', 'order', 'attach', 'retrieve', 'process', 'handle'
            }
            
            words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
            filtered_words = [word for word in words if word in action_words or word.endswith('ing') or word.endswith('ed')]
            word_counts = Counter(filtered_words)
            
        elif analysis_mode == "emotions":
            # Emotional language and sentiment indicators
            emotion_words = {
                'angry', 'happy', 'sad', 'frustrated', 'excited', 'worried', 'concerned', 'pleased',
                'satisfied', 'disappointed', 'surprised', 'shocked', 'confused', 'clear', 'unclear',
                'certain', 'uncertain', 'confident', 'doubtful', 'positive', 'negative', 'neutral',
                'good', 'bad', 'excellent', 'terrible', 'amazing', 'awful', 'great', 'poor',
                'best', 'worst', 'better', 'worse', 'important', 'critical', 'serious', 'urgent',
                'problem', 'issue', 'concern', 'success', 'failure', 'mistake', 'error'
            }
            
            words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
            filtered_words = [word for word in words if word in emotion_words]
            word_counts = Counter(filtered_words)
            
        elif analysis_mode == "entities":
            # Named entities - people, places, organizations
            # Look for capitalized words and known entity patterns
            entity_patterns = re.findall(r'\b[A-Z][a-zA-Z]{2,}\b', all_text)
            
            # Common entity words in legal context
            legal_entities = {
                'Tesla', 'Court', 'Judge', 'Attorney', 'Plaintiff', 'Defendant', 'NTSB',
                'David', 'Cummings', 'Benavides', 'Cades', 'Singleton', 'Schreiber'
            }
            
            filtered_words = [word.lower() for word in entity_patterns if word in legal_entities or len(word) > 5]
            word_counts = Counter(filtered_words)
            
        elif analysis_mode == "themes":
            # Common themes and topics
            legal_themes = {
                'court', 'trial', 'case', 'evidence', 'testimony', 'deposition', 'witness',
                'expert', 'document', 'transcript', 'exhibit', 'motion', 'order', 'ruling',
                'autopilot', 'vehicle', 'driver', 'crash', 'accident', 'safety', 'system',
                'investigation', 'report', 'study', 'analysis', 'examination', 'review'
            }
            
            words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
            filtered_words = [word for word in words if word in legal_themes]
            word_counts = Counter(filtered_words)
            
        elif analysis_mode == "topics":
            # Topic modeling results - advanced analysis
            topic_words = {
                'technology', 'automation', 'artificial', 'intelligence', 'machine', 'learning',
                'legal', 'judicial', 'regulatory', 'compliance', 'liability', 'responsibility',
                'safety', 'security', 'risk', 'assessment', 'evaluation', 'methodology',
                'procedure', 'protocol', 'standard', 'requirement', 'specification'
            }
            
            words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
            filtered_words = [word for word in words if word in topic_words or len(word) > 8]
            word_counts = Counter(filtered_words)
            
        else:
            # Default to "all" mode
            excluded_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
                'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had'
            }
            words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
            filtered_words = [word for word in words if word not in excluded_words and len(word) >= 3]
            word_counts = Counter(filtered_words)
        
        # Convert to word cloud format expected by frontend with mode-specific sentiment
        word_cloud_data = []
        for word, count in word_counts.most_common(limit):
            # Assign sentiment based on analysis mode and word content
            if analysis_mode == "emotions":
                if word in ['happy', 'pleased', 'satisfied', 'excited', 'positive', 'good', 'excellent', 'amazing', 'great', 'best', 'better', 'success']:
                    sentiment = "positive"
                elif word in ['angry', 'sad', 'frustrated', 'worried', 'disappointed', 'shocked', 'negative', 'bad', 'terrible', 'awful', 'poor', 'worst', 'worse', 'problem', 'failure', 'mistake', 'error']:
                    sentiment = "negative"
                else:
                    sentiment = "neutral"
            elif analysis_mode == "action" or analysis_mode == "verbs":
                sentiment = "action"
            elif analysis_mode == "entities":
                sentiment = "entity"
            elif analysis_mode == "themes":
                sentiment = "theme"
            elif analysis_mode == "topics":
                sentiment = "topic"
            else:
                sentiment = "neutral"
            
            word_cloud_data.append({
                "text": word,  # Keep for compatibility
                "word": word,  # Add frontend expected format
                "value": count,
                "weight": count,
                "frequency": count,  # Add frontend expected format
                "sentiment": sentiment,
                "category": analysis_mode
            })
        
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
