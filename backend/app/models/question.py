"""
Question model for storing individual query-response pairs
Enhanced with NLTK analysis results and metadata
"""

from sqlalchemy import Column, String, DateTime, Integer, Float, Boolean, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from ..core.database import Base

class Question(Base):
    """Question model for query-response pairs with analysis results"""
    
    __tablename__ = "questions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Dataset relationship
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False, index=True)
    
    # Original CSV data fields
    original_question = Column(Text, nullable=False)
    context = Column(Text, nullable=True)
    ai_response = Column(Text, nullable=True)
    org_id = Column(String(255), nullable=True, index=True)
    org_name = Column(String(255), nullable=True, index=True)
    user_id_from_csv = Column(String(255), nullable=True)  # User ID from CSV (not our system user)
    timestamp_from_csv = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Data validation and quality
    is_valid = Column(Boolean, default=True, nullable=False, index=True)
    validation_errors = Column(JSON, nullable=True)  # List of validation issues
    data_quality_score = Column(Float, nullable=True)  # Individual question quality 0-1
    
    # Basic text metrics
    question_length = Column(Integer, nullable=True)
    response_length = Column(Integer, nullable=True)
    context_length = Column(Integer, nullable=True)
    word_count_question = Column(Integer, nullable=True)
    word_count_response = Column(Integer, nullable=True)
    
    # NLTK Analysis Results (Direct fields for quick access)
    sentiment_score = Column(Float, nullable=True, index=True)  # Compound score -1 to 1
    sentiment_label = Column(String(20), nullable=True, index=True)  # positive, negative, neutral
    sentiment_confidence = Column(Float, nullable=True)
    
    # Question classification
    question_type = Column(String(50), nullable=True, index=True)  # technical_support, billing, feature_request, etc.
    question_intent = Column(String(50), nullable=True)  # information_seeking, complaint, compliment, etc.
    complexity_score = Column(Float, nullable=True)  # 0-1 scale
    urgency_level = Column(String(20), nullable=True)  # low, medium, high, urgent
    
    # Response analysis (if AI response is provided)
    response_relevance_score = Column(Float, nullable=True)  # How relevant the response is 0-1
    response_completeness_score = Column(Float, nullable=True)  # How complete the response is 0-1
    response_quality_score = Column(Float, nullable=True)  # Overall response quality 0-1
    
    # Text similarity metrics
    query_response_similarity = Column(Float, nullable=True)  # Semantic similarity between query and response
    
    # Readability scores
    readability_question = Column(Float, nullable=True)  # Flesch reading ease for question
    readability_response = Column(Float, nullable=True)  # Flesch reading ease for response
    
    # Processing metadata
    processed_at = Column(DateTime(timezone=True), nullable=True)
    processing_version = Column(String(20), nullable=True)  # Version of analysis pipeline used
    requires_reprocessing = Column(Boolean, default=False, nullable=False)
    
    # Row-level metadata from CSV
    csv_row_number = Column(Integer, nullable=True)
    csv_source_info = Column(JSON, nullable=True)  # Additional metadata from CSV
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    dataset = relationship("Dataset", back_populates="questions")
    nltk_analysis = relationship("NLTKAnalysis", back_populates="question", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Question(id={self.id}, dataset_id={self.dataset_id}, type={self.question_type}, sentiment={self.sentiment_label})>"
    
    def to_dict(self, include_full_text=True, include_analysis=True):
        """Convert question object to dictionary"""
        result = {
            "id": str(self.id),
            "dataset_id": str(self.dataset_id),
            "org_id": self.org_id,
            "org_name": self.org_name,
            "user_id_from_csv": self.user_id_from_csv,
            "timestamp_from_csv": self.timestamp_from_csv.isoformat() if self.timestamp_from_csv else None,
            "is_valid": self.is_valid,
            "validation_errors": self.validation_errors,
            "data_quality_score": self.data_quality_score,
            "question_length": self.question_length,
            "response_length": self.response_length,
            "context_length": self.context_length,
            "word_count_question": self.word_count_question,
            "word_count_response": self.word_count_response,
            "csv_row_number": self.csv_row_number,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None
        }
        
        # Include full text if requested (default True)
        if include_full_text:
            result.update({
                "original_question": self.original_question,
                "context": self.context,
                "ai_response": self.ai_response
            })
        else:
            # Include truncated versions for previews
            result.update({
                "original_question": self.original_question[:200] + "..." if len(self.original_question) > 200 else self.original_question,
                "context": self.context[:100] + "..." if self.context and len(self.context) > 100 else self.context,
                "ai_response": self.ai_response[:200] + "..." if self.ai_response and len(self.ai_response) > 200 else self.ai_response
            })
        
        # Include analysis results if requested (default True)
        if include_analysis:
            result.update({
                "sentiment_score": self.sentiment_score,
                "sentiment_label": self.sentiment_label,
                "sentiment_confidence": self.sentiment_confidence,
                "question_type": self.question_type,
                "question_intent": self.question_intent,
                "complexity_score": self.complexity_score,
                "urgency_level": self.urgency_level,
                "response_relevance_score": self.response_relevance_score,
                "response_completeness_score": self.response_completeness_score,
                "response_quality_score": self.response_quality_score,
                "query_response_similarity": self.query_response_similarity,
                "readability_question": self.readability_question,
                "readability_response": self.readability_response
            })
        
        return result
    
    def update_basic_metrics(self):
        """Update basic text metrics"""
        self.question_length = len(self.original_question) if self.original_question else 0
        self.response_length = len(self.ai_response) if self.ai_response else 0
        self.context_length = len(self.context) if self.context else 0
        
        self.word_count_question = len(self.original_question.split()) if self.original_question else 0
        self.word_count_response = len(self.ai_response.split()) if self.ai_response else 0
    
    def update_sentiment_analysis(self, sentiment_results: dict):
        """Update sentiment analysis results"""
        self.sentiment_score = sentiment_results.get("compound_score")
        self.sentiment_label = sentiment_results.get("label")
        self.sentiment_confidence = sentiment_results.get("confidence")
    
    def update_classification(self, classification_results: dict):
        """Update question classification results"""
        self.question_type = classification_results.get("question_type")
        self.question_intent = classification_results.get("intent")
        self.complexity_score = classification_results.get("complexity_score")
        self.urgency_level = classification_results.get("urgency_level")
    
    def update_response_analysis(self, response_analysis: dict):
        """Update response quality analysis"""
        self.response_relevance_score = response_analysis.get("response_relevance")
        self.response_completeness_score = response_analysis.get("response_completeness")
        self.response_quality_score = response_analysis.get("overall_quality")
        self.query_response_similarity = response_analysis.get("similarity_score")
    
    def update_readability(self, readability_results: dict):
        """Update readability scores"""
        self.readability_question = readability_results.get("question_readability")
        self.readability_response = readability_results.get("response_readability")
    
    def mark_as_processed(self, processing_version: str = "1.0"):
        """Mark question as processed"""
        self.processed_at = func.now()
        self.processing_version = processing_version
        self.requires_reprocessing = False
    
    def add_validation_error(self, error_type: str, error_message: str):
        """Add validation error to the question"""
        if self.validation_errors is None:
            self.validation_errors = []
        
        error_entry = {
            "type": error_type,
            "message": error_message,
            "timestamp": func.now().isoformat()
        }
        self.validation_errors.append(error_entry)
        self.is_valid = False
    
    def clear_validation_errors(self):
        """Clear all validation errors"""
        self.validation_errors = []
        self.is_valid = True
    
    @property
    def has_response(self) -> bool:
        """Check if question has an AI response"""
        return self.ai_response is not None and len(self.ai_response.strip()) > 0
    
    @property
    def has_context(self) -> bool:
        """Check if question has context"""
        return self.context is not None and len(self.context.strip()) > 0
    
    @property
    def is_processed(self) -> bool:
        """Check if question has been processed"""
        return self.processed_at is not None and not self.requires_reprocessing
    
    @property
    def sentiment_category(self) -> str:
        """Get sentiment category based on score"""
        if self.sentiment_score is None:
            return "unknown"
        elif self.sentiment_score >= 0.1:
            return "positive"
        elif self.sentiment_score <= -0.1:
            return "negative"
        else:
            return "neutral"
    
    @property
    def complexity_category(self) -> str:
        """Get complexity category based on score"""
        if self.complexity_score is None:
            return "unknown"
        elif self.complexity_score >= 0.7:
            return "high"
        elif self.complexity_score >= 0.4:
            return "medium"
        else:
            return "low"
    
    @property
    def overall_quality_category(self) -> str:
        """Get overall quality category based on various scores"""
        if self.data_quality_score is None:
            return "unknown"
        elif self.data_quality_score >= 0.8:
            return "excellent"
        elif self.data_quality_score >= 0.6:
            return "good"
        elif self.data_quality_score >= 0.4:
            return "fair"
        else:
            return "poor"
