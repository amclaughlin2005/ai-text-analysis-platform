"""
NLTK Analysis Engine - Core text processing using NLTK and spaCy
Comprehensive text analysis including sentiment, entities, topics, and classification
"""

import re
import string
from typing import List, Dict, Tuple, Optional, Union, Any
import logging

# NLTK imports
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk

# TextBlob for additional sentiment analysis
from textblob import TextBlob

# spaCy for advanced NLP
import spacy
from spacy import displacy

# Scikit-learn for TF-IDF and clustering
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

# Gensim for topic modeling
from gensim import corpora, models
from gensim.models import LdaModel
from gensim.models.coherencemodel import CoherenceModel

# YAKE for keyword extraction
import yake

# Readability metrics
import textstat

# Sentence transformers for semantic similarity
from sentence_transformers import SentenceTransformer

import numpy as np
from datetime import datetime
import json

from ..core.logging import get_logger, log_performance

logger = get_logger(__name__)

class NLTKProcessor:
    """
    Comprehensive NLTK and spaCy-based text analysis processor
    Provides sentiment analysis, entity extraction, topic modeling, and more
    """
    
    def __init__(self):
        """Initialize NLTK processor with required models and data"""
        logger.info("Initializing NLTK Processor...")
        
        # Initialize NLTK components
        self._initialize_nltk()
        
        # Initialize spaCy model
        self._initialize_spacy()
        
        # Initialize sentence transformer for semantic similarity
        self._initialize_sentence_transformer()
        
        # Initialize other components
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        logger.info("✅ NLTK Processor initialized successfully")
    
    def _initialize_nltk(self):
        """Download and initialize required NLTK data"""
        try:
            # Download required NLTK data
            nltk_downloads = [
                'vader_lexicon', 'punkt', 'stopwords', 'wordnet',
                'averaged_perceptron_tagger', 'maxent_ne_chunker', 'words'
            ]
            
            for download in nltk_downloads:
                try:
                    nltk.data.find(f'corpora/{download}')
                except LookupError:
                    logger.info(f"Downloading NLTK data: {download}")
                    nltk.download(download, quiet=True)
            
            # Initialize sentiment analyzer
            self.vader_analyzer = SentimentIntensityAnalyzer()
            
        except Exception as e:
            logger.error(f"❌ NLTK initialization failed: {e}")
            raise
    
    def _initialize_spacy(self):
        """Initialize spaCy model for advanced NLP"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("✅ spaCy model loaded successfully")
        except OSError:
            logger.warning("⚠️ spaCy model not found. Run: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def _initialize_sentence_transformer(self):
        """Initialize sentence transformer for semantic similarity"""
        try:
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Sentence transformer loaded successfully")
        except Exception as e:
            logger.warning(f"⚠️ Sentence transformer initialization failed: {e}")
            self.sentence_model = None
    
    @log_performance(logger, "sentiment_analysis")
    def sentiment_analysis(self, text: str) -> Dict[str, Union[float, str]]:
        """
        Multi-model sentiment analysis using VADER and TextBlob
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with sentiment scores and labels
        """
        if not text or not text.strip():
            return {
                'compound_score': 0.0,
                'positive': 0.0,
                'negative': 0.0,
                'neutral': 1.0,
                'confidence': 0.0,
                'label': 'neutral'
            }
        
        try:
            # VADER sentiment analysis
            vader_scores = self.vader_analyzer.polarity_scores(text)
            
            # TextBlob sentiment analysis
            blob = TextBlob(text)
            textblob_polarity = blob.sentiment.polarity  # -1 to 1
            textblob_subjectivity = blob.sentiment.subjectivity  # 0 to 1
            
            # Combine scores (weighted average)
            compound_score = (vader_scores['compound'] + textblob_polarity) / 2
            
            # Determine label
            if compound_score >= 0.05:
                label = 'positive'
            elif compound_score <= -0.05:
                label = 'negative'
            else:
                label = 'neutral'
            
            # Calculate confidence based on agreement between models
            vader_label = 'positive' if vader_scores['compound'] >= 0.05 else 'negative' if vader_scores['compound'] <= -0.05 else 'neutral'
            textblob_label = 'positive' if textblob_polarity >= 0.05 else 'negative' if textblob_polarity <= -0.05 else 'neutral'
            confidence = 1.0 if vader_label == textblob_label else 0.7
            
            return {
                'compound_score': compound_score,
                'positive': vader_scores['pos'],
                'negative': vader_scores['neg'],
                'neutral': vader_scores['neu'],
                'confidence': confidence,
                'label': label,
                'vader_scores': vader_scores,
                'textblob_polarity': textblob_polarity,
                'textblob_subjectivity': textblob_subjectivity
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {
                'compound_score': 0.0,
                'positive': 0.0,
                'negative': 0.0,
                'neutral': 1.0,
                'confidence': 0.0,
                'label': 'neutral',
                'error': str(e)
            }
    
    @log_performance(logger, "entity_extraction")
    def entity_extraction(self, text: str) -> Dict[str, List[str]]:
        """
        Named Entity Recognition using spaCy
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with categorized entities
        """
        if not text or not text.strip():
            return {'persons': [], 'organizations': [], 'locations': [], 'misc': []}
        
        try:
            if self.nlp is None:
                logger.warning("spaCy model not available, using NLTK NER")
                return self._nltk_entity_extraction(text)
            
            # Process with spaCy
            doc = self.nlp(text)
            
            entities = {
                'persons': [],
                'organizations': [],
                'locations': [],
                'misc': []
            }
            
            for ent in doc.ents:
                entity_text = ent.text.strip()
                if entity_text:
                    if ent.label_ in ['PERSON']:
                        entities['persons'].append(entity_text)
                    elif ent.label_ in ['ORG']:
                        entities['organizations'].append(entity_text)
                    elif ent.label_ in ['GPE', 'LOC']:
                        entities['locations'].append(entity_text)
                    else:
                        entities['misc'].append(entity_text)
            
            # Remove duplicates and clean up
            for key in entities:
                entities[key] = list(set(entities[key]))
            
            return entities
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return {'persons': [], 'organizations': [], 'locations': [], 'misc': [], 'error': str(e)}
    
    def _nltk_entity_extraction(self, text: str) -> Dict[str, List[str]]:
        """Fallback entity extraction using NLTK"""
        try:
            tokens = word_tokenize(text)
            pos_tags = pos_tag(tokens)
            chunks = ne_chunk(pos_tags)
            
            entities = {'persons': [], 'organizations': [], 'locations': [], 'misc': []}
            
            for chunk in chunks:
                if hasattr(chunk, 'label'):
                    entity_text = ' '.join([token for token, pos in chunk.leaves()])
                    if chunk.label() == 'PERSON':
                        entities['persons'].append(entity_text)
                    elif chunk.label() == 'ORGANIZATION':
                        entities['organizations'].append(entity_text)
                    elif chunk.label() in ['GPE', 'LOCATION']:
                        entities['locations'].append(entity_text)
                    else:
                        entities['misc'].append(entity_text)
            
            return entities
            
        except Exception as e:
            logger.error(f"NLTK entity extraction failed: {e}")
            return {'persons': [], 'organizations': [], 'locations': [], 'misc': []}
    
    @log_performance(logger, "topic_modeling")
    def topic_modeling(self, texts: List[str], num_topics: int = 5) -> Dict[str, Any]:
        """
        LDA topic modeling with coherence scoring
        
        Args:
            texts: List of texts to analyze
            num_topics: Number of topics to extract
            
        Returns:
            Dictionary with topics and coherence scores
        """
        if not texts or len(texts) < 2:
            return {'topics': [], 'coherence_score': 0.0, 'topic_assignments': []}
        
        try:
            # Preprocess texts
            processed_texts = [self._preprocess_for_topics(text) for text in texts]
            processed_texts = [tokens for tokens in processed_texts if len(tokens) > 0]
            
            if len(processed_texts) < 2:
                return {'topics': [], 'coherence_score': 0.0, 'topic_assignments': []}
            
            # Create dictionary and corpus
            dictionary = corpora.Dictionary(processed_texts)
            dictionary.filter_extremes(no_below=2, no_above=0.8)
            corpus = [dictionary.doc2bow(tokens) for tokens in processed_texts]
            
            # Train LDA model
            lda_model = LdaModel(
                corpus=corpus,
                id2word=dictionary,
                num_topics=num_topics,
                random_state=42,
                passes=10,
                alpha='auto',
                per_word_topics=True
            )
            
            # Calculate coherence score
            coherence_model = CoherenceModel(
                model=lda_model,
                texts=processed_texts,
                dictionary=dictionary,
                coherence='c_v'
            )
            coherence_score = coherence_model.get_coherence()
            
            # Extract topics
            topics = []
            for topic_id in range(num_topics):
                topic_words = lda_model.show_topic(topic_id, topn=10)
                topics.append({
                    'topic_id': topic_id,
                    'words': [word for word, prob in topic_words],
                    'word_probabilities': topic_words,
                    'description': self._generate_topic_description(topic_words)
                })
            
            # Get topic assignments for each document
            topic_assignments = []
            for doc_bow in corpus:
                doc_topics = lda_model.get_document_topics(doc_bow)
                if doc_topics:
                    # Get the topic with highest probability
                    best_topic = max(doc_topics, key=lambda x: x[1])
                    topic_assignments.append(best_topic[0])
                else:
                    topic_assignments.append(-1)  # No clear topic
            
            return {
                'topics': topics,
                'coherence_score': coherence_score,
                'topic_assignments': topic_assignments,
                'num_topics': num_topics,
                'total_documents': len(texts)
            }
            
        except Exception as e:
            logger.error(f"Topic modeling failed: {e}")
            return {
                'topics': [],
                'coherence_score': 0.0,
                'topic_assignments': [],
                'error': str(e)
            }
    
    def _preprocess_for_topics(self, text: str) -> List[str]:
        """Preprocess text for topic modeling"""
        if not text:
            return []
        
        # Convert to lowercase and remove punctuation
        text = text.lower()
        text = re.sub(f'[{string.punctuation}]', ' ', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords, short words, and lemmatize
        processed_tokens = []
        for token in tokens:
            if (token not in self.stop_words and 
                len(token) > 2 and 
                token.isalpha()):
                lemmatized = self.lemmatizer.lemmatize(token)
                processed_tokens.append(lemmatized)
        
        return processed_tokens
    
    def _generate_topic_description(self, topic_words: List[Tuple[str, float]]) -> str:
        """Generate human-readable description for topic"""
        top_words = [word for word, prob in topic_words[:3]]
        return f"Topic about {', '.join(top_words)}"
    
    @log_performance(logger, "keyword_extraction")
    def keyword_extraction(self, text: str, method: str = 'tfidf') -> Dict[str, List[Tuple[str, float]]]:
        """
        Multi-method keyword extraction
        
        Args:
            text: Input text to analyze
            method: Extraction method ('tfidf', 'yake', 'textrank', 'all')
            
        Returns:
            Dictionary with keyword lists for each method
        """
        if not text or not text.strip():
            return {'tfidf_keywords': [], 'yake_keywords': [], 'textrank_keywords': []}
        
        results = {}
        
        try:
            # TF-IDF keyword extraction
            if method in ['tfidf', 'all']:
                results['tfidf_keywords'] = self._tfidf_keywords(text)
            
            # YAKE keyword extraction
            if method in ['yake', 'all']:
                results['yake_keywords'] = self._yake_keywords(text)
            
            # TextRank keyword extraction (simplified)
            if method in ['textrank', 'all']:
                results['textrank_keywords'] = self._textrank_keywords(text)
            
            return results
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return {'error': str(e)}
    
    def _tfidf_keywords(self, text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Extract keywords using TF-IDF"""
        try:
            vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)  # Include bigrams
            )
            
            tfidf_matrix = vectorizer.fit_transform([text])
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            # Get top keywords
            keyword_scores = list(zip(feature_names, scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            return keyword_scores[:top_k]
            
        except Exception as e:
            logger.error(f"TF-IDF keyword extraction failed: {e}")
            return []
    
    def _yake_keywords(self, text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Extract keywords using YAKE"""
        try:
            kw_extractor = yake.KeywordExtractor(
                lan="en",
                n=3,  # n-grams up to 3 words
                dedupLim=0.7,
                top=top_k
            )
            
            keywords = kw_extractor.extract_keywords(text)
            # YAKE returns (phrase, score) where lower score is better
            # Convert to (phrase, relevance) where higher is better
            return [(phrase, 1 - score) for phrase, score in keywords]
            
        except Exception as e:
            logger.error(f"YAKE keyword extraction failed: {e}")
            return []
    
    def _textrank_keywords(self, text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Simplified TextRank-like keyword extraction"""
        try:
            # Simple frequency-based approach as TextRank alternative
            tokens = self._preprocess_for_topics(text)
            
            # Count word frequencies
            word_freq = {}
            for token in tokens:
                word_freq[token] = word_freq.get(token, 0) + 1
            
            # Sort by frequency and normalize scores
            max_freq = max(word_freq.values()) if word_freq else 1
            
            ranked_words = [
                (word, freq / max_freq) 
                for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            ]
            
            return ranked_words[:top_k]
            
        except Exception as e:
            logger.error(f"TextRank keyword extraction failed: {e}")
            return []
    
    @log_performance(logger, "readability_analysis")
    def readability_analysis(self, text: str) -> Dict[str, float]:
        """
        Multiple readability metrics analysis
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with readability scores
        """
        if not text or not text.strip():
            return {
                'flesch_reading_ease': 0.0,
                'flesch_kincaid_grade': 0.0,
                'gunning_fog': 0.0,
                'automated_readability': 0.0
            }
        
        try:
            return {
                'flesch_reading_ease': textstat.flesch_reading_ease(text),
                'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),
                'gunning_fog': textstat.gunning_fog(text),
                'automated_readability': textstat.automated_readability_index(text),
                'difficult_words': textstat.difficult_words(text),
                'text_standard': textstat.text_standard(text, float_output=False)
            }
            
        except Exception as e:
            logger.error(f"Readability analysis failed: {e}")
            return {'error': str(e)}
    
    @log_performance(logger, "text_similarity")
    def text_similarity(self, text1: str, text2: str, method: str = 'cosine') -> Dict[str, float]:
        """
        Semantic similarity analysis between two texts
        
        Args:
            text1: First text
            text2: Second text
            method: Similarity method ('cosine', 'jaccard', 'semantic')
            
        Returns:
            Dictionary with similarity scores
        """
        if not text1 or not text2:
            return {'cosine_similarity': 0.0, 'jaccard_similarity': 0.0, 'semantic_similarity': 0.0}
        
        try:
            results = {}
            
            # Cosine similarity using TF-IDF
            if method in ['cosine', 'all']:
                results['cosine_similarity'] = self._cosine_similarity(text1, text2)
            
            # Jaccard similarity
            if method in ['jaccard', 'all']:
                results['jaccard_similarity'] = self._jaccard_similarity(text1, text2)
            
            # Semantic similarity using sentence transformers
            if method in ['semantic', 'all'] and self.sentence_model:
                results['semantic_similarity'] = self._semantic_similarity(text1, text2)
            
            return results
            
        except Exception as e:
            logger.error(f"Text similarity analysis failed: {e}")
            return {'error': str(e)}
    
    def _cosine_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity using TF-IDF"""
        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except:
            return 0.0
    
    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity"""
        try:
            tokens1 = set(self._preprocess_for_topics(text1))
            tokens2 = set(self._preprocess_for_topics(text2))
            
            intersection = tokens1.intersection(tokens2)
            union = tokens1.union(tokens2)
            
            if len(union) == 0:
                return 0.0
            
            return len(intersection) / len(union)
        except:
            return 0.0
    
    def _semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity using sentence transformers"""
        try:
            embeddings = self.sentence_model.encode([text1, text2])
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return float(similarity)
        except:
            return 0.0
    
    @log_performance(logger, "question_classification")
    def question_classification(self, question: str) -> Dict[str, Union[str, float]]:
        """
        Classify question type and intent
        
        Args:
            question: Input question to classify
            
        Returns:
            Dictionary with classification results
        """
        if not question or not question.strip():
            return {
                'question_type': 'unknown',
                'intent': 'unknown',
                'complexity_score': 0.0,
                'urgency_level': 'low'
            }
        
        try:
            question_lower = question.lower()
            
            # Question type classification (rule-based)
            question_type = self._classify_question_type(question_lower)
            
            # Intent classification
            intent = self._classify_intent(question_lower)
            
            # Complexity scoring
            complexity_score = self._calculate_complexity_score(question)
            
            # Urgency level
            urgency_level = self._classify_urgency(question_lower)
            
            return {
                'question_type': question_type,
                'intent': intent,
                'complexity_score': complexity_score,
                'urgency_level': urgency_level,
                'length': len(question),
                'word_count': len(question.split())
            }
            
        except Exception as e:
            logger.error(f"Question classification failed: {e}")
            return {
                'question_type': 'unknown',
                'intent': 'unknown', 
                'complexity_score': 0.0,
                'urgency_level': 'low',
                'error': str(e)
            }
    
    def _classify_question_type(self, question: str) -> str:
        """Rule-based question type classification"""
        technical_keywords = ['api', 'code', 'error', 'bug', 'integration', 'database', 'server', 'technical']
        billing_keywords = ['payment', 'bill', 'invoice', 'charge', 'cost', 'price', 'subscription']
        feature_keywords = ['feature', 'functionality', 'capability', 'enhancement', 'improvement']
        
        if any(keyword in question for keyword in technical_keywords):
            return 'technical_support'
        elif any(keyword in question for keyword in billing_keywords):
            return 'billing'
        elif any(keyword in question for keyword in feature_keywords):
            return 'feature_request'
        elif 'how to' in question or 'how do' in question:
            return 'how_to'
        elif '?' in question:
            return 'general_inquiry'
        else:
            return 'general'
    
    def _classify_intent(self, question: str) -> str:
        """Rule-based intent classification"""
        if any(word in question for word in ['help', 'how', 'what', 'where', 'when', 'why']):
            return 'information_seeking'
        elif any(word in question for word in ['problem', 'issue', 'error', 'broken', 'not working']):
            return 'problem_reporting'
        elif any(word in question for word in ['thank', 'great', 'excellent', 'good', 'appreciate']):
            return 'positive_feedback'
        elif any(word in question for word in ['disappointed', 'frustrated', 'angry', 'terrible', 'bad']):
            return 'complaint'
        else:
            return 'general_inquiry'
    
    def _calculate_complexity_score(self, question: str) -> float:
        """Calculate question complexity based on various factors"""
        try:
            # Factors for complexity
            word_count = len(question.split())
            sentence_count = len(sent_tokenize(question))
            avg_word_length = np.mean([len(word) for word in question.split()])
            
            # Readability as complexity indicator
            try:
                flesch_score = textstat.flesch_reading_ease(question)
                # Convert flesch score to 0-1 scale (lower flesch = higher complexity)
                readability_complexity = max(0, (100 - flesch_score) / 100)
            except:
                readability_complexity = 0.5
            
            # Combine factors
            length_complexity = min(1.0, word_count / 50)  # Normalize by 50 words
            structure_complexity = min(1.0, sentence_count / 5)  # Normalize by 5 sentences
            word_complexity = min(1.0, (avg_word_length - 3) / 7)  # Normalize word length
            
            # Weighted average
            complexity = (
                length_complexity * 0.3 +
                structure_complexity * 0.2 +
                word_complexity * 0.2 +
                readability_complexity * 0.3
            )
            
            return min(1.0, max(0.0, complexity))
            
        except Exception as e:
            logger.error(f"Complexity calculation failed: {e}")
            return 0.5
    
    def _classify_urgency(self, question: str) -> str:
        """Classify urgency level of question"""
        urgent_keywords = ['urgent', 'emergency', 'asap', 'immediately', 'critical', 'broken', 'down']
        high_keywords = ['important', 'soon', 'quickly', 'priority', 'issue', 'problem']
        
        if any(keyword in question for keyword in urgent_keywords):
            return 'urgent'
        elif any(keyword in question for keyword in high_keywords):
            return 'high'
        elif len(question.split()) > 30:  # Long questions might be medium priority
            return 'medium'
        else:
            return 'low'
    
    @log_performance(logger, "batch_analysis")
    def analyze_batch(self, texts: List[str], include_topics: bool = True) -> Dict[str, Any]:
        """
        Analyze a batch of texts with all available methods
        
        Args:
            texts: List of texts to analyze
            include_topics: Whether to include topic modeling
            
        Returns:
            Comprehensive analysis results
        """
        logger.info(f"Starting batch analysis of {len(texts)} texts")
        
        try:
            results = {
                'total_texts': len(texts),
                'processed_texts': 0,
                'sentiment_analysis': [],
                'entity_analysis': [],
                'keyword_analysis': [],
                'readability_analysis': [],
                'classification_analysis': [],
                'topic_analysis': None,
                'processing_time': None,
                'errors': []
            }
            
            start_time = datetime.now()
            
            # Process each text individually
            for i, text in enumerate(texts):
                try:
                    # Sentiment analysis
                    sentiment = self.sentiment_analysis(text)
                    results['sentiment_analysis'].append(sentiment)
                    
                    # Entity extraction
                    entities = self.entity_extraction(text)
                    results['entity_analysis'].append(entities)
                    
                    # Keyword extraction
                    keywords = self.keyword_extraction(text, method='tfidf')
                    results['keyword_analysis'].append(keywords)
                    
                    # Readability
                    readability = self.readability_analysis(text)
                    results['readability_analysis'].append(readability)
                    
                    # Question classification
                    classification = self.question_classification(text)
                    results['classification_analysis'].append(classification)
                    
                    results['processed_texts'] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing text {i}: {e}")
                    results['errors'].append(f"Text {i}: {str(e)}")
            
            # Topic modeling on all texts
            if include_topics and len(texts) > 1:
                try:
                    topic_results = self.topic_modeling(texts)
                    results['topic_analysis'] = topic_results
                except Exception as e:
                    logger.error(f"Topic modeling failed: {e}")
                    results['errors'].append(f"Topic modeling: {str(e)}")
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            results['processing_time'] = processing_time
            
            logger.info(f"✅ Batch analysis completed in {processing_time:.2f} seconds")
            return results
            
        except Exception as e:
            logger.error(f"❌ Batch analysis failed: {e}")
            return {
                'total_texts': len(texts),
                'processed_texts': 0,
                'error': str(e)
            }
    
    def get_analysis_summary(self, batch_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics from batch analysis results"""
        try:
            sentiment_scores = [s.get('compound_score', 0) for s in batch_results.get('sentiment_analysis', [])]
            
            summary = {
                'total_processed': batch_results.get('processed_texts', 0),
                'processing_time': batch_results.get('processing_time', 0),
                'sentiment_summary': {
                    'average_sentiment': np.mean(sentiment_scores) if sentiment_scores else 0,
                    'sentiment_distribution': self._calculate_sentiment_distribution(batch_results.get('sentiment_analysis', []))
                },
                'entity_summary': self._summarize_entities(batch_results.get('entity_analysis', [])),
                'keyword_summary': self._summarize_keywords(batch_results.get('keyword_analysis', [])),
                'readability_summary': self._summarize_readability(batch_results.get('readability_analysis', [])),
                'classification_summary': self._summarize_classifications(batch_results.get('classification_analysis', [])),
                'errors_count': len(batch_results.get('errors', []))
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return {'error': str(e)}
    
    def _calculate_sentiment_distribution(self, sentiment_results: List[Dict]) -> Dict[str, float]:
        """Calculate sentiment distribution"""
        if not sentiment_results:
            return {'positive': 0, 'negative': 0, 'neutral': 0}
        
        labels = [s.get('label', 'neutral') for s in sentiment_results]
        total = len(labels)
        
        return {
            'positive': labels.count('positive') / total,
            'negative': labels.count('negative') / total,
            'neutral': labels.count('neutral') / total
        }
    
    def _summarize_entities(self, entity_results: List[Dict]) -> Dict[str, Any]:
        """Summarize entity extraction results"""
        all_entities = {'persons': [], 'organizations': [], 'locations': [], 'misc': []}
        
        for result in entity_results:
            for category, entities in result.items():
                if category != 'error' and isinstance(entities, list):
                    all_entities[category].extend(entities)
        
        # Count frequencies
        entity_counts = {}
        for category, entities in all_entities.items():
            entity_freq = {}
            for entity in entities:
                entity_freq[entity] = entity_freq.get(entity, 0) + 1
            entity_counts[category] = sorted(entity_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return entity_counts
    
    def _summarize_keywords(self, keyword_results: List[Dict]) -> Dict[str, Any]:
        """Summarize keyword extraction results"""
        all_keywords = []
        
        for result in keyword_results:
            tfidf_keywords = result.get('tfidf_keywords', [])
            all_keywords.extend([kw[0] for kw in tfidf_keywords])
        
        # Count frequencies
        keyword_freq = {}
        for keyword in all_keywords:
            keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
        
        top_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        
        return {
            'top_keywords': top_keywords,
            'total_unique_keywords': len(keyword_freq)
        }
    
    def _summarize_readability(self, readability_results: List[Dict]) -> Dict[str, float]:
        """Summarize readability analysis results"""
        if not readability_results:
            return {}
        
        flesch_scores = [r.get('flesch_reading_ease', 0) for r in readability_results if 'error' not in r]
        
        if not flesch_scores:
            return {}
        
        return {
            'average_readability': np.mean(flesch_scores),
            'readability_range': {
                'min': min(flesch_scores),
                'max': max(flesch_scores)
            }
        }
    
    def _summarize_classifications(self, classification_results: List[Dict]) -> Dict[str, Any]:
        """Summarize question classification results"""
        if not classification_results:
            return {}
        
        types = [c.get('question_type', 'unknown') for c in classification_results if 'error' not in c]
        intents = [c.get('intent', 'unknown') for c in classification_results if 'error' not in c]
        complexity_scores = [c.get('complexity_score', 0) for c in classification_results if 'error' not in c]
        
        type_counts = {t: types.count(t) for t in set(types)}
        intent_counts = {i: intents.count(i) for i in set(intents)}
        
        return {
            'question_types': type_counts,
            'intents': intent_counts,
            'average_complexity': np.mean(complexity_scores) if complexity_scores else 0
        }

# Global processor instance
_nltk_processor = None

def get_nltk_processor() -> NLTKProcessor:
    """Get global NLTK processor instance (singleton)"""
    global _nltk_processor
    if _nltk_processor is None:
        _nltk_processor = NLTKProcessor()
    return _nltk_processor
