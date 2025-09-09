"""
Dataset model for storing uploaded CSV files and processing status
Tracks datasets, their processing status, and metadata
"""

from sqlalchemy import Column, String, DateTime, Integer, Float, Boolean, Text, ForeignKey, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from ..core.database import Base

class DatasetStatus(str, enum.Enum):
    """Dataset processing status enumeration"""
    UPLOADING = "uploading"
    VALIDATING = "validating"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Dataset(Base):
    """Dataset model for uploaded query-response CSV files"""
    
    __tablename__ = "datasets"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User relationship
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Basic dataset information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=False)  # S3 path or local file path
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    
    # Processing status and progress
    status = Column(Enum(DatasetStatus), default=DatasetStatus.UPLOADING, nullable=False, index=True)
    progress_percentage = Column(Float, default=0.0, nullable=False)
    status_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)
    
    # Dataset metrics
    total_questions = Column(Integer, default=0, nullable=False)
    processed_questions = Column(Integer, default=0, nullable=False)
    valid_questions = Column(Integer, default=0, nullable=False)
    invalid_questions = Column(Integer, default=0, nullable=False)
    
    # Analysis results summary
    sentiment_avg = Column(Float, nullable=True)
    sentiment_distribution = Column(JSON, nullable=True)  # {"positive": 0.6, "neutral": 0.3, "negative": 0.1}
    top_topics = Column(JSON, nullable=True)  # List of top topics with scores
    top_entities = Column(JSON, nullable=True)  # List of top entities
    top_keywords = Column(JSON, nullable=True)  # List of top keywords
    
    # Data quality metrics
    avg_question_length = Column(Float, nullable=True)
    avg_response_length = Column(Float, nullable=True)
    avg_complexity_score = Column(Float, nullable=True)
    data_quality_score = Column(Float, nullable=True)  # Overall quality score 0-1
    
    # Processing metadata
    processing_started_at = Column(DateTime(timezone=True), nullable=True)
    processing_completed_at = Column(DateTime(timezone=True), nullable=True)
    analysis_config = Column(JSON, nullable=True)  # Configuration used for analysis
    
    # File validation details
    csv_headers = Column(JSON, nullable=True)  # Original CSV headers
    csv_delimiter = Column(String(10), default=",", nullable=False)
    csv_encoding = Column(String(20), default="utf-8", nullable=False)
    has_header_row = Column(Boolean, default=True, nullable=False)
    
    # Organization data (if present in CSV)
    organizations_count = Column(Integer, default=0, nullable=False)
    organization_names = Column(JSON, nullable=True)  # List of unique org names
    
    # Export and sharing
    is_public = Column(Boolean, default=False, nullable=False)
    shared_with_users = Column(JSON, nullable=True)  # List of user IDs with access
    export_formats_available = Column(JSON, nullable=True)  # Available export formats
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="datasets")
    questions = relationship("Question", back_populates="dataset", cascade="all, delete-orphan")
    analysis_jobs = relationship("AnalysisJob", back_populates="dataset", cascade="all, delete-orphan")
    word_frequencies = relationship("WordFrequency", back_populates="dataset", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Dataset(id={self.id}, name={self.name}, status={self.status}, questions={self.total_questions})>"
    
    def to_dict(self, include_sensitive=False):
        """Convert dataset object to dictionary"""
        result = {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "name": self.name,
            "description": self.description,
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "status": self.status.value,
            "progress_percentage": self.progress_percentage,
            "status_message": self.status_message,
            "total_questions": self.total_questions,
            "processed_questions": self.processed_questions,
            "valid_questions": self.valid_questions,
            "invalid_questions": self.invalid_questions,
            "sentiment_avg": self.sentiment_avg,
            "sentiment_distribution": self.sentiment_distribution,
            "top_topics": self.top_topics,
            "top_entities": self.top_entities,
            "top_keywords": self.top_keywords,
            "avg_question_length": self.avg_question_length,
            "avg_response_length": self.avg_response_length,
            "avg_complexity_score": self.avg_complexity_score,
            "data_quality_score": self.data_quality_score,
            "organizations_count": self.organizations_count,
            "organization_names": self.organization_names,
            "is_public": self.is_public,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "processing_started_at": self.processing_started_at.isoformat() if self.processing_started_at else None,
            "processing_completed_at": self.processing_completed_at.isoformat() if self.processing_completed_at else None,
        }
        
        # Include sensitive data only if requested
        if include_sensitive:
            result.update({
                "file_path": self.file_path,
                "error_details": self.error_details,
                "analysis_config": self.analysis_config,
                "csv_headers": self.csv_headers,
                "shared_with_users": self.shared_with_users
            })
        
        return result
    
    def update_status(self, status: DatasetStatus, message: str = None, error_details: dict = None):
        """Update dataset processing status"""
        self.status = status
        self.status_message = message
        self.error_details = error_details
        
        if status == DatasetStatus.PROCESSING and not self.processing_started_at:
            self.processing_started_at = func.now()
        elif status in [DatasetStatus.COMPLETED, DatasetStatus.FAILED, DatasetStatus.CANCELLED]:
            if not self.processing_completed_at:
                self.processing_completed_at = func.now()
    
    def update_progress(self, progress: float, processed_count: int = None):
        """Update processing progress"""
        self.progress_percentage = max(0.0, min(100.0, progress))
        if processed_count is not None:
            self.processed_questions = processed_count
    
    def update_analysis_summary(self, analysis_results: dict):
        """Update dataset with analysis results summary"""
        if "sentiment" in analysis_results:
            self.sentiment_avg = analysis_results["sentiment"].get("average")
            self.sentiment_distribution = analysis_results["sentiment"].get("distribution")
        
        if "topics" in analysis_results:
            self.top_topics = analysis_results["topics"][:10]  # Top 10 topics
        
        if "entities" in analysis_results:
            self.top_entities = analysis_results["entities"][:20]  # Top 20 entities
        
        if "keywords" in analysis_results:
            self.top_keywords = analysis_results["keywords"][:30]  # Top 30 keywords
        
        if "quality_metrics" in analysis_results:
            metrics = analysis_results["quality_metrics"]
            self.avg_question_length = metrics.get("avg_question_length")
            self.avg_response_length = metrics.get("avg_response_length")
            self.avg_complexity_score = metrics.get("avg_complexity_score")
            self.data_quality_score = metrics.get("overall_quality_score")
    
    def get_processing_duration(self) -> float:
        """Get processing duration in seconds"""
        if self.processing_started_at and self.processing_completed_at:
            return (self.processing_completed_at - self.processing_started_at).total_seconds()
        elif self.processing_started_at:
            # Still processing
            from datetime import datetime
            return (datetime.utcnow() - self.processing_started_at).total_seconds()
        return 0.0
    
    def get_completion_rate(self) -> float:
        """Get completion rate as percentage"""
        if self.total_questions == 0:
            return 0.0
        return (self.processed_questions / self.total_questions) * 100
    
    def get_success_rate(self) -> float:
        """Get success rate for valid questions"""
        if self.processed_questions == 0:
            return 0.0
        return (self.valid_questions / self.processed_questions) * 100
    
    @property
    def is_processing_complete(self) -> bool:
        """Check if dataset processing is complete"""
        return self.status in [DatasetStatus.COMPLETED, DatasetStatus.FAILED, DatasetStatus.CANCELLED]
    
    @property
    def is_ready_for_analysis(self) -> bool:
        """Check if dataset is ready for analysis operations"""
        return self.status == DatasetStatus.COMPLETED and self.valid_questions > 0
    
    @property
    def processing_time_readable(self) -> str:
        """Get human-readable processing time"""
        duration = self.get_processing_duration()
        if duration < 60:
            return f"{duration:.1f} seconds"
        elif duration < 3600:
            return f"{duration/60:.1f} minutes"
        else:
            return f"{duration/3600:.1f} hours"
