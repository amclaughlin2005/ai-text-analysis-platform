"""
Analytics models for storing NLTK analysis results and cached data
Includes detailed analysis results, word frequencies, and usage analytics
"""

from sqlalchemy import Column, String, DateTime, Integer, Float, Boolean, Text, ForeignKey, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from ..core.database import Base

class NLTKAnalysis(Base):
    """Detailed NLTK analysis results for each question"""
    
    __tablename__ = "nltk_analysis"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Question relationship (one-to-one)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False, unique=True, index=True)
    
    # Named Entity Recognition results
    entities = Column(JSON, nullable=True)  # {"persons": [], "organizations": [], "locations": [], "misc": []}
    entity_counts = Column(JSON, nullable=True)  # {"PERSON": 5, "ORG": 3, "GPE": 2}
    
    # Topic modeling results
    topics = Column(JSON, nullable=True)  # [{"topic_id": 0, "words": ["word1", "word2"], "score": 0.8}]
    topic_assignments = Column(JSON, nullable=True)  # [0, 2, 1] - topic assignments
    topic_coherence = Column(Float, nullable=True)  # Topic coherence score
    
    # Keyword extraction results
    keywords_tfidf = Column(JSON, nullable=True)  # [{"word": "important", "score": 0.85}]
    keywords_yake = Column(JSON, nullable=True)  # [{"phrase": "machine learning", "score": 0.15}]
    keywords_textrank = Column(JSON, nullable=True)  # [{"word": "analysis", "score": 0.92}]
    
    # Theme and category analysis
    themes = Column(JSON, nullable=True)  # Identified themes and categories
    theme_confidence = Column(JSON, nullable=True)  # Confidence scores for themes
    
    # Part-of-speech tagging
    pos_tags = Column(JSON, nullable=True)  # [{"word": "machine", "pos": "NN"}]
    pos_summary = Column(JSON, nullable=True)  # {"nouns": 15, "verbs": 8, "adjectives": 5}
    
    # Dependency parsing
    dependency_tree = Column(JSON, nullable=True)  # Simplified dependency relationships
    syntactic_complexity = Column(Float, nullable=True)  # Syntactic complexity score
    
    # Advanced linguistic features
    linguistic_features = Column(JSON, nullable=True)  # Advanced NLP features
    semantic_roles = Column(JSON, nullable=True)  # Semantic role labeling results
    
    # Processing metadata
    analysis_version = Column(String(20), nullable=False, default="1.0")
    processing_time_ms = Column(Integer, nullable=True)
    model_versions = Column(JSON, nullable=True)  # Versions of models used
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    question = relationship("Question", back_populates="nltk_analysis")
    
    def __repr__(self):
        return f"<NLTKAnalysis(id={self.id}, question_id={self.question_id})>"
    
    def to_dict(self):
        """Convert analysis object to dictionary"""
        return {
            "id": str(self.id),
            "question_id": str(self.question_id),
            "entities": self.entities,
            "entity_counts": self.entity_counts,
            "topics": self.topics,
            "topic_assignments": self.topic_assignments,
            "topic_coherence": self.topic_coherence,
            "keywords_tfidf": self.keywords_tfidf,
            "keywords_yake": self.keywords_yake,
            "keywords_textrank": self.keywords_textrank,
            "themes": self.themes,
            "theme_confidence": self.theme_confidence,
            "pos_tags": self.pos_tags,
            "pos_summary": self.pos_summary,
            "dependency_tree": self.dependency_tree,
            "syntactic_complexity": self.syntactic_complexity,
            "linguistic_features": self.linguistic_features,
            "semantic_roles": self.semantic_roles,
            "analysis_version": self.analysis_version,
            "processing_time_ms": self.processing_time_ms,
            "model_versions": self.model_versions,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class WordFrequency(Base):
    """Word frequency data for word cloud generation"""
    
    __tablename__ = "word_frequencies"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Dataset relationship
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False, index=True)
    
    # Word cloud analysis mode
    analysis_mode = Column(String(50), nullable=False, index=True)  # 'all', 'verbs', 'themes', 'emotions', etc.
    
    # Word data
    word = Column(String(255), nullable=False, index=True)
    frequency = Column(Integer, nullable=False)
    normalized_frequency = Column(Float, nullable=True)  # Frequency normalized to 0-1
    
    # Word classification
    word_type = Column(String(50), nullable=True, index=True)  # 'noun', 'verb', 'adjective', 'entity', etc.
    sentiment_association = Column(String(20), nullable=True, index=True)  # 'positive', 'negative', 'neutral'
    theme_category = Column(String(100), nullable=True, index=True)  # Theme or category association
    
    # Additional word metadata
    word_length = Column(Integer, nullable=True)
    is_stopword = Column(Boolean, default=False, nullable=False)
    is_custom_filtered = Column(Boolean, default=False, nullable=False)
    
    # Context and significance
    context_examples = Column(JSON, nullable=True)  # Examples where this word appears
    tfidf_score = Column(Float, nullable=True)  # TF-IDF score
    significance_score = Column(Float, nullable=True)  # Overall significance score
    
    # Relationships to source data
    source_questions = Column(JSON, nullable=True)  # Question IDs where this word appears
    co_occurrence_words = Column(JSON, nullable=True)  # Words that commonly appear with this word
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    dataset = relationship("Dataset", back_populates="word_frequencies")
    
    # Composite indexes for performance
    __table_args__ = (
        Index('ix_word_freq_dataset_mode', 'dataset_id', 'analysis_mode'),
        Index('ix_word_freq_word_type', 'word', 'word_type'),
        Index('ix_word_freq_frequency', 'frequency'),
    )
    
    def __repr__(self):
        return f"<WordFrequency(word={self.word}, frequency={self.frequency}, mode={self.analysis_mode})>"
    
    def to_dict(self):
        """Convert word frequency object to dictionary"""
        return {
            "id": str(self.id),
            "dataset_id": str(self.dataset_id),
            "analysis_mode": self.analysis_mode,
            "word": self.word,
            "frequency": self.frequency,
            "normalized_frequency": self.normalized_frequency,
            "word_type": self.word_type,
            "sentiment_association": self.sentiment_association,
            "theme_category": self.theme_category,
            "word_length": self.word_length,
            "is_stopword": self.is_stopword,
            "is_custom_filtered": self.is_custom_filtered,
            "tfidf_score": self.tfidf_score,
            "significance_score": self.significance_score,
            "context_examples": self.context_examples,
            "co_occurrence_words": self.co_occurrence_words,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class LLMAnalysisCache(Base):
    """Cache for expensive LLM analysis results"""
    
    __tablename__ = "llm_analysis_cache"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Query identification
    query_hash = Column(String(64), nullable=False, unique=True, index=True)  # SHA-256 hash
    query_text = Column(Text, nullable=False)  # Original query text
    result_type = Column(String(100), nullable=False, index=True)  # Type of analysis
    
    # LLM results
    result_data = Column(JSON, nullable=False)  # Cached analysis results
    model_used = Column(String(100), nullable=False)  # Model used for analysis
    model_version = Column(String(50), nullable=True)  # Model version
    
    # Usage and performance
    hit_count = Column(Integer, default=1, nullable=False)  # Number of cache hits
    last_accessed = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processing_time_ms = Column(Integer, nullable=True)  # Original processing time
    
    # Cache management
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)
    is_expired = Column(Boolean, default=False, nullable=False, index=True)
    cache_tags = Column(JSON, nullable=True)  # Tags for cache invalidation
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<LLMAnalysisCache(query_hash={self.query_hash[:8]}..., type={self.result_type}, hits={self.hit_count})>"
    
    def increment_hit_count(self):
        """Increment cache hit count and update last accessed time"""
        self.hit_count += 1
        self.last_accessed = func.now()
    
    def is_cache_valid(self) -> bool:
        """Check if cache entry is still valid"""
        if self.is_expired:
            return False
        if self.expires_at:
            from datetime import datetime
            return datetime.utcnow() < self.expires_at
        return True

class OrgUsageAnalytics(Base):
    """Organization-level usage analytics from CSV data"""
    
    __tablename__ = "org_usage_analytics"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Organization identification
    org_id = Column(String(255), nullable=False, index=True)
    org_name = Column(String(255), nullable=False, index=True)
    
    # Time period
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    period_type = Column(String(20), default="daily", nullable=False)  # daily, weekly, monthly
    
    # Usage metrics
    question_count = Column(Integer, default=0, nullable=False)
    unique_users_count = Column(Integer, default=0, nullable=False)
    response_count = Column(Integer, default=0, nullable=False)
    
    # Sentiment analysis
    avg_sentiment = Column(Float, nullable=True)
    sentiment_distribution = Column(JSON, nullable=True)  # Distribution of sentiments
    
    # Question types and patterns
    question_types = Column(JSON, nullable=True)  # Distribution of question types
    top_keywords = Column(JSON, nullable=True)  # Top keywords for the period
    themes = Column(JSON, nullable=True)  # Common themes
    
    # Response quality metrics
    avg_response_quality = Column(Float, nullable=True)
    avg_response_length = Column(Float, nullable=True)
    response_completeness_avg = Column(Float, nullable=True)
    
    # Complexity and readability
    avg_complexity_score = Column(Float, nullable=True)
    avg_readability_score = Column(Float, nullable=True)
    
    # Trend indicators
    growth_rate = Column(Float, nullable=True)  # Growth compared to previous period
    engagement_score = Column(Float, nullable=True)  # Engagement quality score
    
    # Additional analytics
    peak_usage_hour = Column(Integer, nullable=True)  # Peak usage hour (0-23)
    common_entities = Column(JSON, nullable=True)  # Common entities mentioned
    satisfaction_indicators = Column(JSON, nullable=True)  # Satisfaction metrics
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Composite indexes for performance
    __table_args__ = (
        Index('ix_org_analytics_org_date', 'org_id', 'date'),
        Index('ix_org_analytics_period', 'period_type', 'date'),
    )
    
    def __repr__(self):
        return f"<OrgUsageAnalytics(org={self.org_name}, date={self.date.date()}, questions={self.question_count})>"
    
    def to_dict(self):
        """Convert analytics object to dictionary"""
        return {
            "id": str(self.id),
            "org_id": self.org_id,
            "org_name": self.org_name,
            "date": self.date.isoformat() if self.date else None,
            "period_type": self.period_type,
            "question_count": self.question_count,
            "unique_users_count": self.unique_users_count,
            "response_count": self.response_count,
            "avg_sentiment": self.avg_sentiment,
            "sentiment_distribution": self.sentiment_distribution,
            "question_types": self.question_types,
            "top_keywords": self.top_keywords,
            "themes": self.themes,
            "avg_response_quality": self.avg_response_quality,
            "avg_response_length": self.avg_response_length,
            "response_completeness_avg": self.response_completeness_avg,
            "avg_complexity_score": self.avg_complexity_score,
            "avg_readability_score": self.avg_readability_score,
            "growth_rate": self.growth_rate,
            "engagement_score": self.engagement_score,
            "peak_usage_hour": self.peak_usage_hour,
            "common_entities": self.common_entities,
            "satisfaction_indicators": self.satisfaction_indicators,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
