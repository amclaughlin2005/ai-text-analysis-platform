"""
Optimized Word Cloud Service for high-performance text analysis
Provides caching, batching, and optimized database queries for large datasets
"""

import logging
import asyncio
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
from sqlalchemy.orm import Session
from sqlalchemy import text
import re
import json
import time
from concurrent.futures import ThreadPoolExecutor
import threading

from ..core.database import get_db
from .text_validation_service import TextValidationService

logger = logging.getLogger(__name__)

class WordCloudCache:
    """Simple in-memory cache for word cloud results"""
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        self._cache = {}
        self._timestamps = {}
        self._lock = threading.RLock()
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
    
    def _generate_key(self, dataset_id: str, analysis_mode: str, limit: int, exclude_words: List[str]) -> str:
        """Generate cache key from parameters"""
        key_data = {
            'dataset_id': dataset_id,
            'mode': analysis_mode,
            'limit': limit,
            'exclude': sorted(exclude_words or [])
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, dataset_id: str, analysis_mode: str, limit: int, exclude_words: List[str]) -> Optional[Dict]:
        """Get cached result if available and not expired"""
        key = self._generate_key(dataset_id, analysis_mode, limit, exclude_words)
        
        with self._lock:
            if key not in self._cache:
                return None
            
            # Check TTL
            if time.time() - self._timestamps[key] > self.ttl_seconds:
                del self._cache[key]
                del self._timestamps[key]
                return None
            
            logger.info(f"🎯 Cache HIT for dataset {dataset_id}")
            return self._cache[key]
    
    def set(self, dataset_id: str, analysis_mode: str, limit: int, exclude_words: List[str], result: Dict):
        """Cache the result"""
        key = self._generate_key(dataset_id, analysis_mode, limit, exclude_words)
        
        with self._lock:
            # Evict oldest entries if cache is full
            if len(self._cache) >= self.max_size:
                oldest_key = min(self._timestamps.keys(), key=lambda k: self._timestamps[k])
                del self._cache[oldest_key]
                del self._timestamps[oldest_key]
            
            self._cache[key] = result
            self._timestamps[key] = time.time()
            logger.info(f"💾 Cached result for dataset {dataset_id}")
    
    def invalidate(self, dataset_id: str = None):
        """Invalidate cache entries for a dataset or all entries"""
        with self._lock:
            if dataset_id:
                # Remove entries containing this dataset_id
                keys_to_remove = []
                for key in self._cache:
                    try:
                        # Try to extract dataset_id from key
                        if dataset_id in str(self._cache[key].get('dataset_id', '')):
                            keys_to_remove.append(key)
                    except:
                        pass
                
                for key in keys_to_remove:
                    if key in self._cache:
                        del self._cache[key]
                    if key in self._timestamps:
                        del self._timestamps[key]
                
                logger.info(f"🗑️ Invalidated cache for dataset {dataset_id}")
            else:
                self._cache.clear()
                self._timestamps.clear()
                logger.info("🗑️ Invalidated entire cache")

# Global cache instance
word_cloud_cache = WordCloudCache()

class OptimizedWordCloudService:
    """High-performance word cloud generation service"""
    
    @staticmethod
    async def generate_word_cloud(
        db: Session,
        dataset_id: str,
        analysis_mode: str = "all",
        limit: int = 50,
        exclude_words: Optional[List[str]] = None,
        selected_columns: Optional[List[int]] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Generate word cloud with optimizations for large datasets
        
        Args:
            db: Database session
            dataset_id: Dataset identifier
            analysis_mode: Type of analysis (all, verbs, emotions, etc.)
            limit: Maximum number of words to return
            exclude_words: Additional words to exclude
            selected_columns: Which columns to analyze (future use)
            use_cache: Whether to use caching
            
        Returns:
            Word cloud data dictionary
        """
        start_time = time.time()
        exclude_words = exclude_words or []
        
        # Check cache first
        if use_cache:
            cached_result = word_cloud_cache.get(dataset_id, analysis_mode, limit, exclude_words)
            if cached_result:
                cached_result['cache_hit'] = True
                cached_result['generation_time'] = time.time() - start_time
                return cached_result
        
        logger.info(f"🎨 Generating word cloud for dataset {dataset_id} with mode {analysis_mode}")
        
        try:
            # Step 1: Verify dataset exists (fast query)
            dataset_exists = await OptimizedWordCloudService._verify_dataset_exists(db, dataset_id)
            if not dataset_exists:
                raise ValueError("Dataset not found")
            
            # Step 2: Get optimized text data
            text_data, tenant_info, total_questions = await OptimizedWordCloudService._get_optimized_text_data(
                db, dataset_id
            )
            
            if not text_data:
                result = {
                    "dataset_id": dataset_id,
                    "analysis_mode": analysis_mode,
                    "words": [],
                    "word_count": 0,
                    "total_questions": 0,
                    "message": "No questions found in dataset",
                    "generation_time": time.time() - start_time,
                    "cache_hit": False
                }
                return result
            
            # Step 3: Process text in parallel for better performance
            word_counts = await OptimizedWordCloudService._process_text_parallel(
                text_data, analysis_mode, tenant_info, exclude_words
            )
            
            # Step 4: Generate final word cloud data
            word_cloud_data = OptimizedWordCloudService._generate_word_cloud_data(
                word_counts, analysis_mode, limit
            )
            
            # Step 5: Final validation (optimized)
            word_cloud_data = TextValidationService.validate_word_list(
                word_cloud_data,
                tenant_info=tenant_info,
                additional_blacklist=exclude_words
            )
            
            generation_time = time.time() - start_time
            
            result = {
                "dataset_id": dataset_id,
                "analysis_mode": analysis_mode,
                "words": word_cloud_data,
                "word_count": len(word_cloud_data),
                "total_questions": total_questions,
                "success": True,
                "generation_time": generation_time,
                "cache_hit": False
            }
            
            # Cache the result
            if use_cache:
                word_cloud_cache.set(dataset_id, analysis_mode, limit, exclude_words, result)
            
            logger.info(f"✅ Generated word cloud with {len(word_cloud_data)} words in {generation_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Word cloud generation failed for dataset {dataset_id}: {e}")
            raise
    
    @staticmethod
    async def _verify_dataset_exists(db: Session, dataset_id: str) -> bool:
        """Fast dataset existence check"""
        try:
            dataset_sql = text("SELECT 1 FROM datasets WHERE id = :dataset_id LIMIT 1")
            result = db.execute(dataset_sql, {"dataset_id": dataset_id}).fetchone()
            return result is not None
        except Exception as e:
            logger.error(f"Error verifying dataset {dataset_id}: {e}")
            return False
    
    @staticmethod
    async def _get_optimized_text_data(db: Session, dataset_id: str) -> Tuple[str, Dict, int]:
        """
        Get text data with optimized database query
        Uses streaming and batching for large datasets
        """
        try:
            # Get total count first for progress tracking
            count_sql = text("SELECT COUNT(*) FROM questions WHERE dataset_id = :dataset_id")
            total_questions = db.execute(count_sql, {"dataset_id": dataset_id}).scalar() or 0
            
            if total_questions == 0:
                return "", {}, 0
            
            logger.info(f"📊 Processing {total_questions} questions from dataset {dataset_id}")
            
            # For very large datasets, use chunked processing
            if total_questions > 10000:
                return await OptimizedWordCloudService._get_chunked_text_data(db, dataset_id, total_questions)
            else:
                return await OptimizedWordCloudService._get_text_data_batch(db, dataset_id, total_questions)
                
        except Exception as e:
            logger.error(f"Error getting text data for dataset {dataset_id}: {e}")
            return "", {}, 0
    
    @staticmethod
    async def _get_text_data_batch(db: Session, dataset_id: str, total_questions: int) -> Tuple[str, Dict, int]:
        """Get text data in single batch for smaller datasets"""
        try:
            # Optimized query - only get what we need
            questions_sql = text("""
                SELECT original_question, ai_response 
                FROM questions 
                WHERE dataset_id = :dataset_id 
                AND (original_question IS NOT NULL OR ai_response IS NOT NULL)
            """)
            
            questions_result = db.execute(questions_sql, {"dataset_id": dataset_id}).fetchall()
            
            # Build text efficiently
            text_parts = []
            tenant_info = {}
            
            for row in questions_result:
                if row.original_question:
                    text_parts.append(str(row.original_question))
                if row.ai_response:
                    text_parts.append(str(row.ai_response))
            
            all_text = " ".join(text_parts)
            
            return all_text, tenant_info, total_questions
            
        except Exception as e:
            logger.error(f"Error in batch text processing: {e}")
            return "", {}, 0
    
    @staticmethod
    async def _get_chunked_text_data(db: Session, dataset_id: str, total_questions: int) -> Tuple[str, Dict, int]:
        """Get text data in chunks for very large datasets"""
        try:
            chunk_size = 5000  # Process 5000 records at a time
            text_parts = []
            tenant_info = {}
            
            for offset in range(0, total_questions, chunk_size):
                logger.info(f"📦 Processing chunk {offset//chunk_size + 1}/{(total_questions//chunk_size) + 1}")
                
                chunk_sql = text("""
                    SELECT original_question, ai_response 
                    FROM questions 
                    WHERE dataset_id = :dataset_id 
                    AND (original_question IS NOT NULL OR ai_response IS NOT NULL)
                    LIMIT :limit OFFSET :offset
                """)
                
                chunk_result = db.execute(chunk_sql, {
                    "dataset_id": dataset_id,
                    "limit": chunk_size,
                    "offset": offset
                }).fetchall()
                
                for row in chunk_result:
                    if row.original_question:
                        text_parts.append(str(row.original_question))
                    if row.ai_response:
                        text_parts.append(str(row.ai_response))
                
                # Yield control to allow other async operations
                await asyncio.sleep(0.01)
            
            all_text = " ".join(text_parts)
            
            return all_text, tenant_info, total_questions
            
        except Exception as e:
            logger.error(f"Error in chunked text processing: {e}")
            return "", {}, 0
    
    @staticmethod
    async def _process_text_parallel(
        text_data: str, 
        analysis_mode: str, 
        tenant_info: Dict, 
        exclude_words: List[str]
    ) -> Counter:
        """Process text using parallel processing for better performance"""
        
        # Clean text first
        cleaned_text = TextValidationService.clean_text_for_analysis(
            text_data, 
            tenant_info=tenant_info,
            additional_blacklist=exclude_words
        )
        
        # For very large text, split processing
        if len(cleaned_text) > 1000000:  # 1MB of text
            return await OptimizedWordCloudService._process_large_text_parallel(cleaned_text, analysis_mode)
        else:
            return OptimizedWordCloudService._process_text_mode(cleaned_text, analysis_mode)
    
    @staticmethod
    async def _process_large_text_parallel(text: str, analysis_mode: str) -> Counter:
        """Process very large text using thread pool for CPU-intensive work"""
        
        # Split text into chunks for parallel processing
        chunk_size = len(text) // 4  # 4 chunks
        if chunk_size < 10000:
            chunk_size = 10000
        
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            # Ensure we don't cut words in half
            if i + chunk_size < len(text):
                last_space = chunk.rfind(' ')
                if last_space > chunk_size * 0.8:  # If space is reasonably close to end
                    chunk = chunk[:last_space]
            chunks.append(chunk)
        
        # Process chunks in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(
                    executor, 
                    OptimizedWordCloudService._process_text_mode, 
                    chunk, 
                    analysis_mode
                )
                for chunk in chunks
            ]
            
            chunk_results = await asyncio.gather(*tasks)
        
        # Combine results
        combined_counter = Counter()
        for counter in chunk_results:
            combined_counter.update(counter)
        
        return combined_counter
    
    @staticmethod
    def _process_text_mode(text: str, analysis_mode: str) -> Counter:
        """Process text based on analysis mode - optimized for speed"""
        
        if analysis_mode == "all":
            # Simple and fast - already cleaned by TextValidationService
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            return Counter(words)
            
        elif analysis_mode == "action" or analysis_mode == "verbs":
            # Optimized verb detection with compiled regex
            verb_pattern = re.compile(r'\b\w*(?:ing|ed|ize|ise|ate|ify)\b|\b(?:make|take|give|get|go|come|know|think|see|look|use|find|tell|ask|work|seem|feel|try|leave|call|move|live|believe|hold|bring|happen|write|sit|stand|lose|pay|meet|include|continue|set|learn|change|lead|understand|watch|follow|stop|create|speak|read|allow|add|spend|grow|open|walk|win|offer|remember|love|consider|appear|buy|wait|serve|die|send|expect|build|stay|fall|cut|reach|kill|remain)\b')
            words = verb_pattern.findall(text.lower())
            return Counter(words)
            
        elif analysis_mode == "emotions":
            # Optimized emotion word detection
            emotion_pattern = re.compile(r'\b(?:happy|sad|angry|excited|frustrated|pleased|disappointed|worried|confident|nervous|proud|ashamed|grateful|jealous|hopeful|fearful|surprised|shocked|calm|stressed|relaxed|anxious|joyful|depressed|elated|furious|content|miserable|ecstatic|livid|serene|panicked|love|hate|like|dislike|enjoy|despise|adore|loathe|appreciate|detest|cherish|abhor|positive|negative|good|bad|excellent|terrible|amazing|awful|great|poor|best|worst|better|worse|success|failure|win|lose|triumph|defeat|victory|loss)\b')
            words = emotion_pattern.findall(text.lower())
            return Counter(words)
            
        elif analysis_mode == "themes":
            # Optimized theme detection
            theme_pattern = re.compile(r'\b(?:business|technology|education|health|finance|legal|marketing|management|development|research|analysis|strategy|innovation|communication|leadership|quality|performance|customer|service|support|solution|problem|success|growth|security|compliance|process|system|project|work|team|data|information|experience|training|professional)\b')
            words = theme_pattern.findall(text.lower())
            return Counter(words)
            
        elif analysis_mode == "topics":
            # Optimized topic detection
            topic_pattern = re.compile(r'\b(?:artificial|intelligence|machine|learning|technology|software|development|research|analysis|data|business|strategy|security|automation|innovation|design|testing|deployment|monitoring|support|training|performance|quality|management|framework|methodology)\b')
            words = topic_pattern.findall(text.lower())
            return Counter(words)
            
        elif analysis_mode == "entities":
            # Simple entity detection (capitalized words)
            words = re.findall(r'\b[A-Z][a-z]+\b', text)
            return Counter(word.lower() for word in words)
            
        else:
            # Default to all words
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            return Counter(words)
    
    @staticmethod
    def _generate_word_cloud_data(word_counts: Counter, analysis_mode: str, limit: int) -> List[Dict[str, Any]]:
        """Generate final word cloud data structure"""
        word_cloud_data = []
        
        for word, count in word_counts.most_common(limit):
            # Assign sentiment based on analysis mode
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
        
        return word_cloud_data
    
    @staticmethod
    def _get_word_sentiment(word: str, analysis_mode: str) -> str:
        """Fast sentiment assignment based on analysis mode"""
        if analysis_mode == "emotions":
            if word in {'happy', 'pleased', 'satisfied', 'excited', 'positive', 'good', 'excellent', 'amazing', 'great', 'best', 'better', 'success'}:
                return "positive"
            elif word in {'angry', 'sad', 'frustrated', 'worried', 'disappointed', 'shocked', 'negative', 'bad', 'terrible', 'awful', 'poor', 'worst', 'worse', 'problem', 'failure', 'mistake', 'error'}:
                return "negative"
            else:
                return "neutral"
        elif analysis_mode in ("action", "verbs"):
            return "action"
        elif analysis_mode == "entities":
            return "entity"
        elif analysis_mode == "themes":
            return "theme"
        elif analysis_mode == "topics":
            return "topic"
        else:
            return "neutral"
    
    @staticmethod
    def invalidate_cache(dataset_id: str = None):
        """Invalidate cache for a specific dataset or all datasets"""
        word_cloud_cache.invalidate(dataset_id)
