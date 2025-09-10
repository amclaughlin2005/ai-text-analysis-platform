"""
Analysis service for background processing and word frequency generation
"""

import logging
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from collections import Counter

from ..models.dataset import Dataset
from ..models.question import Question
from ..models.analytics import WordFrequency
from ..core.database import DatabaseTransaction

logger = logging.getLogger(__name__)

class AnalysisService:
    """
    Service for text analysis and word frequency generation
    """
    
    @classmethod
    def generate_word_frequencies(
        cls,
        dataset_id: str,
        analysis_mode: str = 'all',
        selected_columns: List[int] = None,
        db: Session = None,
        force_regenerate: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Generate word frequencies for dataset with NLTK analysis
        
        Args:
            dataset_id: Dataset UUID
            analysis_mode: Analysis mode (all, verbs, nouns, adjectives, emotions)
            selected_columns: CSV columns to analyze (1=questions, 2=responses)
            db: Database session
            force_regenerate: Force regeneration even if cached data exists
            
        Returns:
            List of word frequency dictionaries
        """
        try:
            # Check if we already have cached results
            if not force_regenerate:
                existing_frequencies = cls._get_cached_word_frequencies(
                    dataset_id, analysis_mode, db
                )
                if existing_frequencies:
                    logger.info(f"📊 Using cached word frequencies for {dataset_id} - {analysis_mode}")
                    return [freq.to_dict() for freq in existing_frequencies]
            
            # Get dataset and questions
            dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
            if not dataset:
                logger.error(f"❌ Dataset not found: {dataset_id}")
                return []
            
            questions = db.query(Question)\
                         .filter(Question.dataset_id == dataset_id)\
                         .all()
            
            if not questions:
                logger.warning(f"⚠️ No questions found for dataset: {dataset_id}")
                return []
            
            # Extract and process text
            word_data = cls._process_text_with_nltk(
                questions=questions,
                analysis_mode=analysis_mode,
                selected_columns=selected_columns or [1, 2]
            )
            
            # Clear existing frequencies if regenerating
            if force_regenerate:
                cls._clear_existing_frequencies(dataset_id, analysis_mode, db)
            
            # Save to database
            with DatabaseTransaction(db) as transaction_db:
                cls._save_word_frequencies(
                    dataset_id=dataset_id,
                    word_data=word_data,
                    analysis_mode=analysis_mode,
                    selected_columns=selected_columns or [1, 2],
                    db=transaction_db
                )
                transaction_db.commit()
            
            logger.info(f"✅ Generated {len(word_data)} word frequencies for {dataset_id}")
            return word_data
            
        except Exception as e:
            logger.error(f"❌ Failed to generate word frequencies: {e}", exc_info=True)
            return []

    @classmethod
    def _get_cached_word_frequencies(
        cls,
        dataset_id: str,
        analysis_mode: str,
        db: Session,
        limit: int = 50
    ) -> List[WordFrequency]:
        """Get cached word frequencies from database"""
        try:
            return db.query(WordFrequency)\
                    .filter(
                        and_(
                            WordFrequency.dataset_id == dataset_id,
                            WordFrequency.analysis_mode == analysis_mode
                        )
                    )\
                    .order_by(desc(WordFrequency.frequency))\
                    .limit(limit)\
                    .all()
        except Exception as e:
            logger.error(f"❌ Failed to get cached frequencies: {e}")
            return []

    @classmethod
    def _process_text_with_nltk(
        cls,
        questions: List[Question],
        analysis_mode: str,
        selected_columns: List[int]
    ) -> List[Dict[str, Any]]:
        """Process text using NLTK with POS tagging for analysis modes"""
        try:
            # Import NLTK components
            import nltk
            from nltk.tokenize import word_tokenize
            from nltk.tag import pos_tag
            from nltk.corpus import stopwords
            
            # Ensure NLTK data is available
            cls._ensure_nltk_data()
            
            # Extract text based on selected columns
            text_parts = []
            for question in questions:
                if 1 in selected_columns and question.original_question:
                    text_parts.append(question.original_question.lower())
                
                if 2 in selected_columns and question.ai_response:
                    text_parts.append(question.ai_response.lower())
            
            if not text_parts:
                return []
            
            # Combine all text
            all_text = ' '.join(text_parts)
            
            # Tokenize and POS tag
            tokens = word_tokenize(all_text.lower())
            pos_tags = pos_tag(tokens)
            
            # Filter based on analysis mode
            filtered_tokens = cls._filter_tokens_by_mode(pos_tags, analysis_mode)
            
            # Remove noise words and stopwords
            clean_tokens = cls._remove_noise_words(filtered_tokens)
            
            # Count frequencies
            word_counts = Counter(clean_tokens)
            
            # Create word data
            return cls._create_word_data(word_counts, analysis_mode)
            
        except Exception as e:
            logger.error(f"❌ NLTK processing failed: {e}")
            # Fallback to simple processing
            return cls._simple_text_processing(questions, selected_columns, analysis_mode)

    @classmethod
    def _filter_tokens_by_mode(cls, pos_tags: List[tuple], analysis_mode: str) -> List[str]:
        """Filter tokens based on analysis mode using POS tags"""
        if analysis_mode == 'verbs' or analysis_mode == 'action':
            # Extract verbs (VB, VBD, VBG, VBN, VBP, VBZ)
            return [word for word, pos in pos_tags 
                   if pos.startswith('VB') and len(word) >= 3 and word.isalpha()]
        
        elif analysis_mode == 'nouns':
            # Extract nouns (NN, NNS, NNP, NNPS)
            return [word for word, pos in pos_tags 
                   if pos.startswith('NN') and len(word) >= 3 and word.isalpha()]
        
        elif analysis_mode == 'adjectives':
            # Extract adjectives (JJ, JJR, JJS)
            return [word for word, pos in pos_tags 
                   if pos.startswith('JJ') and len(word) >= 3 and word.isalpha()]
        
        elif analysis_mode == 'emotions':
            # Extract emotion-related words
            emotion_pos = ['JJ', 'JJR', 'JJS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
            emotion_keywords = {
                'feel', 'felt', 'happy', 'sad', 'angry', 'excited', 'frustrated',
                'satisfied', 'disappointed', 'pleased', 'concerned', 'worried',
                'confident', 'nervous', 'comfortable', 'uncomfortable'
            }
            return [word for word, pos in pos_tags 
                   if ((pos in emotion_pos or word.lower() in emotion_keywords) 
                       and len(word) >= 3 and word.isalpha())]
        
        else:  # 'all' mode
            # Extract meaningful words (nouns, verbs, adjectives, adverbs)
            meaningful_pos = [
                'NN', 'NNS', 'NNP', 'NNPS',  # Nouns
                'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ',  # Verbs
                'JJ', 'JJR', 'JJS',  # Adjectives
                'RB', 'RBR', 'RBS'   # Adverbs
            ]
            return [word for word, pos in pos_tags 
                   if pos in meaningful_pos and len(word) >= 3 and word.isalpha()]

    @classmethod
    def _remove_noise_words(cls, tokens: List[str]) -> List[str]:
        """Remove stopwords and noise words"""
        try:
            from nltk.corpus import stopwords
            english_stops = set(stopwords.words('english'))
        except:
            english_stops = set()
        
        # Enhanced noise words list
        noise_words = {
            # User-specified exclusions (from memory)
            'details', 'page', 'https', 'filevineapp', 'docviewer',
            'view', 'source', 'embedding', 'docwebviewer', 'com', 'www',
            'html', 'link', 'url', 'href', 'retrieved', 'matching', 'appeared',
            
            # Common filler words
            'that', 'this', 'from', 'with', 'they', 'have', 'will',
            'about', 'information', 'could', 'would', 'should', 'when',
            'where', 'there', 'what', 'please', 'question', 'see',
            
            # Legal document technical terms
            'singletonschreiber', 'filevineapp', 'docwebviewer'
        }
        
        return [word for word in tokens 
                if (word.lower() not in noise_words and 
                    word.lower() not in english_stops and 
                    len(word) >= 3)]

    @classmethod
    def _create_word_data(cls, word_counts: Counter, analysis_mode: str) -> List[Dict[str, Any]]:
        """Create word data structures from counts"""
        word_data = []
        max_freq = max(word_counts.values()) if word_counts else 1
        
        for word, frequency in word_counts.most_common(50):  # Top 50 words
            # Simple sentiment analysis
            sentiment = cls._analyze_word_sentiment(word)
            
            word_data.append({
                'word': word,
                'frequency': frequency,
                'normalized_frequency': frequency / max_freq,
                'sentiment': sentiment,
                'size': frequency / max_freq,
                'analysis_mode': analysis_mode
            })
        
        return word_data

    @classmethod
    def _analyze_word_sentiment(cls, word: str) -> str:
        """Simple word-level sentiment analysis"""
        positive_words = {
            'excellent', 'great', 'good', 'helpful', 'satisfied', 
            'perfect', 'amazing', 'wonderful', 'fantastic', 'outstanding'
        }
        negative_words = {
            'bad', 'terrible', 'awful', 'frustrated', 'angry', 
            'disappointed', 'horrible', 'hate', 'worst', 'annoying'
        }
        
        word_lower = word.lower()
        if word_lower in positive_words:
            return 'positive'
        elif word_lower in negative_words:
            return 'negative'
        else:
            return 'neutral'

    @classmethod
    def _simple_text_processing(
        cls,
        questions: List[Question],
        selected_columns: List[int],
        analysis_mode: str
    ) -> List[Dict[str, Any]]:
        """Fallback simple text processing without NLTK"""
        import re
        
        # Extract text
        text_parts = []
        for question in questions:
            if 1 in selected_columns and question.original_question:
                text_parts.append(question.original_question.lower())
            if 2 in selected_columns and question.ai_response:
                text_parts.append(question.ai_response.lower())
        
        # Simple tokenization
        all_text = ' '.join(text_parts)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
        
        # Basic filtering
        filtered_words = [w for w in words if w not in {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were'
        }]
        
        word_counts = Counter(filtered_words)
        return cls._create_word_data(word_counts, analysis_mode)

    @classmethod
    def _save_word_frequencies(
        cls,
        dataset_id: str,
        word_data: List[Dict[str, Any]],
        analysis_mode: str,
        selected_columns: List[int],
        db: Session
    ):
        """Save word frequencies to database"""
        for word_info in word_data:
            word_freq = WordFrequency(
                dataset_id=dataset_id,
                word=word_info['word'],
                frequency=word_info['frequency'],
                normalized_frequency=word_info['normalized_frequency'],
                analysis_mode=analysis_mode,
                columns_analyzed=selected_columns,
                sentiment=word_info['sentiment']
            )
            db.add(word_freq)

    @classmethod
    def _clear_existing_frequencies(cls, dataset_id: str, analysis_mode: str, db: Session):
        """Clear existing word frequencies for regeneration"""
        try:
            db.query(WordFrequency)\
              .filter(
                  and_(
                      WordFrequency.dataset_id == dataset_id,
                      WordFrequency.analysis_mode == analysis_mode
                  )
              )\
              .delete()
            logger.info(f"🗑️ Cleared existing frequencies for {dataset_id} - {analysis_mode}")
        except Exception as e:
            logger.error(f"❌ Failed to clear existing frequencies: {e}")

    @classmethod
    def _ensure_nltk_data(cls):
        """Ensure required NLTK data is downloaded"""
        import nltk
        
        required_data = [
            'punkt', 'averaged_perceptron_tagger', 'stopwords'
        ]
        
        for data_name in required_data:
            try:
                nltk.data.find(f'tokenizers/{data_name}' if data_name == 'punkt' 
                              else f'taggers/{data_name}' if 'tagger' in data_name
                              else f'corpora/{data_name}')
            except LookupError:
                nltk.download(data_name, quiet=True)
