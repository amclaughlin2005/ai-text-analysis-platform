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
    async def generate_word_cloud_with_filters(
        db: Session,
        dataset_id: str,
        analysis_mode: str = "all",
        limit: int = 50,
        filters = None,  # WordCloudFilters type
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Generate word cloud with comprehensive filtering support
        
        Args:
            db: Database session
            dataset_id: Dataset identifier
            analysis_mode: Type of analysis (all, verbs, emotions, etc.)
            limit: Maximum number of words to return
            filters: WordCloudFilters object with all filter options
            use_cache: Whether to use caching
            
        Returns:
            Word cloud data dictionary
        """
        start_time = time.time()
        
        # Extract filter parameters
        selected_columns = filters.selected_columns if filters else None
        exclude_words = filters.exclude_words if filters else []
        org_names = filters.org_names if filters else None
        user_emails = filters.user_emails if filters else None
        tenant_names = filters.tenant_names if filters else None
        date_filter = filters.date_filter if filters else None
        include_words = filters.include_words if filters else None
        min_word_length = filters.min_word_length if filters else 3
        max_words = filters.max_words if filters and filters.max_words else limit
        sentiments = filters.sentiments if filters else None
        
        # Generate cache key including all filter parameters
        cache_key_data = {
            'dataset_id': dataset_id,
            'mode': analysis_mode,
            'limit': limit,
            'selected_columns': selected_columns,
            'exclude_words': sorted(exclude_words or []),
            'org_names': sorted(org_names or []),
            'user_emails': sorted(user_emails or []),
            'tenant_names': sorted(tenant_names or []),
            'date_filter': date_filter.dict() if date_filter else None,
            'include_words': sorted(include_words or []),
            'min_word_length': min_word_length,
            'max_words': max_words,
            'sentiments': sorted(sentiments or [])
        }
        
        # Check cache first
        if use_cache:
            cache_key = hashlib.md5(json.dumps(cache_key_data, sort_keys=True).encode()).hexdigest()
            if cache_key in word_cloud_cache._cache:
                cached_result = word_cloud_cache._cache[cache_key]
                if time.time() - word_cloud_cache._timestamps[cache_key] <= word_cloud_cache.ttl_seconds:
                    cached_result = cached_result.copy()
                    cached_result['cache_hit'] = True
                    cached_result['generation_time'] = time.time() - start_time
                    logger.info(f"🎯 Cache HIT for filtered dataset {dataset_id}")
                    return cached_result
        
        logger.info(f"🎨 Generating filtered word cloud for dataset {dataset_id} with mode {analysis_mode}")
        
        try:
            # Step 1: Verify dataset exists
            dataset_exists = await OptimizedWordCloudService._verify_dataset_exists(db, dataset_id)
            if not dataset_exists:
                raise ValueError("Dataset not found")
            
            # Step 2: Get filtered data with all filter criteria
            text_data, tenant_info, total_questions, filtered_count = await OptimizedWordCloudService._get_filtered_text_data(
                db, dataset_id, selected_columns, org_names, user_emails, tenant_names, date_filter
            )
            
            if not text_data:
                result = {
                    "dataset_id": dataset_id,
                    "analysis_mode": analysis_mode,
                    "words": [],
                    "word_count": 0,
                    "total_questions": total_questions,
                    "filtered_count": filtered_count,
                    "message": "No questions found matching filters",
                    "generation_time": time.time() - start_time,
                    "cache_hit": False
                }
                return result
            
            # Step 3: Process text with all filters
            word_counts = await OptimizedWordCloudService._process_text_with_filters(
                text_data, analysis_mode, tenant_info, exclude_words, include_words, min_word_length
            )
            
            # Step 4: Generate word cloud data
            word_cloud_data = OptimizedWordCloudService._generate_word_cloud_data(
                word_counts, analysis_mode, max_words
            )
            
            # Step 5: Apply sentiment filtering if specified
            if sentiments:
                word_cloud_data = [wd for wd in word_cloud_data if wd['sentiment'] in sentiments]
            
            # Step 6: Final validation
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
                "filtered_count": filtered_count,
                "filters_applied": {
                    "columns": selected_columns,
                    "org_names": org_names,
                    "user_emails": user_emails,
                    "tenant_names": tenant_names,
                    "date_filter": date_filter.dict() if date_filter else None,
                    "sentiments": sentiments
                },
                "success": True,
                "generation_time": generation_time,
                "cache_hit": False
            }
            
            # Cache the result
            if use_cache:
                cache_key = hashlib.md5(json.dumps(cache_key_data, sort_keys=True).encode()).hexdigest()
                with word_cloud_cache._lock:
                    if len(word_cloud_cache._cache) >= word_cloud_cache.max_size:
                        oldest_key = min(word_cloud_cache._timestamps.keys(), key=lambda k: word_cloud_cache._timestamps[k])
                        del word_cloud_cache._cache[oldest_key]
                        del word_cloud_cache._timestamps[oldest_key]
                    
                    word_cloud_cache._cache[cache_key] = result
                    word_cloud_cache._timestamps[cache_key] = time.time()
                    logger.info(f"💾 Cached filtered result for dataset {dataset_id}")
            
            logger.info(f"✅ Generated filtered word cloud with {len(word_cloud_data)} words in {generation_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Filtered word cloud generation failed for dataset {dataset_id}: {e}")
            raise
    
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
    async def _get_filtered_text_data(
        db: Session, 
        dataset_id: str, 
        selected_columns: Optional[List[int]] = None,
        org_names: Optional[List[str]] = None,
        user_emails: Optional[List[str]] = None,
        tenant_names: Optional[List[str]] = None,
        date_filter = None
    ) -> Tuple[str, Dict, int, int]:
        """
        Get text data with comprehensive filtering
        Returns: (text_data, tenant_info, total_questions, filtered_count)
        """
        try:
            # Build dynamic query based on filters
            where_conditions = ["dataset_id = :dataset_id"]
            query_params = {"dataset_id": dataset_id}
            
            # Date filtering - using correct field name
            if date_filter:
                if date_filter.exact_date:
                    where_conditions.append("DATE(timestamp_from_csv) = :exact_date")
                    query_params["exact_date"] = date_filter.exact_date
                else:
                    if date_filter.start_date:
                        where_conditions.append("DATE(timestamp_from_csv) >= :start_date")
                        query_params["start_date"] = date_filter.start_date
                    if date_filter.end_date:
                        where_conditions.append("DATE(timestamp_from_csv) <= :end_date")
                        query_params["end_date"] = date_filter.end_date
            
            # Organization filtering - using correct field name
            if org_names:
                org_placeholders = ','.join([f':org_{i}' for i in range(len(org_names))])
                where_conditions.append(f"LOWER(org_name) IN ({org_placeholders})")
                for i, org in enumerate(org_names):
                    query_params[f'org_{i}'] = org.lower()
            
            # Tenant filtering - Note: tenant info may be in org_name or need different approach
            if tenant_names:
                tenant_placeholders = ','.join([f':tenant_{i}' for i in range(len(tenant_names))])
                where_conditions.append(f"LOWER(org_name) IN ({tenant_placeholders})")  # Using org_name as fallback
                for i, tenant in enumerate(tenant_names):
                    query_params[f'tenant_{i}'] = tenant.lower()
            
            # User email filtering - Note: no user_email field in schema, using user_id_from_csv
            if user_emails:
                email_placeholders = ','.join([f':email_{i}' for i in range(len(user_emails))])
                where_conditions.append(f"LOWER(user_id_from_csv) IN ({email_placeholders})")
                for i, email in enumerate(user_emails):
                    query_params[f'email_{i}'] = email.lower()
            
            # Get total count first
            count_sql = text("SELECT COUNT(*) FROM questions WHERE " + " AND ".join(where_conditions))
            total_questions = db.execute(count_sql, query_params).scalar() or 0
            
            # Debug: Check if dataset has any questions at all
            debug_count_sql = text("SELECT COUNT(*) FROM questions WHERE dataset_id = :dataset_id")
            debug_total = db.execute(debug_count_sql, {"dataset_id": dataset_id}).scalar() or 0
            logger.info(f"🔍 Debug: Dataset {dataset_id} has {debug_total} total questions, {total_questions} matching filters")
            logger.info(f"🔍 Debug: Filter conditions: {where_conditions}")
            logger.info(f"🔍 Debug: Query params: {query_params}")
            
            if total_questions == 0:
                return "", {}, debug_total, 0
            
            logger.info(f"📊 Processing {total_questions} filtered questions from dataset {dataset_id}")
            
            # Determine which columns to select based on selected_columns filter
            column_selection = []
            if not selected_columns or 1 in selected_columns:
                column_selection.append("original_question")
            if not selected_columns or 2 in selected_columns:
                column_selection.append("ai_response")
            
            if not column_selection:
                column_selection = ["original_question", "ai_response"]  # Default to both
            
            logger.info(f"🔍 Debug: Selected columns filter: {selected_columns}")
            logger.info(f"🔍 Debug: Column selection: {column_selection}")
            
            # Build the main query - using correct field names
            select_columns = ", ".join(column_selection + ["org_name", "user_id_from_csv"])
            questions_sql = text(f"""
                SELECT {select_columns}
                FROM questions 
                WHERE {" AND ".join(where_conditions)}
                AND ({" IS NOT NULL OR ".join(column_selection)} IS NOT NULL)
            """)
            
            questions_result = db.execute(questions_sql, query_params).fetchall()
            filtered_count = len(questions_result)
            
            # Build text efficiently
            text_parts = []
            tenant_info = {}
            
            for row in questions_result:
                # Extract tenant info from first row
                if not tenant_info:
                    tenant_info = {
                        'org_name': getattr(row, 'org_name', None),
                        'user_id_from_csv': getattr(row, 'user_id_from_csv', None)
                    }
                
                # Add text based on selected columns
                if not selected_columns or 1 in selected_columns:
                    if hasattr(row, 'original_question') and row.original_question:
                        text_parts.append(str(row.original_question))
                
                if not selected_columns or 2 in selected_columns:
                    if hasattr(row, 'ai_response') and row.ai_response:
                        text_parts.append(str(row.ai_response))
            
            all_text = " ".join(text_parts)
            
            return all_text, tenant_info, total_questions, filtered_count
            
        except Exception as e:
            logger.error(f"Error getting filtered text data for dataset {dataset_id}: {e}")
            return "", {}, 0, 0
    
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
    async def _process_text_with_filters(
        text_data: str, 
        analysis_mode: str, 
        tenant_info: Dict, 
        exclude_words: List[str],
        include_words: Optional[List[str]] = None,
        min_word_length: int = 3
    ) -> Counter:
        """Process text with comprehensive filtering support"""
        
        # Clean text first
        cleaned_text = TextValidationService.clean_text_for_analysis(
            text_data, 
            tenant_info=tenant_info,
            additional_blacklist=exclude_words
        )
        
        # For very large text, split processing
        if len(cleaned_text) > 1000000:  # 1MB of text
            word_counts = await OptimizedWordCloudService._process_large_text_parallel(cleaned_text, analysis_mode)
        else:
            word_counts = OptimizedWordCloudService._process_text_mode(cleaned_text, analysis_mode)
        
        # Apply additional filters
        filtered_counts = Counter()
        for word, count in word_counts.items():
            # Apply minimum length filter
            if len(word) < min_word_length:
                continue
            
            # Apply include words filter (if specified, only include these words)
            if include_words and word.lower() not in [w.lower() for w in include_words]:
                continue
            
            filtered_counts[word] = count
        
        return filtered_counts
    
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
            # Enhanced emotion detection for legal/customer service context
            emotion_pattern = re.compile(r'\b(?:' +
                # Positive emotions
                'happy|pleased|satisfied|excited|confident|relieved|grateful|appreciative|hopeful|optimistic|comfortable|reassured|impressed|delighted|thrilled|content|calm|peaceful|secure|trusting|encouraged|motivated|empowered|' +
                # Negative emotions  
                'angry|frustrated|upset|disappointed|worried|concerned|anxious|stressed|confused|overwhelmed|irritated|annoyed|furious|outraged|devastated|heartbroken|discouraged|hopeless|desperate|betrayed|violated|helpless|powerless|abandoned|ignored|dismissed|' +
                # Neutral/descriptive emotions
                'surprised|shocked|amazed|curious|interested|cautious|uncertain|skeptical|doubtful|hesitant|conflicted|ambivalent|' +
                # Intensity words
                'extremely|very|quite|somewhat|slightly|incredibly|absolutely|completely|totally|utterly|deeply|profoundly|' +
                # Legal emotional context
                'traumatic|devastating|life-changing|overwhelming|unbearable|intolerable|unacceptable|fair|unfair|just|unjust|reasonable|unreasonable|' +
                # Satisfaction levels
                'excellent|outstanding|exceptional|good|average|poor|terrible|awful|horrible|wonderful|fantastic|amazing|disappointing|unsatisfactory' +
                r')\b', re.IGNORECASE)
            words = emotion_pattern.findall(text.lower())
            return Counter(words)
            
        elif analysis_mode == "themes":
            # Enhanced theme detection for legal/business context
            theme_pattern = re.compile(r'\b(?:' +
                # Legal themes
                'litigation|settlement|negotiation|mediation|arbitration|discovery|deposition|testimony|evidence|witness|expert|trial|court|hearing|motion|appeal|verdict|judgment|damages|liability|negligence|malpractice|contract|agreement|breach|violation|compliance|regulation|statute|law|legal|judicial|attorney|lawyer|counsel|' +
                # Business/Corporate themes
                'business|corporate|company|organization|management|leadership|strategy|operations|finance|accounting|budget|revenue|profit|investment|merger|acquisition|partnership|collaboration|venture|startup|enterprise|' +
                # Technology themes
                'technology|software|hardware|system|platform|application|database|network|security|cybersecurity|data|analytics|artificial|intelligence|machine|learning|automation|digital|cloud|internet|website|mobile|' +
                # Process themes
                'process|procedure|protocol|methodology|framework|workflow|implementation|deployment|development|testing|quality|performance|efficiency|optimization|improvement|innovation|solution|troubleshooting|maintenance|support|' +
                # Communication themes
                'communication|correspondence|meeting|conference|presentation|report|documentation|training|education|consultation|advice|guidance|instruction|explanation|clarification|notification|announcement|' +
                # Service themes
                'service|support|assistance|help|customer|client|user|experience|satisfaction|feedback|complaint|issue|problem|resolution|response|delivery|performance|quality|standard|requirement|expectation|' +
                # Healthcare/Insurance themes
                'medical|health|healthcare|treatment|diagnosis|therapy|rehabilitation|recovery|injury|accident|insurance|claim|coverage|benefits|compensation|disability|workers|employment|workplace|safety' +
                r')\b', re.IGNORECASE)
            words = theme_pattern.findall(text.lower())
            return Counter(words)
            
        elif analysis_mode == "topics":
            # Enhanced topic detection for advanced legal/business analysis
            topic_pattern = re.compile(r'\b(?:' +
                # Legal topics
                'constitutional|statutory|regulatory|procedural|substantive|criminal|civil|administrative|contract|tort|property|intellectual|employment|environmental|healthcare|immigration|family|estate|bankruptcy|securities|antitrust|' +
                # Technology topics
                'artificial|intelligence|machine|learning|neural|network|algorithm|blockchain|cryptocurrency|cybersecurity|cloud|computing|database|analytics|automation|robotics|digitization|transformation|innovation|' +
                # Business topics
                'strategic|operational|financial|marketing|sales|procurement|supply|chain|logistics|distribution|manufacturing|production|quality|assurance|risk|management|compliance|governance|audit|' +
                # Research/Analysis topics
                'research|analysis|methodology|statistical|quantitative|qualitative|empirical|theoretical|experimental|observational|longitudinal|cross-sectional|meta-analysis|systematic|review|' +
                # Communication topics
                'interpersonal|organizational|mass|digital|social|media|public|relations|marketing|advertising|branding|messaging|storytelling|narrative|discourse|rhetoric|' +
                # Process improvement topics
                'optimization|efficiency|productivity|streamlining|standardization|automation|lean|agile|six-sigma|continuous|improvement|best-practices|benchmarking|performance|measurement|' +
                # Industry-specific topics
                'automotive|aerospace|pharmaceutical|biotechnology|telecommunications|energy|utilities|construction|real-estate|hospitality|retail|e-commerce|education|healthcare|finance|insurance' +
                r')\b', re.IGNORECASE)
            words = topic_pattern.findall(text.lower())
            return Counter(words)
            
        elif analysis_mode == "entities":
            # Enhanced entity detection for legal/business context
            entity_words = []
            
            # Capitalized words (potential proper nouns)
            capitalized = re.findall(r'\b[A-Z][a-z]{2,}\b', text)
            entity_words.extend([word.lower() for word in capitalized])
            
            # Legal entity patterns
            legal_entity_pattern = re.compile(r'\b(?:' +
                # Common names and titles
                'judge|justice|attorney|counsel|plaintiff|defendant|witness|expert|doctor|professor|manager|director|president|ceo|cfo|cto|' +
                # Organizations and institutions
                'court|tribunal|commission|agency|department|bureau|office|authority|board|committee|council|association|corporation|company|firm|partnership|llc|inc|ltd|' +
                # Legal document types
                'contract|agreement|motion|brief|complaint|petition|subpoena|warrant|order|judgment|verdict|settlement|transcript|deposition|affidavit|' +
                # Geographic entities
                'county|state|province|district|jurisdiction|federal|national|international|local|municipal|regional|' +
                # Time-related entities
                'monday|tuesday|wednesday|thursday|friday|saturday|sunday|january|february|march|april|may|june|july|august|september|october|november|december|' +
                # Legal concepts as entities
                'negligence|malpractice|liability|damages|compensation|insurance|coverage|benefits|disability|injury|accident|incident|violation|breach|' +
                # Technology entities
                'software|system|platform|application|database|server|network|website|portal|interface|algorithm|protocol|standard|framework|' +
                # Business entities
                'customer|client|vendor|supplier|partner|stakeholder|shareholder|employee|contractor|consultant|representative|agent|' +
                # Medical/Health entities
                'patient|provider|physician|specialist|therapist|treatment|procedure|diagnosis|condition|symptoms|recovery|rehabilitation' +
                r')\b', re.IGNORECASE)
            
            legal_entities = legal_entity_pattern.findall(text.lower())
            entity_words.extend(legal_entities)
            
            # Remove duplicates and return
            return Counter(entity_words)
            
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
        """Enhanced sentiment assignment based on analysis mode and word content"""
        if analysis_mode == "emotions":
            # Positive emotions
            positive_emotions = {
                'happy', 'pleased', 'satisfied', 'excited', 'confident', 'relieved', 'grateful', 
                'appreciative', 'hopeful', 'optimistic', 'comfortable', 'reassured', 'impressed', 
                'delighted', 'thrilled', 'content', 'calm', 'peaceful', 'secure', 'trusting', 
                'encouraged', 'motivated', 'empowered', 'excellent', 'outstanding', 'exceptional', 
                'good', 'wonderful', 'fantastic', 'amazing'
            }
            
            # Negative emotions
            negative_emotions = {
                'angry', 'frustrated', 'upset', 'disappointed', 'worried', 'concerned', 'anxious', 
                'stressed', 'confused', 'overwhelmed', 'irritated', 'annoyed', 'furious', 'outraged', 
                'devastated', 'heartbroken', 'discouraged', 'hopeless', 'desperate', 'betrayed', 
                'violated', 'helpless', 'powerless', 'abandoned', 'ignored', 'dismissed', 'traumatic', 
                'devastating', 'unbearable', 'intolerable', 'unacceptable', 'unfair', 'unjust', 
                'unreasonable', 'terrible', 'awful', 'horrible', 'poor', 'disappointing', 'unsatisfactory'
            }
            
            if word in positive_emotions:
                return "positive"
            elif word in negative_emotions:
                return "negative"
            else:
                return "neutral"
                
        elif analysis_mode == "themes":
            # Theme-based sentiment for legal/business context
            positive_themes = {
                'success', 'solution', 'improvement', 'innovation', 'optimization', 'efficiency', 
                'quality', 'excellence', 'satisfaction', 'resolution', 'agreement', 'settlement', 
                'collaboration', 'partnership', 'support', 'assistance', 'guidance', 'training', 
                'development', 'growth', 'recovery', 'rehabilitation', 'benefits', 'coverage', 
                'compensation', 'compliance', 'security', 'safety'
            }
            
            negative_themes = {
                'problem', 'issue', 'violation', 'breach', 'negligence', 'malpractice', 'liability', 
                'damages', 'injury', 'accident', 'complaint', 'dispute', 'conflict', 'litigation', 
                'failure', 'error', 'mistake', 'defect', 'risk', 'threat', 'crisis', 'emergency'
            }
            
            if word in positive_themes:
                return "positive"
            elif word in negative_themes:
                return "negative"
            else:
                return "theme"
                
        elif analysis_mode == "topics":
            # Neutral sentiment for topics - they're analytical
            return "topic"
            
        elif analysis_mode == "entities":
            # Entities are generally neutral
            return "entity"
            
        elif analysis_mode in ("action", "verbs"):
            # Action words can have implied sentiment
            positive_actions = {
                'help', 'support', 'assist', 'improve', 'resolve', 'fix', 'solve', 'create', 
                'build', 'develop', 'enhance', 'optimize', 'succeed', 'achieve', 'accomplish', 
                'complete', 'deliver', 'provide', 'offer', 'give', 'share', 'collaborate', 
                'cooperate', 'agree', 'settle', 'recover', 'heal', 'restore'
            }
            
            negative_actions = {
                'fail', 'break', 'damage', 'harm', 'hurt', 'injure', 'violate', 'breach', 
                'dispute', 'conflict', 'argue', 'fight', 'oppose', 'reject', 'deny', 'refuse', 
                'cancel', 'terminate', 'abandon', 'neglect', 'ignore', 'dismiss', 'worsen', 
                'deteriorate', 'complain', 'criticize'
            }
            
            if word in positive_actions:
                return "positive"
            elif word in negative_actions:
                return "negative"
            else:
                return "action"
        else:
            return "neutral"
    
    @staticmethod
    def invalidate_cache(dataset_id: str = None):
        """Invalidate cache for a specific dataset or all datasets"""
        word_cloud_cache.invalidate(dataset_id)
