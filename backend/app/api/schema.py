"""
Schema detection and mapping API endpoints
Handles JSON schema detection, field mapping, and analysis configuration
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..core.database import get_db
from ..models.dataset import Dataset, DatasetStatus
from ..models.data_schema import DataSchema, SchemaField, DataType, FieldRole
from ..services.schema_detection_service import SchemaDetectionService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/schema", tags=["schema"])

# Pydantic models for request/response
class FieldMappingRequest(BaseModel):
    field_id: str
    field_role: FieldRole
    data_type: Optional[DataType] = None
    include_in_analysis: bool = True
    display_name: Optional[str] = None

class AnalysisConfigRequest(BaseModel):
    primary_text_fields: List[str]
    secondary_text_fields: Optional[List[str]] = []
    category_fields: Optional[List[str]] = []
    metadata_fields: Optional[List[str]] = []
    exclude_words: Optional[List[str]] = []
    analysis_modes: List[str] = ["all", "verbs", "emotions"]

class SchemaMappingRequest(BaseModel):
    dataset_id: str
    field_mappings: List[FieldMappingRequest]
    analysis_config: AnalysisConfigRequest

@router.post("/detect")
async def detect_schema(
    file: UploadFile = File(..., description="JSON or CSV file for schema detection"),
    dataset_id: str = Form(..., description="Dataset ID to associate schema with"),
    db: Session = Depends(get_db)
):
    """
    Detect schema from uploaded JSON or CSV file
    Returns detected fields, types, and suggested roles
    """
    logger.info(f"🔍 Schema detection request for dataset: {dataset_id}")
    
    try:
        # Verify dataset exists
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        # Check file size before reading to avoid memory issues
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        file_size_mb = file_size / 1024 / 1024
        logger.info(f"📊 File size: {file_size_mb:.2f}MB")
        
        if file_size_mb > 2048:  # 2GB
            raise HTTPException(
                status_code=413, 
                detail="File too large for processing. Maximum size: 2GB"
            )
        elif file_size_mb > 500:  # 500MB - use minimal processing to avoid memory issues
            return await SchemaDetectionService.handle_extremely_large_file_stream(
                file, dataset_id, db
            )
        
        # For smaller files, read normally
        file_content = await file.read()
        
        if file_size_mb > 100:  # 100MB
            logger.warning(f"⚠️ Processing large file: {file_size_mb:.1f}MB")
        
        # Detect schema based on file type
        file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
        
        # Adjust sample size based on file size for faster processing
        if file_size_mb > 500:
            max_sample_records = 25  # Very small sample for huge files
        elif file_size_mb > 100:
            max_sample_records = 35  # Small sample for very large files
        elif file_size_mb > 50:
            max_sample_records = 50  # Medium sample for large files
        elif file_size_mb > 10:
            max_sample_records = 75
        else:
            max_sample_records = 100
            
        logger.info(f"📝 Using sample size: {max_sample_records} records")
        
        if file_extension == 'json' or file.content_type == 'application/json':
            schema_data = SchemaDetectionService.detect_json_schema(
                file_content, file.filename, max_sample_records
            )
            dataset.data_format = 'json'
        elif file_extension == 'csv' or file.content_type == 'text/csv':
            schema_data = SchemaDetectionService.detect_csv_schema(
                file_content, file.filename, max_sample_records
            )
            dataset.data_format = 'csv'
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file format: {file_extension}. Supported: json, csv"
            )
        
        # Create schema records in database
        schema = await SchemaDetectionService.create_schema_from_detection(
            dataset_id, schema_data, db
        )
        
        # Update dataset
        dataset.schema_detected = True
        dataset.supports_flexible_analysis = True
        db.commit()
        
        logger.info(f"✅ Schema detected: {len(schema_data.get('fields', {}))} fields, confidence: {schema_data.get('confidence_score', 0):.2f}")
        
        return {
            "success": True,
            "schema_id": str(schema.id),
            "schema": schema.to_dict(),
            "message": f"Schema detected with {len(schema_data.get('fields', {}))} fields"
        }
        
    except ValueError as e:
        logger.error(f"❌ Schema detection error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Unexpected error during schema detection: {str(e)}")
        raise HTTPException(status_code=500, detail="Schema detection failed")

@router.get("/{dataset_id}")
async def get_dataset_schema(
    dataset_id: str,
    db: Session = Depends(get_db)
):
    """Get the detected schema for a dataset"""
    
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if not dataset.data_schema:
        raise HTTPException(status_code=404, detail="No schema found for this dataset")
    
    return {
        "success": True,
        "schema": dataset.data_schema.to_dict()
    }

@router.post("/mapping")
async def save_field_mapping(
    mapping_request: SchemaMappingRequest,
    db: Session = Depends(get_db)
):
    """
    Save user-defined field mappings and analysis configuration
    """
    logger.info(f"💾 Saving field mapping for dataset: {mapping_request.dataset_id}")
    
    try:
        # Get dataset and schema
        dataset = db.query(Dataset).filter(Dataset.id == mapping_request.dataset_id).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        schema = dataset.data_schema
        if not schema:
            raise HTTPException(status_code=404, detail="No schema found for dataset")
        
        # Update field mappings
        field_mappings = {}
        for field_mapping in mapping_request.field_mappings:
            # Find the schema field
            schema_field = db.query(SchemaField).filter(
                SchemaField.id == field_mapping.field_id
            ).first()
            
            if schema_field:
                # Update field configuration
                schema_field.field_role = field_mapping.field_role
                schema_field.include_in_analysis = field_mapping.include_in_analysis
                
                if field_mapping.data_type:
                    schema_field.user_selected_type = field_mapping.data_type
                
                if field_mapping.display_name:
                    schema_field.display_name = field_mapping.display_name
                
                # Store in mapping dictionary
                field_mappings[schema_field.field_name] = {
                    "role": field_mapping.field_role.value,
                    "type": (field_mapping.data_type or schema_field.detected_type).value,
                    "include_in_analysis": field_mapping.include_in_analysis,
                    "display_name": field_mapping.display_name or schema_field.display_name
                }
        
        # Update schema with field mappings and analysis config
        schema.field_mappings = field_mappings
        schema.analysis_config = mapping_request.analysis_config.model_dump()
        
        # Mark dataset as ready for processing
        dataset.user_mapping_complete = True
        dataset.status = DatasetStatus.VALIDATING
        
        db.commit()
        
        logger.info(f"✅ Field mapping saved: {len(field_mappings)} fields configured")
        
        return {
            "success": True,
            "message": "Field mapping and analysis configuration saved",
            "schema": schema.to_dict()
        }
        
    except Exception as e:
        logger.error(f"❌ Error saving field mapping: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to save field mapping")

@router.get("/suggestions/{dataset_id}")
async def get_field_suggestions(
    dataset_id: str,
    db: Session = Depends(get_db)
):
    """
    Get AI-powered suggestions for field roles and analysis configuration
    """
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    schema = dataset.data_schema
    if not schema:
        raise HTTPException(status_code=404, detail="No schema found for dataset")
    
    # Generate intelligent suggestions
    suggestions = {
        "recommended_primary_text": [],
        "recommended_secondary_text": [],
        "recommended_categories": [],
        "recommended_ignore": [],
        "analysis_modes": ["all", "verbs", "emotions"],
        "confidence_notes": []
    }
    
    for field in schema.schema_fields:
        if field.field_role == FieldRole.PRIMARY_TEXT:
            suggestions["recommended_primary_text"].append({
                "field_id": str(field.id),
                "field_name": field.field_name,
                "confidence": field.confidence_score,
                "reason": "Detected as primary text content"
            })
        elif field.field_role == FieldRole.SECONDARY_TEXT:
            suggestions["recommended_secondary_text"].append({
                "field_id": str(field.id),
                "field_name": field.field_name,
                "confidence": field.confidence_score,
                "reason": "Detected as secondary text content"
            })
        elif field.field_role == FieldRole.CATEGORY:
            suggestions["recommended_categories"].append({
                "field_id": str(field.id),
                "field_name": field.field_name,
                "unique_count": field.unique_count,
                "reason": f"Limited unique values ({field.unique_count})"
            })
        elif field.field_role == FieldRole.IDENTIFIER:
            suggestions["recommended_ignore"].append({
                "field_id": str(field.id),
                "field_name": field.field_name,
                "reason": "Appears to be an identifier"
            })
        
        # Add confidence notes for low-confidence fields
        if field.confidence_score < 0.6:
            suggestions["confidence_notes"].append({
                "field_name": field.field_name,
                "confidence": field.confidence_score,
                "note": "Low confidence in type detection - please review"
            })
    
    return {
        "success": True,
        "suggestions": suggestions
    }

@router.post("/preview")
async def preview_analysis_config(
    dataset_id: str,
    analysis_config: AnalysisConfigRequest,
    db: Session = Depends(get_db)
):
    """
    Preview what data will be analyzed with the given configuration
    """
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    schema = dataset.data_schema
    if not schema:
        raise HTTPException(status_code=404, detail="No schema found for dataset")
    
    # Generate preview
    preview = {
        "fields_to_analyze": [],
        "sample_combined_text": "",
        "estimated_word_count": 0,
        "categories_for_filtering": []
    }
    
    # Get sample data
    sample_records = schema.sample_data[:3] if schema.sample_data else []
    
    for field_name in analysis_config.primary_text_fields + analysis_config.secondary_text_fields:
        # Find the schema field
        schema_field = next(
            (f for f in schema.schema_fields if f.field_name == field_name), 
            None
        )
        
        if schema_field:
            preview["fields_to_analyze"].append({
                "field_name": field_name,
                "display_name": schema_field.display_name,
                "avg_length": schema_field.avg_length,
                "sample_values": schema_field.sample_values[:3]
            })
            
            # Add to sample text
            for record in sample_records:
                if field_name in record and record[field_name]:
                    preview["sample_combined_text"] += str(record[field_name]) + " "
    
    # Estimate word count
    if preview["sample_combined_text"]:
        words_in_sample = len(preview["sample_combined_text"].split())
        # Rough estimate based on sample
        preview["estimated_word_count"] = int(words_in_sample * schema.total_records / len(sample_records)) if sample_records else 0
    
    # Get category information
    for field_name in analysis_config.category_fields:
        schema_field = next(
            (f for f in schema.schema_fields if f.field_name == field_name), 
            None
        )
        
        if schema_field:
            preview["categories_for_filtering"].append({
                "field_name": field_name,
                "unique_count": schema_field.unique_count,
                "sample_values": schema_field.sample_values[:5]
            })
    
    return {
        "success": True,
        "preview": preview
    }
