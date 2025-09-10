"""
Database-powered FastAPI server for AI Text Analysis Platform
This version uses SQLite/PostgreSQL instead of in-memory storage
"""

import os
import uuid
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Database imports
from database import get_db, create_all_tables, check_database_connection
from database_service import DatabaseInitService, DatasetService, QuestionService, WordFrequencyService, AnalysisJobService, DatabaseUtilityService
from models import Dataset, Question, WordFrequency, AnalysisJob

# Initialize FastAPI app
app = FastAPI(
    title="AI-Powered Text Analysis Platform API (Database Version)",
    description="Enhanced API with persistent database storage",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Ensure uploads directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Pydantic models for requests
class WordCloudRequest(BaseModel):
    dataset_id: str
    mode: str = "all"
    selected_columns: Optional[List[int]] = None
    filters: Optional[Dict[str, Any]] = None

class DatasetResponse(BaseModel):
    id: str
    name: str
    filename: str
    file_size: int
    total_rows: int
    questions_count: int
    upload_status: str
    processing_status: str
    created_at: str

# Database initialization check
@app.on_event("startup")
async def startup_event():
    """
    Initialize database on application startup
    """
    print("🚀 Starting AI Text Analysis Platform API (Database Version)...")
    
    # Check database connection
    if not check_database_connection():
        print("❌ Database connection failed!")
        exit(1)
    
    # Initialize database
    if not DatabaseInitService.initialize_database():
        print("❌ Database initialization failed!")
        exit(1)
    
    print("✅ Database ready")
    print("📊 API server starting with persistent storage...")

@app.get("/")
def read_root():
    """Root endpoint with API information"""
    return {
        "message": "AI-Powered Text Analysis Platform API (Database Version)",
        "version": "2.0.0",
        "status": "running",
        "database": "enabled",
        "features": [
            "Persistent dataset storage",
            "Advanced analytics",
            "Background job processing",
            "Real-time word cloud generation"
        ],
        "endpoints": [
            "GET /health - Health check with database status",
            "GET /docs - API documentation", 
            "POST /api/wordcloud/generate - Generate word cloud from database",
            "GET /api/wordcloud/modes - Get analysis modes",
            "GET /api/datasets - List all datasets from database",
            "POST /api/datasets/upload - Upload CSV dataset to database",
            "GET /api/datasets/{id} - Get dataset details from database",
            "DELETE /api/datasets/{id} - Delete dataset from database",
            "GET /api/datasets/{id}/questions - Get questions with pagination",
            "GET /api/jobs - List background processing jobs",
            "GET /api/stats - Database statistics"
        ]
    }

@app.get("/health")
def health_check():
    """Health check with database status"""
    db_connected = check_database_connection()
    stats = DatabaseUtilityService.get_database_stats()
    
    return {
        "status": "healthy" if db_connected else "unhealthy",
        "database": {
            "connected": db_connected,
            "statistics": stats
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/datasets")
def get_datasets(
    limit: int = 50, 
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get all datasets from database"""
    try:
        datasets = DatasetService.get_all_datasets(limit=limit, offset=offset)
        
        dataset_responses = [
            DatasetResponse(
                id=dataset.id,
                name=dataset.name,
                filename=dataset.filename,
                file_size=dataset.file_size,
                total_rows=dataset.total_rows,
                questions_count=dataset.questions_count,
                upload_status=dataset.upload_status,
                processing_status=dataset.processing_status,
                created_at=dataset.created_at.isoformat()
            )
            for dataset in datasets
        ]
        
        return {
            "success": True,
            "data": dataset_responses,
            "message": f"Retrieved {len(dataset_responses)} datasets"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve datasets: {str(e)}")

@app.post("/api/datasets/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload and store CSV dataset in database"""
    try:
        # Validate file
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        # Generate unique filename
        dataset_id = str(uuid.uuid4())
        safe_filename = f"{dataset_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(file_path)
        
        # Parse CSV to get structure
        import csv
        import io
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Try multiple encodings
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
        csv_text = None
        encoding_used = 'utf-8'
        
        for encoding in encodings:
            try:
                csv_text = content.decode(encoding)
                encoding_used = encoding
                break
            except UnicodeDecodeError:
                continue
        
        if not csv_text:
            raise HTTPException(status_code=400, detail="Could not decode CSV file")
        
        # Parse CSV structure
        csv_reader = csv.reader(io.StringIO(csv_text))
        headers = next(csv_reader, [])
        rows = list(csv_reader)
        
        # Create dataset record
        display_name = name or file.filename.replace('.csv', '').replace('_', ' ').title()
        
        dataset = DatasetService.create_dataset(
            name=display_name,
            filename=file.filename,
            file_size=file_size,
            file_path=file_path,
            column_names=headers,
            total_rows=len(rows),
            encoding=encoding_used
        )
        
        if not dataset:
            raise HTTPException(status_code=500, detail="Failed to create dataset record")
        
        # Create background job to process questions
        job = AnalysisJobService.create_job(
            dataset_id=dataset.id,
            job_type='dataset_processing',
            priority=1
        )
        
        # Process questions immediately (in real implementation, this would be a background task)
        questions_created = QuestionService.create_questions_from_csv(dataset.id, file_path)
        
        # Generate initial word frequencies
        word_data = WordFrequencyService.generate_word_frequencies(
            dataset_id=dataset.id,
            analysis_mode='all',
            selected_columns=[1, 2]
        )
        
        # Update job status
        if job:
            AnalysisJobService.update_job_progress(
                job_id=job.id,
                status='completed',
                progress_percentage=100,
                current_step='Dataset processing completed'
            )
        
        return {
            "success": True,
            "message": f"Dataset uploaded and processed successfully",
            "data": dataset.to_dict(),
            "processing": {
                "questions_created": questions_created,
                "word_frequencies_generated": len(word_data),
                "job_id": job.id if job else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up file if dataset creation failed
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/api/datasets/{dataset_id}")
def get_dataset(dataset_id: str, db: Session = Depends(get_db)):
    """Get specific dataset details from database"""
    try:
        dataset = DatasetService.get_dataset(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        return {
            "status": "success",
            "dataset": dataset.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve dataset: {str(e)}")

@app.delete("/api/datasets/{dataset_id}")
def delete_dataset(dataset_id: str, db: Session = Depends(get_db)):
    """Delete dataset from database"""
    try:
        success = DatasetService.delete_dataset(dataset_id)
        if not success:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        return {
            "status": "success",
            "message": f"Dataset {dataset_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete dataset: {str(e)}")

@app.get("/api/datasets/{dataset_id}/questions")
def get_dataset_questions(
    dataset_id: str,
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db)
):
    """Get paginated questions for a dataset from database"""
    try:
        if per_page > 100:
            per_page = 100  # Limit page size
        
        questions, total_count = QuestionService.get_questions_paginated(
            dataset_id=dataset_id,
            page=page,
            per_page=per_page
        )
        
        total_pages = (total_count + per_page - 1) // per_page
        
        return {
            "status": "success",
            "data": [question.to_dict() for question in questions],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve questions: {str(e)}")

@app.post("/api/wordcloud/generate")
def generate_wordcloud(request: WordCloudRequest, db: Session = Depends(get_db)):
    """Generate word cloud from database data"""
    try:
        # Check if dataset exists
        dataset = DatasetService.get_dataset(request.dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        # Get existing word frequencies or generate new ones
        word_freqs = WordFrequencyService.get_word_frequencies(
            dataset_id=request.dataset_id,
            analysis_mode=request.mode,
            limit=50
        )
        
        if not word_freqs:
            # Generate word frequencies if they don't exist
            print(f"📊 Generating new word frequencies for dataset {request.dataset_id}")
            word_data = WordFrequencyService.generate_word_frequencies(
                dataset_id=request.dataset_id,
                analysis_mode=request.mode,
                selected_columns=request.selected_columns or [1, 2]
            )
        else:
            # Use existing word frequencies
            word_data = []
            for wf in word_freqs:
                word_data.append({
                    'word': wf.word,
                    'frequency': wf.frequency,
                    'sentiment': wf.sentiment,
                    'size': wf.normalized_frequency
                })
        
        # Format response
        return {
            "status": "success",
            "words": word_data,
            "insights": {
                "total_words": len(word_data),
                "mode": request.mode,
                "dataset_name": dataset.name,
                "source": "database",
                "sentiment_distribution": {
                    "positive": len([w for w in word_data if w['sentiment'] == 'positive']),
                    "negative": len([w for w in word_data if w['sentiment'] == 'negative']),
                    "neutral": len([w for w in word_data if w['sentiment'] == 'neutral'])
                }
            },
            "metadata": {
                "dataset_id": dataset.id,
                "analysis_mode": request.mode,
                "columns_analyzed": request.selected_columns or [1, 2],
                "generated_at": datetime.utcnow().isoformat(),
                "source": "database_storage",
                "total_questions": dataset.questions_count
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Word cloud generation failed: {str(e)}")

@app.get("/api/wordcloud/modes")
def get_wordcloud_modes():
    """Get available word cloud analysis modes"""
    return {
        "modes": [
            {"id": "all", "name": "All Words", "description": "Complete vocabulary analysis"},
            {"id": "verbs", "name": "Action Words", "description": "Verbs and action-oriented language"},
            {"id": "themes", "name": "Themes", "description": "Common themes and topics"},
            {"id": "emotions", "name": "Emotions", "description": "Emotional language and sentiment"},
            {"id": "entities", "name": "Entities", "description": "Named entities and organizations"},
            {"id": "topics", "name": "Topics", "description": "Topic modeling results"}
        ]
    }

@app.get("/api/jobs")
def get_analysis_jobs(
    dataset_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get background processing jobs"""
    try:
        query = db.query(AnalysisJob)
        
        if dataset_id:
            query = query.filter(AnalysisJob.dataset_id == dataset_id)
        
        if status:
            query = query.filter(AnalysisJob.status == status)
        
        jobs = query.order_by(AnalysisJob.created_at.desc()).limit(limit).all()
        
        return {
            "status": "success",
            "jobs": [job.to_dict() for job in jobs]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve jobs: {str(e)}")

@app.get("/api/stats")
def get_database_stats(db: Session = Depends(get_db)):
    """Get database and application statistics"""
    try:
        stats = DatabaseUtilityService.get_database_stats()
        return {
            "status": "success",
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve statistics: {str(e)}")

@app.get("/api/settings")
def get_application_settings(public_only: bool = True):
    """Get application settings"""
    try:
        # Get noise words setting
        noise_words = DatabaseUtilityService.get_setting('noise_words', [
            'details', 'page', 'https', 'filevineapp', 'docviewer', 'view', 'source', 'embedding'
        ])
        
        max_words = DatabaseUtilityService.get_setting('max_words_per_cloud', 50)
        default_mode = DatabaseUtilityService.get_setting('default_analysis_mode', 'all')
        
        return {
            "status": "success",
            "settings": {
                "noise_words": noise_words,
                "max_words_per_cloud": max_words,
                "default_analysis_mode": default_mode
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve settings: {str(e)}")

@app.get("/api/test-database-connection")
def test_database_connection():
    """Test database connectivity"""
    try:
        connected = check_database_connection()
        stats = DatabaseUtilityService.get_database_stats()
        
        return {
            "database_connected": connected,
            "connection_test": "success" if connected else "failed",
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"database_connected": False, "error": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    print("🗄️  Starting Database-Powered API Server on port 8003...")
    print("📊 Features: SQLite storage, persistent datasets, background jobs")
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")
