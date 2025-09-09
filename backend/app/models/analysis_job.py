"""
Analysis Job model for tracking background processing tasks
Handles job queue management, progress tracking, and error handling
"""

from sqlalchemy import Column, String, DateTime, Integer, Float, Boolean, Text, ForeignKey, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from ..core.database import Base

class JobType(str, enum.Enum):
    """Background job types"""
    DATASET_UPLOAD = "dataset_upload"
    DATASET_PROCESSING = "dataset_processing"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    TOPIC_MODELING = "topic_modeling"
    ENTITY_EXTRACTION = "entity_extraction"
    KEYWORD_EXTRACTION = "keyword_extraction"
    CLASSIFICATION = "classification"
    WORD_CLOUD_GENERATION = "word_cloud_generation"
    REPORT_GENERATION = "report_generation"
    DATA_EXPORT = "data_export"
    DATASET_REPROCESSING = "dataset_reprocessing"

class JobStatus(str, enum.Enum):
    """Job processing status"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRY = "retry"

class JobPriority(str, enum.Enum):
    """Job priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class AnalysisJob(Base):
    """Analysis job model for background task tracking"""
    
    __tablename__ = "analysis_jobs"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Relationships
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=True, index=True)
    
    # Job metadata
    job_type = Column(Enum(JobType), nullable=False, index=True)
    job_name = Column(String(255), nullable=False)
    job_description = Column(Text, nullable=True)
    
    # Job status and progress
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False, index=True)
    priority = Column(Enum(JobPriority), default=JobPriority.NORMAL, nullable=False)
    progress_percentage = Column(Float, default=0.0, nullable=False)
    current_step = Column(String(255), nullable=True)
    total_steps = Column(Integer, nullable=True)
    
    # Job configuration and parameters
    job_config = Column(JSON, nullable=True)  # Job-specific configuration parameters
    input_parameters = Column(JSON, nullable=True)  # Input parameters for the job
    
    # Results and output
    results = Column(JSON, nullable=True)  # Job results and output data
    output_file_path = Column(String(500), nullable=True)  # Path to output file if applicable
    output_metadata = Column(JSON, nullable=True)  # Metadata about the output
    
    # Error handling
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)  # Detailed error information
    stack_trace = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    
    # Timing information
    estimated_duration = Column(Integer, nullable=True)  # Estimated duration in seconds
    actual_duration = Column(Integer, nullable=True)  # Actual duration in seconds
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Resource usage
    memory_usage_mb = Column(Float, nullable=True)
    cpu_usage_percent = Column(Float, nullable=True)
    
    # Celery integration
    celery_task_id = Column(String(255), nullable=True, unique=True, index=True)
    worker_name = Column(String(255), nullable=True)
    queue_name = Column(String(100), default="default", nullable=False)
    
    # Job dependencies and ordering
    depends_on_job_id = Column(UUID(as_uuid=True), ForeignKey("analysis_jobs.id"), nullable=True)
    job_group_id = Column(String(255), nullable=True, index=True)  # Group related jobs
    
    # Scheduling information
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_config = Column(JSON, nullable=True)  # Cron-like recurrence configuration
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="analysis_jobs")
    dataset = relationship("Dataset", back_populates="analysis_jobs")
    dependent_job = relationship("AnalysisJob", remote_side=[id])  # Self-referencing relationship
    
    def __repr__(self):
        return f"<AnalysisJob(id={self.id}, type={self.job_type}, status={self.status}, progress={self.progress_percentage}%)>"
    
    def to_dict(self, include_sensitive=False):
        """Convert job object to dictionary"""
        result = {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "dataset_id": str(self.dataset_id) if self.dataset_id else None,
            "job_type": self.job_type.value,
            "job_name": self.job_name,
            "job_description": self.job_description,
            "status": self.status.value,
            "priority": self.priority.value,
            "progress_percentage": self.progress_percentage,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "estimated_duration": self.estimated_duration,
            "actual_duration": self.actual_duration,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "is_recurring": self.is_recurring,
            "depends_on_job_id": str(self.depends_on_job_id) if self.depends_on_job_id else None,
            "job_group_id": self.job_group_id,
            "queue_name": self.queue_name,
            "worker_name": self.worker_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Include sensitive data if requested
        if include_sensitive:
            result.update({
                "job_config": self.job_config,
                "input_parameters": self.input_parameters,
                "results": self.results,
                "output_file_path": self.output_file_path,
                "output_metadata": self.output_metadata,
                "error_message": self.error_message,
                "error_details": self.error_details,
                "stack_trace": self.stack_trace,
                "celery_task_id": self.celery_task_id,
                "memory_usage_mb": self.memory_usage_mb,
                "cpu_usage_percent": self.cpu_usage_percent,
                "recurrence_config": self.recurrence_config
            })
        else:
            # Include limited error information for non-sensitive view
            if self.status == JobStatus.FAILED and self.error_message:
                result["error_summary"] = self.error_message[:200]
        
        return result
    
    def update_status(self, status: JobStatus, message: str = None, error_details: dict = None):
        """Update job status with optional message and error details"""
        self.status = status
        
        if status == JobStatus.RUNNING and not self.started_at:
            self.started_at = func.now()
        elif status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
            if not self.completed_at:
                self.completed_at = func.now()
                if self.started_at:
                    self.actual_duration = int((self.completed_at - self.started_at).total_seconds())
        
        if status == JobStatus.FAILED:
            self.error_message = message
            self.error_details = error_details
        elif message:
            self.current_step = message
    
    def update_progress(self, progress: float, current_step: str = None):
        """Update job progress"""
        self.progress_percentage = max(0.0, min(100.0, progress))
        if current_step:
            self.current_step = current_step
    
    def increment_retry(self):
        """Increment retry count"""
        self.retry_count += 1
        self.status = JobStatus.RETRY if self.retry_count < self.max_retries else JobStatus.FAILED
    
    def set_results(self, results: dict, output_file_path: str = None, output_metadata: dict = None):
        """Set job results and output information"""
        self.results = results
        self.output_file_path = output_file_path
        self.output_metadata = output_metadata
    
    def set_resource_usage(self, memory_mb: float = None, cpu_percent: float = None):
        """Update resource usage information"""
        if memory_mb is not None:
            self.memory_usage_mb = memory_mb
        if cpu_percent is not None:
            self.cpu_usage_percent = cpu_percent
    
    def get_duration_readable(self) -> str:
        """Get human-readable duration"""
        duration = self.actual_duration or 0
        if self.status == JobStatus.RUNNING and self.started_at:
            from datetime import datetime
            duration = int((datetime.utcnow() - self.started_at).total_seconds())
        
        if duration < 60:
            return f"{duration} seconds"
        elif duration < 3600:
            return f"{duration//60} minutes {duration%60} seconds"
        else:
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            return f"{hours} hours {minutes} minutes"
    
    def can_retry(self) -> bool:
        """Check if job can be retried"""
        return self.status == JobStatus.FAILED and self.retry_count < self.max_retries
    
    def is_terminal_status(self) -> bool:
        """Check if job is in terminal status (completed/failed/cancelled)"""
        return self.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]
    
    def estimate_remaining_time(self) -> int:
        """Estimate remaining time in seconds based on progress"""
        if self.progress_percentage <= 0 or not self.started_at or self.is_terminal_status():
            return 0
        
        from datetime import datetime
        elapsed = (datetime.utcnow() - self.started_at).total_seconds()
        estimated_total = elapsed / (self.progress_percentage / 100)
        remaining = max(0, estimated_total - elapsed)
        return int(remaining)
    
    @property
    def is_active(self) -> bool:
        """Check if job is currently active (pending, queued, or running)"""
        return self.status in [JobStatus.PENDING, JobStatus.QUEUED, JobStatus.RUNNING, JobStatus.RETRY]
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate based on retry attempts"""
        total_attempts = self.retry_count + 1
        if self.status == JobStatus.COMPLETED:
            return 1.0
        elif self.status == JobStatus.FAILED:
            return 0.0
        else:
            return (total_attempts - self.retry_count) / total_attempts
