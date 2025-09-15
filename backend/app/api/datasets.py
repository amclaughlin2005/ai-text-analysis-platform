"""
Dataset management API endpoints
Handles CSV upload, dataset CRUD operations, and processing status
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from ..core.database import get_db
from ..core.logging import get_logger
from ..services.dataset_service import DatasetService
from ..services.analysis_service import AnalysisService

logger = get_logger(__name__)
router = APIRouter()

@router.get("/")
@router.get("")
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

@router.get("/{dataset_id}/columns")
async def get_dataset_columns(dataset_id: str, db: Session = Depends(get_db)):
    """Get dataset column information for filtering"""
    logger.info(f"📊 Getting column info for dataset: {dataset_id}")
    
    try:
        from sqlalchemy import text
        
        # Check if dataset exists
        dataset_sql = text("SELECT name FROM datasets WHERE id = :dataset_id")
        dataset_result = db.execute(dataset_sql, {"dataset_id": dataset_id}).fetchone()
        
        if not dataset_result:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        # Return standard column structure for Q&A datasets
        return {
            "success": True,
            "columns": [
                {
                    "index": 0,
                    "name": "Questions", 
                    "type": "text",
                    "description": "Original questions from the dataset",
                    "sample": "Sample question text..."
                },
                {
                    "index": 1,
                    "name": "Responses",
                    "type": "text", 
                    "description": "AI responses and answers",
                    "sample": "Sample response text..."
                }
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get columns for dataset {dataset_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get dataset columns: {str(e)}"
        )

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

@router.get("/debug/schema")
async def debug_questions_schema(db: Session = Depends(get_db)):
    """Debug endpoint to inspect questions table schema"""
    try:
        # Get table structure from PostgreSQL information_schema
        schema_sql = text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'questions'
            ORDER BY ordinal_position
        """)
        
        result = db.execute(schema_sql).fetchall()
        
        columns = []
        for row in result:
            columns.append({
                "column_name": row.column_name,
                "data_type": row.data_type,
                "is_nullable": row.is_nullable,
                "column_default": row.column_default
            })
        
        # Skip constraints for now - just get basic schema
        constraints = []
        
        return {
            "table_name": "questions",
            "columns": columns,
            "constraints": constraints,
            "total_columns": len(columns)
        }
        
    except Exception as e:
        return {"error": str(e), "message": "Failed to get schema info"}

@router.get("/questions")
async def get_dataset_questions(
    dataset_id: str = Query(..., description="Dataset ID to fetch questions for"),
    db: Session = Depends(get_db)
):
    """Get questions for a dataset (simple version for table view)"""
    try:
        # Use the same query as word cloud API since that works
        questions_sql = text("SELECT original_question, ai_response FROM questions WHERE dataset_id = :dataset_id ORDER BY csv_row_number ASC")
        questions_result = db.execute(questions_sql, {"dataset_id": dataset_id}).fetchall()
        
        # Format for table view
        questions = []
        for i, row in enumerate(questions_result):
            questions.append({
                "id": i + 1,
                "question": str(row[0]) if row[0] else "",
                "response": str(row[1]) if row[1] else "",
                "created": None
            })
        
        return {
            "questions": questions,
            "total": len(questions)
        }
        
    except Exception as e:
        logger.error(f"Questions API error: {e}")
        return {
            "questions": [],
            "total": 0,
            "error": str(e)
        }
