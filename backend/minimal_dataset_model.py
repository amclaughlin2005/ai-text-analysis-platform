"""
Minimal Dataset model for Railway compatibility
Only includes fields that exist in the Railway database
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Enum, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from datetime import datetime
from ..core.database import Base

class DatasetStatus(enum.Enum):
    """Dataset processing status"""
    UPLOADING = "uploading"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class MinimalDataset(Base):
    """Minimal dataset model that only uses existing Railway database columns"""
    
    __tablename__ = "datasets"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Only the most basic fields that definitely exist
    name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    original_filename = Column(String(255), nullable=False)  
    file_size = Column(Integer, nullable=False)
    status = Column(Enum(DatasetStatus), default=DatasetStatus.PROCESSING, nullable=False)
    
    # Timestamps (these usually exist)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
