"""
SQLAlchemy models for the AI Text Analysis Platform
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float, 
    ForeignKey, JSON, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

class Dataset(Base):
    """
    Represents uploaded CSV datasets
    """
    __tablename__ = "datasets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    filename = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(String(1000), nullable=False)
    
    # CSV structure information
    total_rows = Column(Integer, nullable=False, default=0)
    total_columns = Column(Integer, nullable=False, default=0)
    column_names = Column(JSON, nullable=True)  # List of column names
    encoding = Column(String(50), nullable=True, default='utf-8')
    
    # Processing status
    upload_status = Column(String(50), nullable=False, default='uploaded')
    processing_status = Column(String(50), nullable=False, default='pending')
    error_message = Column(Text, nullable=True)
    
    # Analytics metadata
    questions_count = Column(Integer, nullable=False, default=0)
    avg_question_length = Column(Float, nullable=True)
    avg_response_length = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    questions = relationship("Question", back_populates="dataset", cascade="all, delete-orphan")
    word_frequencies = relationship("WordFrequency", back_populates="dataset", cascade="all, delete-orphan")
    analysis_jobs = relationship("AnalysisJob", back_populates="dataset", cascade="all, delete-orphan")

    # Indexes for performance
    __table_args__ = (
        Index('idx_dataset_name', 'name'),
        Index('idx_dataset_status', 'processing_status'),
        Index('idx_dataset_created', 'created_at'),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'filename': self.filename,
            'file_size': self.file_size,
            'total_rows': self.total_rows,
            'total_columns': self.total_columns,
            'column_names': self.column_names,
            'upload_status': self.upload_status,
            'processing_status': self.processing_status,
            'questions_count': self.questions_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }

class Question(Base):
    """
    Individual questions from uploaded CSV datasets
    """
    __tablename__ = "questions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String, ForeignKey('datasets.id'), nullable=False, index=True)
    
    # Original CSV data
    csv_row_number = Column(Integer, nullable=False)
    original_question = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=True)
    context = Column(Text, nullable=True)
    
    # CSV metadata
    timestamp_from_csv = Column(String(255), nullable=True)
    user_id_from_csv = Column(String(255), nullable=True)
    project_id_from_csv = Column(String(255), nullable=True)
    
    # Data validation
    is_valid = Column(Boolean, nullable=False, default=True)
    validation_errors = Column(JSON, nullable=True)
    data_quality_score = Column(Float, nullable=True)
    
    # Text metrics
    question_length = Column(Integer, nullable=True)
    response_length = Column(Integer, nullable=True)
    word_count_question = Column(Integer, nullable=True)
    word_count_response = Column(Integer, nullable=True)
    
    # Analysis results
    sentiment_score = Column(Float, nullable=True)
    sentiment_label = Column(String(20), nullable=True)
    sentiment_confidence = Column(Float, nullable=True)
    complexity_score = Column(Float, nullable=True)
    urgency_level = Column(String(20), nullable=True)
    
    # Question categorization
    question_type = Column(String(100), nullable=True)
    question_intent = Column(String(100), nullable=True)
    
    # Response quality metrics
    response_relevance_score = Column(Float, nullable=True)
    response_completeness_score = Column(Float, nullable=True)
    response_quality_score = Column(Float, nullable=True)
    query_response_similarity = Column(Float, nullable=True)
    
    # Readability scores
    readability_question = Column(Float, nullable=True)
    readability_response = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    dataset = relationship("Dataset", back_populates="questions")
    nltk_analysis = relationship("NLTKAnalysis", back_populates="question", uselist=False)

    # Indexes
    __table_args__ = (
        Index('idx_question_dataset', 'dataset_id'),
        Index('idx_question_sentiment', 'sentiment_label'),
        Index('idx_question_quality', 'data_quality_score'),
        Index('idx_question_processed', 'processed_at'),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'dataset_id': self.dataset_id,
            'csv_row_number': self.csv_row_number,
            'original_question': self.original_question,
            'ai_response': self.ai_response,
            'context': self.context,
            'is_valid': self.is_valid,
            'sentiment_label': self.sentiment_label,
            'sentiment_score': self.sentiment_score,
            'question_length': self.question_length,
            'response_length': self.response_length,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class WordFrequency(Base):
    """
    Word frequency data for word clouds
    """
    __tablename__ = "word_frequencies"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String, ForeignKey('datasets.id'), nullable=False, index=True)
    
    # Word data
    word = Column(String(100), nullable=False, index=True)
    frequency = Column(Integer, nullable=False, default=0)
    normalized_frequency = Column(Float, nullable=False, default=0.0)
    
    # Analysis context
    analysis_mode = Column(String(50), nullable=False, default='all')  # all, verbs, themes, etc.
    columns_analyzed = Column(JSON, nullable=True)  # Which CSV columns were analyzed
    
    # Sentiment and categorization
    sentiment = Column(String(20), nullable=True, default='neutral')
    category = Column(String(100), nullable=True)
    
    # Word cloud display properties
    font_size = Column(Float, nullable=True)
    color_code = Column(String(10), nullable=True)
    position_x = Column(Float, nullable=True)
    position_y = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    dataset = relationship("Dataset", back_populates="word_frequencies")

    # Indexes and constraints
    __table_args__ = (
        Index('idx_word_dataset_mode', 'dataset_id', 'analysis_mode'),
        Index('idx_word_frequency', 'frequency'),
        Index('idx_word_sentiment', 'sentiment'),
        UniqueConstraint('dataset_id', 'word', 'analysis_mode', name='uq_dataset_word_mode'),
    )

class NLTKAnalysis(Base):
    """
    Detailed NLTK analysis results for individual questions
    """
    __tablename__ = "nltk_analysis"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id = Column(String, ForeignKey('questions.id'), nullable=False, unique=True, index=True)
    
    # Sentiment analysis (multiple methods)
    vader_sentiment = Column(JSON, nullable=True)  # VADER scores
    textblob_sentiment = Column(JSON, nullable=True)  # TextBlob scores
    custom_sentiment = Column(JSON, nullable=True)  # Custom model scores
    
    # Named Entity Recognition
    entities = Column(JSON, nullable=True)  # spaCy entities
    
    # Topic modeling
    lda_topics = Column(JSON, nullable=True)  # LDA topic distributions
    topic_keywords = Column(JSON, nullable=True)  # Topic-word associations
    
    # Keyword extraction
    tfidf_keywords = Column(JSON, nullable=True)  # TF-IDF keywords
    yake_keywords = Column(JSON, nullable=True)  # YAKE keywords
    textrank_keywords = Column(JSON, nullable=True)  # TextRank keywords
    
    # Language analysis
    language_detected = Column(String(10), nullable=True, default='en')
    readability_scores = Column(JSON, nullable=True)
    
    # Question classification
    question_classification = Column(JSON, nullable=True)
    intent_analysis = Column(JSON, nullable=True)
    
    # Response analysis
    response_quality_analysis = Column(JSON, nullable=True)
    response_completeness = Column(JSON, nullable=True)
    
    # Processing metadata
    nltk_version = Column(String(50), nullable=True)
    spacy_model = Column(String(100), nullable=True)
    processing_time_seconds = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    question = relationship("Question", back_populates="nltk_analysis")

    # Indexes
    __table_args__ = (
        Index('idx_nltk_question', 'question_id'),
        Index('idx_nltk_created', 'created_at'),
    )

class AnalysisJob(Base):
    """
    Background processing job tracking
    """
    __tablename__ = "analysis_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String, ForeignKey('datasets.id'), nullable=False, index=True)
    
    # Job configuration
    job_type = Column(String(50), nullable=False)  # 'dataset_upload', 'nltk_analysis', 'word_cloud', etc.
    priority = Column(Integer, nullable=False, default=1)
    
    # Job status
    status = Column(String(50), nullable=False, default='pending')  # pending, running, completed, failed
    progress_percentage = Column(Integer, nullable=False, default=0)
    current_step = Column(String(200), nullable=True)
    
    # Results and errors
    result_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    error_traceback = Column(Text, nullable=True)
    
    # Performance metrics
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    processing_duration_seconds = Column(Float, nullable=True)
    
    # Worker information
    worker_id = Column(String(100), nullable=True)
    worker_hostname = Column(String(200), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    dataset = relationship("Dataset", back_populates="analysis_jobs")

    # Indexes
    __table_args__ = (
        Index('idx_job_dataset_type', 'dataset_id', 'job_type'),
        Index('idx_job_status', 'status'),
        Index('idx_job_created', 'created_at'),
        Index('idx_job_priority', 'priority'),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'dataset_id': self.dataset_id,
            'job_type': self.job_type,
            'status': self.status,
            'progress_percentage': self.progress_percentage,
            'current_step': self.current_step,
            'error_message': self.error_message,
            'processing_duration_seconds': self.processing_duration_seconds,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class LLMAnalysisCache(Base):
    """
    Cache for expensive LLM API calls to avoid repeated costs
    """
    __tablename__ = "llm_analysis_cache"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Cache key components
    content_hash = Column(String(64), nullable=False, unique=True, index=True)  # SHA256 of content
    prompt_hash = Column(String(64), nullable=False, index=True)  # SHA256 of prompt template
    model_name = Column(String(100), nullable=False)
    
    # Input and output
    original_content = Column(Text, nullable=False)
    prompt_used = Column(Text, nullable=False)
    llm_response = Column(Text, nullable=False)
    
    # Metadata
    token_count_input = Column(Integer, nullable=True)
    token_count_output = Column(Integer, nullable=True)
    api_cost = Column(Float, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    
    # Usage tracking
    hit_count = Column(Integer, nullable=False, default=1)
    last_accessed = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Indexes
    __table_args__ = (
        Index('idx_cache_content', 'content_hash'),
        Index('idx_cache_prompt', 'prompt_hash'),
        Index('idx_cache_model', 'model_name'),
        Index('idx_cache_accessed', 'last_accessed'),
    )

class UserSession(Base):
    """
    Basic user session tracking (when we re-add authentication)
    """
    __tablename__ = "user_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_token = Column(String(255), nullable=False, unique=True, index=True)
    
    # User identification (placeholder for Clerk integration)
    user_id = Column(String(255), nullable=True, index=True)
    user_email = Column(String(255), nullable=True)
    
    # Session metadata
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    user_agent = Column(String(500), nullable=True)
    
    # Activity tracking
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    datasets_accessed = Column(JSON, nullable=True)  # List of dataset IDs
    
    # Session status
    is_active = Column(Boolean, nullable=False, default=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Indexes
    __table_args__ = (
        Index('idx_session_token', 'session_token'),
        Index('idx_session_user', 'user_id'),
        Index('idx_session_activity', 'last_activity'),
    )

class ApplicationSettings(Base):
    """
    Application configuration and settings
    """
    __tablename__ = "application_settings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    setting_key = Column(String(100), nullable=False, unique=True, index=True)
    setting_value = Column(JSON, nullable=False)
    setting_type = Column(String(50), nullable=False, default='json')  # json, string, number, boolean
    
    # Metadata
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, nullable=False, default=False)  # Can be exposed to frontend
    requires_restart = Column(Boolean, nullable=False, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

# Example initial settings that will be inserted
INITIAL_SETTINGS = [
    {
        'setting_key': 'noise_words',
        'setting_value': ['details', 'page', 'https', 'filevineapp', 'docviewer', 'view', 'source', 'embedding'],
        'setting_type': 'json',
        'description': 'Words to always exclude from word cloud analysis',
        'is_public': True
    },
    {
        'setting_key': 'max_words_per_cloud',
        'setting_value': 50,
        'setting_type': 'number',
        'description': 'Maximum number of words to display in word clouds',
        'is_public': True
    },
    {
        'setting_key': 'default_analysis_mode',
        'setting_value': 'all',
        'setting_type': 'string',
        'description': 'Default analysis mode for new word clouds',
        'is_public': True
    },
    {
        'setting_key': 'enable_llm_analysis',
        'setting_value': True,
        'setting_type': 'boolean',
        'description': 'Enable LLM-powered analysis features',
        'is_public': False
    }
]
