"""
Data Schema models for flexible JSON/CSV data ingestion
Supports dynamic schema detection and user-defined field mappings
"""

from sqlalchemy import Column, String, DateTime, Integer, Float, Boolean, Text, ForeignKey, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from ..core.database import Base

class DataType(str, enum.Enum):
    """Supported data types for schema detection"""
    TEXT = "text"
    NUMBER = "number"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    EMAIL = "email"
    URL = "url"
    JSON_OBJECT = "json_object"
    JSON_ARRAY = "json_array"
    
class FieldRole(str, enum.Enum):
    """Role that a field plays in analysis"""
    PRIMARY_TEXT = "primary_text"        # Main text to analyze (like question)
    SECONDARY_TEXT = "secondary_text"    # Supporting text (like response/context)
    CATEGORY = "category"                # Categorical data for grouping
    METADATA = "metadata"                # Additional information
    IDENTIFIER = "identifier"            # Unique identifiers
    TIMESTAMP = "timestamp"              # Time information
    IGNORE = "ignore"                    # Skip this field
    
class DataSchema(Base):
    """Schema definition for uploaded datasets"""
    
    __tablename__ = "data_schemas"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Dataset relationship
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False, index=True)
    
    # Schema metadata
    schema_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(20), default="1.0", nullable=False)
    
    # File format information
    file_format = Column(String(20), nullable=False)  # json, csv, xml, etc.
    detected_encoding = Column(String(50), nullable=True)
    detected_delimiter = Column(String(10), nullable=True)  # for CSV
    has_headers = Column(Boolean, default=True, nullable=False)
    
    # Schema structure (auto-detected from file)
    raw_schema = Column(JSON, nullable=False)  # Original detected schema
    sample_data = Column(JSON, nullable=True)  # Sample rows for preview
    total_records = Column(Integer, default=0, nullable=False)
    
    # User-defined configuration
    field_mappings = Column(JSON, nullable=False)  # User's field mapping choices
    analysis_config = Column(JSON, nullable=False)  # How to analyze this data
    
    # Schema validation
    is_valid = Column(Boolean, default=True, nullable=False)
    validation_errors = Column(JSON, nullable=True)
    confidence_score = Column(Float, default=0.0, nullable=False)  # 0-1 schema detection confidence
    
    # Processing options
    process_nested_objects = Column(Boolean, default=False, nullable=False)
    flatten_arrays = Column(Boolean, default=True, nullable=False)
    max_nesting_depth = Column(Integer, default=3, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    dataset = relationship("Dataset", back_populates="data_schema")
    schema_fields = relationship("SchemaField", back_populates="schema", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DataSchema(id={self.id}, dataset_id={self.dataset_id}, format={self.file_format})>"
    
    def to_dict(self):
        """Convert schema to dictionary"""
        return {
            "id": str(self.id),
            "dataset_id": str(self.dataset_id),
            "schema_name": self.schema_name,
            "description": self.description,
            "version": self.version,
            "file_format": self.file_format,
            "detected_encoding": self.detected_encoding,
            "detected_delimiter": self.detected_delimiter,
            "has_headers": self.has_headers,
            "raw_schema": self.raw_schema,
            "sample_data": self.sample_data,
            "total_records": self.total_records,
            "field_mappings": self.field_mappings,
            "analysis_config": self.analysis_config,
            "is_valid": self.is_valid,
            "validation_errors": self.validation_errors,
            "confidence_score": self.confidence_score,
            "process_nested_objects": self.process_nested_objects,
            "flatten_arrays": self.flatten_arrays,
            "max_nesting_depth": self.max_nesting_depth,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "fields": [field.to_dict() for field in self.schema_fields] if self.schema_fields else []
        }

class SchemaField(Base):
    """Individual field definition within a schema"""
    
    __tablename__ = "schema_fields"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Schema relationship
    schema_id = Column(UUID(as_uuid=True), ForeignKey("data_schemas.id"), nullable=False, index=True)
    
    # Field identification
    field_name = Column(String(255), nullable=False)  # Original field name
    field_path = Column(String(500), nullable=True)   # JSON path for nested fields (e.g., "user.profile.name")
    display_name = Column(String(255), nullable=True) # User-friendly name
    
    # Data type information
    detected_type = Column(Enum(DataType), nullable=False)
    suggested_type = Column(Enum(DataType), nullable=True)  # AI suggestion if different
    user_selected_type = Column(Enum(DataType), nullable=True)  # User override
    
    # Role in analysis
    field_role = Column(Enum(FieldRole), default=FieldRole.METADATA, nullable=False)
    is_required = Column(Boolean, default=False, nullable=False)
    include_in_analysis = Column(Boolean, default=True, nullable=False)
    
    # Statistical information
    sample_values = Column(JSON, nullable=True)      # Sample values from data
    unique_count = Column(Integer, nullable=True)    # Number of unique values
    null_count = Column(Integer, nullable=True)      # Number of null values
    min_length = Column(Integer, nullable=True)      # Min string length
    max_length = Column(Integer, nullable=True)      # Max string length
    avg_length = Column(Float, nullable=True)        # Average string length
    
    # Validation rules
    validation_rules = Column(JSON, nullable=True)   # Custom validation rules
    transformation_rules = Column(JSON, nullable=True)  # Data transformation rules
    
    # Field ordering and grouping
    display_order = Column(Integer, default=0, nullable=False)
    field_group = Column(String(100), nullable=True)  # Group similar fields
    
    # AI suggestions and confidence
    ai_suggestions = Column(JSON, nullable=True)     # AI-generated suggestions for this field
    confidence_score = Column(Float, default=0.0, nullable=False)  # Confidence in type detection
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    schema = relationship("DataSchema", back_populates="schema_fields")
    
    def __repr__(self):
        return f"<SchemaField(name={self.field_name}, type={self.detected_type}, role={self.field_role})>"
    
    def to_dict(self):
        """Convert field to dictionary"""
        return {
            "id": str(self.id),
            "schema_id": str(self.schema_id),
            "field_name": self.field_name,
            "field_path": self.field_path,
            "display_name": self.display_name,
            "detected_type": self.detected_type.value,
            "suggested_type": self.suggested_type.value if self.suggested_type else None,
            "user_selected_type": self.user_selected_type.value if self.user_selected_type else None,
            "field_role": self.field_role.value,
            "is_required": self.is_required,
            "include_in_analysis": self.include_in_analysis,
            "sample_values": self.sample_values,
            "unique_count": self.unique_count,
            "null_count": self.null_count,
            "min_length": self.min_length,
            "max_length": self.max_length,
            "avg_length": self.avg_length,
            "validation_rules": self.validation_rules,
            "transformation_rules": self.transformation_rules,
            "display_order": self.display_order,
            "field_group": self.field_group,
            "ai_suggestions": self.ai_suggestions,
            "confidence_score": self.confidence_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def effective_type(self) -> DataType:
        """Get the effective data type (user override > suggested > detected)"""
        return self.user_selected_type or self.suggested_type or self.detected_type
    
    @property
    def is_text_field(self) -> bool:
        """Check if this field contains text suitable for analysis"""
        return self.effective_type in [DataType.TEXT] and self.field_role in [
            FieldRole.PRIMARY_TEXT, FieldRole.SECONDARY_TEXT
        ]
    
    @property
    def is_categorical(self) -> bool:
        """Check if this field is categorical"""
        return self.field_role == FieldRole.CATEGORY or (
            self.unique_count and self.unique_count < 100  # Heuristic for categorical
        )

class DataRecord(Base):
    """Flexible data record that can store any type of data"""
    
    __tablename__ = "data_records"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Dataset relationship
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False, index=True)
    
    # Raw data storage
    raw_data = Column(JSON, nullable=False)          # Original record data
    processed_data = Column(JSON, nullable=True)     # Processed/normalized data
    
    # Record metadata
    record_index = Column(Integer, nullable=False, index=True)  # Original position in file
    source_row = Column(Integer, nullable=True)      # Row number in source file
    record_hash = Column(String(64), nullable=True, index=True)  # Hash for deduplication
    
    # Data quality
    is_valid = Column(Boolean, default=True, nullable=False, index=True)
    validation_errors = Column(JSON, nullable=True)
    data_quality_score = Column(Float, nullable=True)
    
    # Processing status
    is_processed = Column(Boolean, default=False, nullable=False, index=True)
    processing_errors = Column(JSON, nullable=True)
    processing_version = Column(String(20), nullable=True)
    
    # Analysis results (flexible storage)
    analysis_results = Column(JSON, nullable=True)   # Store all analysis results
    extracted_text = Column(Text, nullable=True)     # Combined text for word cloud
    categories = Column(JSON, nullable=True)         # Extracted categories
    metadata = Column(JSON, nullable=True)           # Additional metadata
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    dataset = relationship("Dataset", back_populates="data_records")
    
    def __repr__(self):
        return f"<DataRecord(id={self.id}, dataset_id={self.dataset_id}, index={self.record_index})>"
    
    def to_dict(self, include_raw_data=True):
        """Convert record to dictionary"""
        result = {
            "id": str(self.id),
            "dataset_id": str(self.dataset_id),
            "record_index": self.record_index,
            "source_row": self.source_row,
            "record_hash": self.record_hash,
            "is_valid": self.is_valid,
            "validation_errors": self.validation_errors,
            "data_quality_score": self.data_quality_score,
            "is_processed": self.is_processed,
            "processing_errors": self.processing_errors,
            "processing_version": self.processing_version,
            "analysis_results": self.analysis_results,
            "extracted_text": self.extracted_text,
            "categories": self.categories,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None
        }
        
        if include_raw_data:
            result.update({
                "raw_data": self.raw_data,
                "processed_data": self.processed_data
            })
        
        return result
    
    def get_field_value(self, field_path: str):
        """Get value from raw_data using field path (supports nested access)"""
        if not self.raw_data:
            return None
            
        try:
            # Split path and navigate nested structure
            keys = field_path.split('.')
            value = self.raw_data
            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key)
                elif isinstance(value, list) and key.isdigit():
                    index = int(key)
                    value = value[index] if 0 <= index < len(value) else None
                else:
                    return None
            return value
        except (KeyError, IndexError, ValueError, TypeError):
            return None
    
    def set_field_value(self, field_path: str, value):
        """Set value in processed_data using field path"""
        if self.processed_data is None:
            self.processed_data = {}
            
        # Split path and create nested structure
        keys = field_path.split('.')
        current = self.processed_data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
