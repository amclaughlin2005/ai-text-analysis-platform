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
from ..services.text_validation_service import TextValidationService
from ..services.wordcloud_service import OptimizedWordCloudService

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

class MultiWordCloudRequest(BaseModel):
    dataset_ids: List[str]
    mode: str = "all"
    analysis_mode: Optional[str] = None  # Alternative name
    max_words: int = 50
    limit: Optional[int] = None  # Alternative name
    selected_columns: Optional[List[int]] = None
    exclude_words: Optional[List[str]] = None
    filters: Optional[dict] = None

# Word cloud generation endpoints
@router.post("/generate-fast")
async def generate_wordcloud_optimized(
    request: WordCloudRequest,
    db: Session = Depends(get_db)
):
    """Generate word cloud data using optimized service for better performance"""
    try:
        # Extract parameters from request
        dataset_id = request.dataset_id
        analysis_mode = request.analysis_mode or request.mode
        limit = request.limit or request.max_words
        exclude_words = request.exclude_words or []
        selected_columns = request.selected_columns
        
        # Use optimized service
        result = await OptimizedWordCloudService.generate_word_cloud(
            db=db,
            dataset_id=dataset_id,
            analysis_mode=analysis_mode,
            limit=limit,
            exclude_words=exclude_words,
            selected_columns=selected_columns,
            use_cache=True
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Optimized word cloud generation failed for dataset {request.dataset_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Word cloud generation failed: {str(e)}"
        )

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
        tenant_info = {}
        
        for row in questions_result:
            # Extract tenant information for filtering (if available)
            # Note: This would need to be adapted based on your actual schema
            # For now, we'll extract it from the first record if available
            if not tenant_info and hasattr(row, 'tenant_name'):
                tenant_info = {
                    'tenant_name': getattr(row, 'tenant_name', None),
                    'org_name': getattr(row, 'org_name', None),
                    'organization': getattr(row, 'organization', None)
                }
            
            if row.original_question:
                all_text += " " + str(row.original_question)
            if row.ai_response:
                all_text += " " + str(row.ai_response)
        
        # Clean the text using validation service
        all_text = TextValidationService.clean_text_for_analysis(
            all_text, 
            tenant_info=tenant_info,
            additional_blacklist=exclude_words
        )
        
        # Different analysis modes
        if analysis_mode == "all":
            # Basic text processing for all words (text already cleaned by TextValidationService)
            words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
            word_counts = Counter(words)
            
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
        
        # Final validation of word list to remove any remaining noise
        word_cloud_data = TextValidationService.validate_word_list(
            word_cloud_data,
            tenant_info=tenant_info,
            additional_blacklist=exclude_words
        )
        
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

@router.post("/generate-multi")
async def generate_multi_wordcloud(
    request: MultiWordCloudRequest,
    db: Session = Depends(get_db)
):
    """Generate word cloud data from multiple datasets combined"""
    try:
        from sqlalchemy import text
        from collections import Counter
        import re
        
        # Extract parameters from request
        dataset_ids = request.dataset_ids
        analysis_mode = request.analysis_mode or request.mode
        limit = request.limit or request.max_words
        exclude_words = request.exclude_words or []
        
        logger.info(f"🎨 Generating multi-dataset word cloud for {len(dataset_ids)} datasets with mode {analysis_mode}")
        
        if not dataset_ids:
            raise HTTPException(status_code=400, detail="No dataset IDs provided")
        
        # Verify all datasets exist and collect questions
        all_questions = []
        valid_datasets = []
        
        for dataset_id in dataset_ids:
            dataset_sql = text("SELECT name FROM datasets WHERE id = :dataset_id")
            dataset_result = db.execute(dataset_sql, {"dataset_id": dataset_id}).fetchone()
            
            if dataset_result:
                valid_datasets.append(dataset_id)
                # Get questions from this dataset
                questions_sql = text("SELECT original_question, ai_response FROM questions WHERE dataset_id = :dataset_id")
                questions_result = db.execute(questions_sql, {"dataset_id": dataset_id}).fetchall()
                all_questions.extend(questions_result)
                logger.info(f"Dataset {dataset_id}: {len(questions_result)} questions")
            else:
                logger.warning(f"Dataset {dataset_id} not found, skipping")
        
        if not valid_datasets:
            raise HTTPException(status_code=404, detail="No valid datasets found")
        
        if not all_questions:
            logger.warning(f"No questions found across {len(valid_datasets)} datasets")
            return {
                "dataset_ids": valid_datasets,
                "analysis_mode": analysis_mode,
                "words": [],
                "word_count": 0,
                "message": f"No questions found across {len(valid_datasets)} datasets"
            }
        
        # Extract text from all questions and answers
        all_text = ""
        tenant_info = {}
        
        for row in all_questions:
            # Extract tenant information for filtering (if available)
            if not tenant_info and hasattr(row, 'tenant_name'):
                tenant_info = {
                    'tenant_name': getattr(row, 'tenant_name', None),
                    'org_name': getattr(row, 'org_name', None),
                    'organization': getattr(row, 'organization', None)
                }
            
            if row.original_question:
                all_text += " " + str(row.original_question)
            if row.ai_response:
                all_text += " " + str(row.ai_response)
        
        # Clean the text using validation service
        all_text = TextValidationService.clean_text_for_analysis(
            all_text, 
            tenant_info=tenant_info,
            additional_blacklist=exclude_words
        )
        
        # Use the same word analysis logic as single dataset
        # Different analysis modes
        if analysis_mode == "all":
            # Get all significant words
            words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
        elif analysis_mode == "action" or analysis_mode == "verbs":
            # Simple verb detection (words ending in common verb patterns)
            words = re.findall(r'\b\w*(?:ing|ed|ize|ise|ate|ify)\b|\b(?:make|take|give|get|go|come|know|think|see|look|use|find|tell|ask|work|seem|feel|try|leave|call|move|live|believe|hold|bring|happen|write|sit|stand|lose|pay|meet|include|continue|set|learn|change|lead|understand|watch|follow|stop|create|speak|read|allow|add|spend|grow|open|walk|win|offer|remember|love|consider|appear|buy|wait|serve|die|send|expect|build|stay|fall|cut|reach|kill|remain)\b', all_text.lower())
        elif analysis_mode == "entities":
            # Simple entity detection (capitalized words)
            words = re.findall(r'\b[A-Z][a-z]+\b', all_text)
        elif analysis_mode == "emotions":
            # Emotion-related words
            emotion_words = r'\b(?:happy|sad|angry|excited|frustrated|pleased|disappointed|worried|confident|nervous|proud|ashamed|grateful|jealous|hopeful|fearful|surprised|shocked|calm|stressed|relaxed|anxious|joyful|depressed|elated|furious|content|miserable|ecstatic|livid|serene|panicked|love|hate|like|dislike|enjoy|despise|adore|loathe|appreciate|detest|cherish|abhor|positive|negative|good|bad|excellent|terrible|amazing|awful|great|poor|best|worst|better|worse|success|failure|win|lose|triumph|defeat|victory|loss)\b'
            words = re.findall(emotion_words, all_text.lower())
        elif analysis_mode == "themes":
            # Common themes (simpler pattern)
            theme_words = r'\b(?:business|technology|education|health|finance|legal|marketing|management|development|research|analysis|strategy|innovation|communication|leadership|quality|performance|customer|service|support|solution|problem|success|growth|security|compliance|process|system|project|work|team|data|information|experience|training|professional)\b'
            words = re.findall(theme_words, all_text.lower())
        elif analysis_mode == "topics":
            # Topic modeling simulation (simpler pattern)
            topic_words = r'\b(?:artificial|intelligence|machine|learning|technology|software|development|research|analysis|data|business|strategy|security|automation|innovation|design|testing|deployment|monitoring|support|training|performance|quality|management|framework|methodology)\b'
            words = re.findall(topic_words, all_text.lower())
        else:
            # Default to all words
            words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
        
        # Default exclude words list including user's memory preference
        default_exclude = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 
            'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 
            'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 
            'too', 'use', 'that', 'with', 'have', 'this', 'will', 'your', 'from', 'they', 'know', 
            'want', 'been', 'good', 'much', 'some', 'time', 'very', 'when', 'come', 'here', 'just', 
            'like', 'long', 'make', 'many', 'over', 'such', 'take', 'than', 'them', 'well', 'were',
            'details', 'page', 'https', 'filevineapp', 'docviewer', 'view', 'source', 'embedding'  # User's preference
        }
        
        # Combine with user-provided exclude words
        all_exclude = default_exclude.union(set(exclude_words))
        
        # Filter and count words
        filtered_words = [word for word in words if word.lower() not in all_exclude and len(word) >= 3]
        word_counts = Counter(filtered_words)
        
        # Generate word cloud data with sentiment assignment
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
        
        # Final validation of word list to remove any remaining noise
        word_cloud_data = TextValidationService.validate_word_list(
            word_cloud_data,
            tenant_info=tenant_info,
            additional_blacklist=exclude_words
        )
        
        logger.info(f"✅ Generated multi-dataset word cloud with {len(word_cloud_data)} words from {len(valid_datasets)} datasets")
        
        return {
            "dataset_ids": valid_datasets,
            "analysis_mode": analysis_mode,
            "words": word_cloud_data,
            "word_count": len(word_cloud_data),
            "total_questions": len(all_questions),
            "datasets_processed": len(valid_datasets),
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Multi-dataset word cloud generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Multi-dataset word cloud generation failed: {str(e)}"
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

@router.post("/invalidate-cache")
async def invalidate_cache(dataset_id: Optional[str] = None):
    """Invalidate word cloud cache for a dataset or all datasets"""
    try:
        OptimizedWordCloudService.invalidate_cache(dataset_id)
        if dataset_id:
            return {"message": f"Cache invalidated for dataset {dataset_id}", "success": True}
        else:
            return {"message": "All cache entries invalidated", "success": True}
    except Exception as e:
        logger.error(f"❌ Cache invalidation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Cache invalidation failed: {str(e)}"
        )

@router.post("/generate-multi-fast")
async def generate_multi_wordcloud_optimized(
    request: MultiWordCloudRequest,
    db: Session = Depends(get_db)
):
    """Generate multi-dataset word cloud using optimized service"""
    try:
        # Extract parameters from request
        dataset_ids = request.dataset_ids
        analysis_mode = request.analysis_mode or request.mode
        limit = request.limit or request.max_words
        exclude_words = request.exclude_words or []
        
        if not dataset_ids:
            raise HTTPException(status_code=400, detail="No dataset IDs provided")
        
        logger.info(f"🎨 Generating optimized multi-dataset word cloud for {len(dataset_ids)} datasets")
        
        # Process each dataset and combine results
        all_word_counts = Counter()
        total_questions = 0
        valid_datasets = []
        
        for dataset_id in dataset_ids:
            try:
                result = await OptimizedWordCloudService.generate_word_cloud(
                    db=db,
                    dataset_id=dataset_id,
                    analysis_mode=analysis_mode,
                    limit=1000,  # Get more words for combining
                    exclude_words=exclude_words,
                    use_cache=True
                )
                
                if result['success'] and result['words']:
                    valid_datasets.append(dataset_id)
                    total_questions += result.get('total_questions', 0)
                    
                    # Combine word counts
                    for word_data in result['words']:
                        word = word_data['word']
                        frequency = word_data['frequency']
                        all_word_counts[word] += frequency
                        
            except Exception as e:
                logger.warning(f"Failed to process dataset {dataset_id}: {e}")
                continue
        
        if not valid_datasets:
            raise HTTPException(status_code=404, detail="No valid datasets found")
        
        # Generate final combined word cloud data
        word_cloud_data = []
        for word, count in all_word_counts.most_common(limit):
            sentiment = OptimizedWordCloudService._get_word_sentiment(word, analysis_mode)
            
            word_cloud_data.append({
                "text": word,
                "word": word,
                "value": count,
                "weight": count,
                "frequency": count,
                "sentiment": sentiment,
                "category": analysis_mode
            })
        
        return {
            "dataset_ids": valid_datasets,
            "analysis_mode": analysis_mode,
            "words": word_cloud_data,
            "word_count": len(word_cloud_data),
            "total_questions": total_questions,
            "datasets_processed": len(valid_datasets),
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Optimized multi-dataset word cloud generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Multi-dataset word cloud generation failed: {str(e)}"
        )
