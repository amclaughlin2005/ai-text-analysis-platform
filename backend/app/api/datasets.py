"""
Dataset management API endpoints
Handles CSV upload, dataset CRUD operations, and processing status
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from ..core.logging import get_logger
from ..services.dataset_service import DatasetService
from ..services.analysis_service import AnalysisService

logger = get_logger(__name__)
router = APIRouter()

@router.get("/")
async def list_datasets(
    limit: int = Query(default=50, le=100, description="Number of datasets to return"),
    offset: int = Query(default=0, ge=0, description="Number of datasets to skip"),
    db: Session = Depends(get_db)
):
    """List all datasets with pagination"""
    logger.info(f"📊 Listing datasets: limit={limit}, offset={offset}")
    
    return DatasetService.get_datasets(
        limit=limit,
        offset=offset,
        db=db
    )

@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(..., description="CSV file containing query-response pairs"),
    name: str = Form(..., description="Display name for the dataset"),
    description: Optional[str] = Form(None, description="Optional dataset description"),
    db: Session = Depends(get_db)
):
    """Upload and process CSV dataset with comprehensive validation"""
    logger.info(f"📤 Dataset upload request: {file.filename}, name: {name}")
    
    result = await DatasetService.upload_dataset(
        file=file,
        name=name,
        description=description,
        user_id=None,  # Will be set when auth is enabled
        db=db
    )
    
    return result

@router.get("/{dataset_id}")
async def get_dataset(dataset_id: str, db: Session = Depends(get_db)):
    """Get dataset details with analysis results"""
    logger.info(f"📋 Getting dataset details: {dataset_id}")
    
    return DatasetService.get_dataset(dataset_id, db)

@router.delete("/{dataset_id}")
async def delete_dataset(dataset_id: str, db: Session = Depends(get_db)):
    """Delete dataset and all associated data"""
    logger.info(f"🗑️ Deleting dataset: {dataset_id}")
    
    return DatasetService.delete_dataset(dataset_id, db)

@router.post("/{dataset_id}/reprocess")
async def reprocess_dataset(
    dataset_id: str,
    analysis_mode: str = Form(default="all", description="Analysis mode for word frequency generation"),
    selected_columns: Optional[List[int]] = Form(default=[1, 2], description="CSV columns to analyze"),
    force_regenerate: bool = Form(default=False, description="Force regeneration of existing data"),
    db: Session = Depends(get_db)
):
    """Trigger dataset reprocessing and word frequency generation"""
    logger.info(f"🔄 Reprocessing dataset: {dataset_id} with mode: {analysis_mode}")
    
    # Verify dataset exists
    dataset = DatasetService.get_dataset(dataset_id, db)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Generate word frequencies
    word_frequencies = AnalysisService.generate_word_frequencies(
        dataset_id=dataset_id,
        analysis_mode=analysis_mode,
        selected_columns=selected_columns,
        db=db,
        force_regenerate=force_regenerate
    )
    
    return {
        "success": True,
        "message": f"Dataset '{dataset['name']}' reprocessed successfully",
        "analysis_mode": analysis_mode,
        "word_frequencies_generated": len(word_frequencies),
        "word_frequencies": word_frequencies[:20]  # Return first 20 for preview
    }

@router.get("/{dataset_id}/word-frequencies")
async def get_word_frequencies(
    dataset_id: str,
    analysis_mode: str = Query(default="all", description="Analysis mode filter"),
    limit: int = Query(default=50, le=100, description="Number of words to return"),
    db: Session = Depends(get_db)
):
    """Get word frequencies for dataset visualization"""
    logger.info(f"📊 Getting word frequencies: {dataset_id} - {analysis_mode}")
    
    word_frequencies = AnalysisService.generate_word_frequencies(
        dataset_id=dataset_id,
        analysis_mode=analysis_mode,
        db=db,
        force_regenerate=False  # Use cached if available
    )
    
    return {
        "dataset_id": dataset_id,
        "analysis_mode": analysis_mode,
        "word_count": len(word_frequencies),
        "words": word_frequencies[:limit]
    }
