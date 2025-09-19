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

@router.get("/debug/orgs/{dataset_id}")
async def debug_organization_data(dataset_id: str, db: Session = Depends(get_db)):
    """Debug endpoint to check organization data formatting"""
    try:
        # Get sample organization data
        org_sql = text("""
            SELECT org_name, COUNT(*) as count 
            FROM questions 
            WHERE dataset_id = :dataset_id AND org_name IS NOT NULL 
            GROUP BY org_name 
            ORDER BY count DESC 
            LIMIT 20
        """)
        
        orgs = db.execute(org_sql, {"dataset_id": dataset_id}).fetchall()
        
        # Check specific organization
        singleton_exact = text("""
            SELECT COUNT(*) 
            FROM questions 
            WHERE dataset_id = :dataset_id AND org_name = 'Singleton Schreiber, LLP'
        """)
        singleton_count = db.execute(singleton_exact, {"dataset_id": dataset_id}).scalar()
        
        # Check similar organizations (case insensitive, partial match)
        singleton_like = text("""
            SELECT org_name, COUNT(*) 
            FROM questions 
            WHERE dataset_id = :dataset_id AND org_name ILIKE '%singleton%' 
            GROUP BY org_name
        """)
        singleton_variations = db.execute(singleton_like, {"dataset_id": dataset_id}).fetchall()
        
        return {
            "dataset_id": dataset_id,
            "top_organizations": [{"name": org[0], "count": org[1]} for org in orgs],
            "singleton_exact_match": singleton_count,
            "singleton_variations": [{"name": var[0], "count": var[1]} for var in singleton_variations],
            "total_questions": db.execute(text("SELECT COUNT(*) FROM questions WHERE dataset_id = :dataset_id"), {"dataset_id": dataset_id}).scalar()
        }
        
    except Exception as e:
        return {"error": str(e)}

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

@router.get("/{dataset_id}/questions")
async def get_dataset_questions(
    dataset_id: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=100),
    org_names: Optional[str] = Query(None, description="Comma-separated organization names"),
    user_emails: Optional[str] = Query(None, description="Comma-separated user emails"),
    start_date: Optional[str] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)"),
    include_words: Optional[str] = Query(None, description="Comma-separated words to include"),
    exclude_words: Optional[str] = Query(None, description="Comma-separated words to exclude"),
    db: Session = Depends(get_db)
):
    """Get questions for a dataset with pagination and filtering (table view)"""
    try:
        logger.info(f"Fetching questions for dataset {dataset_id} with filters")
        
        # Parse filter parameters
        filters = {}
        if org_names:
            filters['org_names'] = [org.strip() for org in org_names.split(',') if org.strip()]
        if user_emails:
            filters['user_emails'] = [email.strip() for email in user_emails.split(',') if email.strip()]
        if start_date:
            filters['start_date'] = start_date
        if end_date:
            filters['end_date'] = end_date
        if include_words:
            filters['include_words'] = [word.strip() for word in include_words.split(',') if word.strip()]
        if exclude_words:
            filters['exclude_words'] = [word.strip() for word in exclude_words.split(',') if word.strip()]
        
        logger.info(f"📋 Applied filters: {filters}")
        
        # Build dynamic query with filters
        base_query = """
            SELECT id, original_question, ai_response, org_name, user_id_from_csv, 
                   timestamp_from_csv, created_at, csv_row_number
            FROM questions 
            WHERE dataset_id = :dataset_id
        """
        
        params = {"dataset_id": dataset_id}
        where_conditions = []
        
        # Apply filters
        if filters.get('org_names'):
            logger.info(f"🔍 Filtering by organizations: {filters['org_names']}")
            
            # Debug: Check what organizations actually exist in the database
            debug_orgs_sql = text("SELECT DISTINCT org_name FROM questions WHERE dataset_id = :dataset_id AND org_name IS NOT NULL LIMIT 20")
            debug_orgs = db.execute(debug_orgs_sql, {"dataset_id": dataset_id}).fetchall()
            logger.info(f"📋 Sample organizations in database: {[org[0] for org in debug_orgs]}")
            
            # Use flexible matching: case-insensitive and trimmed
            org_conditions = []
            for i, org in enumerate(filters['org_names']):
                # Normalize the search term: trim whitespace and convert to lowercase
                normalized_org = org.strip().lower()
                org_conditions.append(f"LOWER(TRIM(org_name)) = :org_{i}")
                params[f'org_{i}'] = normalized_org
                logger.info(f"🎯 Looking for flexible match: '{org}' -> normalized: '{normalized_org}'")
            
            if org_conditions:
                where_conditions.append(f"({' OR '.join(org_conditions)})")
        
        if filters.get('user_emails'):
            logger.info(f"🔍 Filtering by user emails: {filters['user_emails']}")
            
            # Use flexible matching for emails too: case-insensitive and trimmed
            email_conditions = []
            for i, email in enumerate(filters['user_emails']):
                # Normalize the search term: trim whitespace and convert to lowercase
                normalized_email = email.strip().lower()
                email_conditions.append(f"LOWER(TRIM(user_id_from_csv)) = :email_{i}")
                params[f'email_{i}'] = normalized_email
                logger.info(f"📧 Looking for flexible email match: '{email}' -> normalized: '{normalized_email}'")
            
            if email_conditions:
                where_conditions.append(f"({' OR '.join(email_conditions)})")
        
        if filters.get('start_date'):
            where_conditions.append("timestamp_from_csv >= :start_date")
            params['start_date'] = filters['start_date']
        
        if filters.get('end_date'):
            where_conditions.append("timestamp_from_csv <= :end_date")
            params['end_date'] = filters['end_date']
        
        if filters.get('include_words'):
            logger.info(f"🔍 Filtering by include words: {filters['include_words']}")
            for i, word in enumerate(filters['include_words']):
                # Trim the word but keep case for text search
                normalized_word = word.strip()
                where_conditions.append(f"(original_question ILIKE :include_word_{i} OR ai_response ILIKE :include_word_{i})")
                params[f'include_word_{i}'] = f'%{normalized_word}%'
                logger.info(f"✅ Include word filter: '{word}' -> '{normalized_word}'")
        
        if filters.get('exclude_words'):
            logger.info(f"🔍 Filtering by exclude words: {filters['exclude_words']}")
            for i, word in enumerate(filters['exclude_words']):
                # Trim the word but keep case for text search
                normalized_word = word.strip()
                where_conditions.append(f"NOT (original_question ILIKE :exclude_word_{i} OR ai_response ILIKE :exclude_word_{i})")
                params[f'exclude_word_{i}'] = f'%{normalized_word}%'
                logger.info(f"❌ Exclude word filter: '{word}' -> '{normalized_word}'")
        
        # Build final query
        if where_conditions:
            base_query += " AND " + " AND ".join(where_conditions)
        
        # Add ordering and pagination
        count_query = f"SELECT COUNT(*) FROM ({base_query}) as filtered_questions"
        paginated_query = f"{base_query} ORDER BY csv_row_number ASC LIMIT :limit OFFSET :offset"
        
        logger.info(f"🔍 Final count query: {count_query}")
        logger.info(f"🔍 Query parameters: {params}")
        
        # Get total count
        total_result = db.execute(text(count_query), params)
        total = total_result.scalar()
        
        logger.info(f"📊 Query result: {total} records found")
        
        # Get paginated results
        params['limit'] = per_page
        params['offset'] = (page - 1) * per_page
        
        questions_result = db.execute(text(paginated_query), params).fetchall()
        
        # Format for table view
        questions = []
        for row in questions_result:
            questions.append({
                "id": str(row[0]) if row[0] else "",
                "original_question": str(row[1]) if row[1] else "",
                "ai_response": str(row[2]) if row[2] else "",
                "org_name": str(row[3]) if row[3] else "",
                "user_id_from_csv": str(row[4]) if row[4] else "",
                "timestamp_from_csv": row[5].isoformat() if row[5] else "",
                "created_at": row[6].isoformat() if row[6] else ""
            })
        
        logger.info(f"✅ Returned {len(questions)} questions (filtered from {total} total)")
        
        return {
            "success": True,
            "data": questions,
            "total": total,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_count": total,
                "total_pages": (total + per_page - 1) // per_page,
                "has_next": page * per_page < total,
                "has_prev": page > 1
            },
            "filters_applied": filters
        }
        
    except Exception as e:
        logger.error(f"Questions API error for dataset {dataset_id}: {e}")
        return {
            "success": False,
            "data": [],
            "total": 0,
            "error": str(e),
            "pagination": {
                "page": 1,
                "per_page": per_page,
                "total_count": 0,
                "total_pages": 0
            }
        }

@router.post("/{dataset_id}/append")
async def append_data_to_dataset(
    dataset_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Append new data to an existing dataset"""
    try:
        from ..services.dataset_service import DatasetService
        from ..services.railway_question_service import RailwayQuestionService
        
        logger.info(f"📝 Appending data to dataset: {dataset_id}")
        logger.info(f"📁 File: {file.filename}, Size: {file.size} bytes")
        
        # Verify dataset exists
        existing_dataset = DatasetService.get_dataset(dataset_id, db)
        if not existing_dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        # Read and validate file
        file_content = await file.read()
        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Validate file type
        if not file.filename.lower().endswith(('.csv', '.json')):
            raise HTTPException(status_code=400, detail="Only CSV and JSON files are supported")
        
        # Process the file and append questions
        try:
            # Use the Railway question service to append questions
            questions_created = await RailwayQuestionService.append_questions_to_dataset(
                dataset_id=dataset_id,
                file_content=file_content,
                filename=file.filename,
                db=db
            )
            
            # Update dataset statistics
            DatasetService.update_dataset_stats(dataset_id, db)
            
            logger.info(f"✅ Successfully appended {questions_created} questions to dataset {dataset_id}")
            
            return {
                "success": True,
                "message": f"Successfully appended {questions_created} questions to dataset",
                "dataset_id": dataset_id,
                "questions_added": questions_created,
                "filename": file.filename
            }
            
        except Exception as processing_error:
            logger.error(f"❌ Failed to process appended file: {processing_error}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process file: {str(processing_error)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Append data operation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Append operation failed: {str(e)}"
        )

@router.post("/merge")
async def merge_datasets(
    source_dataset_ids: List[str] = Form(..., description="List of dataset IDs to merge"),
    target_name: str = Form(..., description="Name for the new merged dataset"),
    target_description: Optional[str] = Form(None, description="Optional description for merged dataset"),
    delete_source: bool = Form(False, description="Whether to delete source datasets after merge"),
    db: Session = Depends(get_db)
):
    """Merge multiple datasets into a new dataset"""
    try:
        import uuid
        from ..models.dataset import Dataset
        from ..models.question import Question
        
        logger.info(f"🔗 Starting merge operation: {len(source_dataset_ids)} datasets -> '{target_name}'")
        
        if len(source_dataset_ids) < 2:
            raise HTTPException(status_code=400, detail="At least 2 datasets required for merge")
        
        # Verify all source datasets exist
        source_datasets = []
        total_questions = 0
        
        for dataset_id in source_dataset_ids:
            dataset_sql = text("SELECT id, name, filename FROM datasets WHERE id = :dataset_id")
            dataset_result = db.execute(dataset_sql, {"dataset_id": dataset_id}).fetchone()
            
            if not dataset_result:
                raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")
            
            # Count questions in this dataset
            count_sql = text("SELECT COUNT(*) FROM questions WHERE dataset_id = :dataset_id")
            question_count = db.execute(count_sql, {"dataset_id": dataset_id}).scalar()
            
            source_datasets.append({
                "id": dataset_result[0],
                "name": dataset_result[1], 
                "filename": dataset_result[2],
                "question_count": question_count
            })
            total_questions += question_count
            
        if total_questions == 0:
            raise HTTPException(status_code=400, detail="No questions found in source datasets")
        
        logger.info(f"📊 Source datasets validation complete: {total_questions} total questions")
        
        # Create new target dataset
        target_dataset_id = str(uuid.uuid4())
        
        create_dataset_sql = text("""
            INSERT INTO datasets (id, name, filename, file_size, file_path, original_filename, 
                                created_at, updated_at, upload_status, processing_status, status, 
                                total_questions, processed_questions, valid_questions, invalid_questions,
                                csv_delimiter, csv_encoding, has_header_row, organizations_count, is_public,
                                total_rows, total_columns, progress_percentage, questions_count)
            VALUES (:id, :name, :filename, :file_size, :file_path, :original_filename,
                   NOW(), NOW(), 'completed', 'completed', 'completed',
                   :total_questions, :processed_questions, :valid_questions, :invalid_questions,
                   ',', 'utf-8', TRUE, 0, FALSE,
                   :total_rows, 2, 100.0, :questions_count)
        """)
        
        merged_filename = f"merged_{len(source_dataset_ids)}_datasets.json"
        merged_file_path = f"/merged/{target_dataset_id}/{merged_filename}"
        estimated_size = total_questions * 500  # Rough estimate
        
        db.execute(create_dataset_sql, {
            "id": target_dataset_id,
            "name": target_name,
            "filename": merged_filename,
            "file_size": estimated_size,
            "file_path": merged_file_path,
            "original_filename": merged_filename,
            "total_questions": total_questions,
            "processed_questions": total_questions,
            "valid_questions": total_questions,
            "invalid_questions": 0,
            "total_rows": total_questions,  # Each question is a row
            "questions_count": total_questions  # Total questions count
        })
        
        # Copy all questions from source datasets to target dataset
        questions_copied = 0
        
        for source_dataset in source_datasets:
            copy_questions_sql = text("""
                INSERT INTO questions (id, dataset_id, original_question, ai_response, org_name, user_id_from_csv, csv_row_number, is_valid, created_at, updated_at)
                SELECT 
                    gen_random_uuid() as id,
                    :target_dataset_id as dataset_id,
                    original_question,
                    ai_response, 
                    org_name,
                    user_id_from_csv,
                    csv_row_number,
                    is_valid,
                    NOW() as created_at,
                    NOW() as updated_at
                FROM questions 
                WHERE dataset_id = :source_dataset_id
            """)
            
            result = db.execute(copy_questions_sql, {
                "target_dataset_id": target_dataset_id,
                "source_dataset_id": source_dataset["id"]
            })
            
            copied_count = result.rowcount if hasattr(result, 'rowcount') else source_dataset["question_count"]
            questions_copied += copied_count
            
            logger.info(f"✅ Copied {copied_count} questions from dataset '{source_dataset['name']}'")
        
        # Update target dataset with actual counts
        update_dataset_sql = text("""
            UPDATE datasets 
            SET file_size = :actual_size,
                total_questions = :actual_questions,
                processed_questions = :actual_questions,
                valid_questions = :actual_questions,
                total_rows = :actual_questions,
                questions_count = :actual_questions
            WHERE id = :dataset_id
        """)
        
        db.execute(update_dataset_sql, {
            "dataset_id": target_dataset_id,
            "actual_size": questions_copied * 150,  # More accurate estimate based on actual data
            "actual_questions": questions_copied
        })
        
        # Delete source datasets if requested
        deleted_datasets = []
        if delete_source:
            for source_dataset in source_datasets:
                try:
                    # Delete questions first
                    delete_questions_sql = text("DELETE FROM questions WHERE dataset_id = :dataset_id")
                    db.execute(delete_questions_sql, {"dataset_id": source_dataset["id"]})
                    
                    # Delete dataset
                    delete_dataset_sql = text("DELETE FROM datasets WHERE id = :dataset_id")
                    db.execute(delete_dataset_sql, {"dataset_id": source_dataset["id"]})
                    
                    deleted_datasets.append(source_dataset["name"])
                    logger.info(f"🗑️ Deleted source dataset '{source_dataset['name']}'")
                    
                except Exception as delete_error:
                    logger.warning(f"⚠️ Failed to delete dataset {source_dataset['id']}: {delete_error}")
        
        # Commit all changes
        db.commit()
        
        logger.info(f"🎉 Merge completed successfully: {questions_copied} questions in new dataset '{target_name}'")
        
        return {
            "success": True,
            "message": f"Successfully merged {len(source_dataset_ids)} datasets",
            "target_dataset_id": target_dataset_id,
            "target_dataset_name": target_name,
            "questions_merged": questions_copied,
            "source_datasets": [ds["name"] for ds in source_datasets],
            "deleted_datasets": deleted_datasets if delete_source else [],
            "total_source_datasets": len(source_dataset_ids)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Dataset merge failed: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Merge operation failed: {str(e)}"
        )
