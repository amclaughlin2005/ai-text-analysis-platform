# Backend - FastAPI Application

## Purpose
FastAPI backend server providing REST API endpoints, background job processing, and real-time WebSocket connections for the AI-Powered Text Analysis Platform.

## Technology Stack
- **Framework**: FastAPI with Python 3.11+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Job Queue**: Celery with Redis broker
- **Authentication**: JWT tokens + Clerk integration
- **Text Analysis**: NLTK + OpenAI LLM integration
- **File Storage**: AWS S3 for raw data storage
- **WebSocket**: FastAPI WebSocket for real-time updates

## Directory Structure

### `/app/`
- **`main.py`** - FastAPI application entry point and configuration
- **`models/`** - SQLAlchemy database models and Pydantic schemas
- **`api/`** - REST API endpoints organized by feature area
- **`analysis/`** - **CORE**: NLTK processing and LLM integration engine
- **`tasks/`** - Celery background job definitions
- **`core/`** - Configuration, database connection, security, logging
- **`websocket/`** - Real-time WebSocket connection management
- **`reporting/`** - Report generation and export functionality
- **`utils/`** - Shared utility functions and helpers

### Root Level Files
- **`requirements.txt`** - Python package dependencies
- **`celery_config.py`** - Background job queue configuration
- **`alembic/`** - Database migration scripts and versioning
- **`tests/`** - Unit and integration test suites

## Core Services

### 1. Dataset Management (`/api/datasets.py`)
- Upload and validate CSV files containing query-response pairs
- Dataset preprocessing and metadata extraction
- Status tracking and progress reporting
- Cascade deletion with cleanup

### 2. NLTK Analysis Engine (`/analysis/nltk_processor.py`)
- **Sentiment Analysis**: VADER + TextBlob + custom models
- **Topic Modeling**: LDA with coherence scoring
- **Entity Extraction**: Named entity recognition with spaCy
- **Question Classification**: Type and intent classification
- **Text Similarity**: Semantic similarity analysis
- **Readability Analysis**: Multiple readability metrics

### 3. LLM Integration (`/analysis/llm_processor.py`)
- OpenAI API integration for advanced analysis
- Conversation quality assessment
- Business insights generation
- Response completeness and relevance scoring
- Intelligent caching for expensive operations

### 4. Real-time Processing (`/websocket/manager.py`)
- WebSocket connection management
- Background job status broadcasting
- Progress updates for long-running operations
- Error notification and recovery

### 5. Advanced Analytics (`/api/analytics.py`)
- Time-series sentiment analysis
- Topic evolution tracking
- Entity relationship networks
- Cross-dataset comparative analysis

## Database Schema

### Core Tables
- **users** - Clerk integration for user management
- **datasets** - Dataset metadata with processing status
- **questions** - Query-response pairs with analysis results
- **nltk_analysis** - Detailed NLTK analysis results
- **word_frequencies** - Word cloud data with associations
- **analysis_jobs** - Background job tracking
- **llm_analysis_cache** - Cached LLM responses
- **org_usage_analytics** - Organization-level metrics

## API Endpoints

### Dataset Management
- `GET /api/datasets` - List datasets with status
- `POST /api/datasets/upload` - Upload CSV with preprocessing
- `GET /api/datasets/{id}` - Dataset details with analytics
- `DELETE /api/datasets/{id}` - Delete with cascade cleanup
- `POST /api/datasets/{id}/reprocess` - Trigger reanalysis

### NLTK Analysis
- `POST /api/analysis/sentiment` - Batch sentiment analysis
- `POST /api/analysis/topics` - Topic modeling
- `POST /api/analysis/entities` - Named entity extraction
- `POST /api/analysis/classification` - Question classification
- `GET /api/analysis/jobs/{id}` - Job status tracking

### Word Cloud & Visualization
- `POST /api/wordcloud/generate` - Multi-mode word cloud generation
- `POST /api/wordcloud/interactive` - Interactive exploration
- `POST /api/wordcloud/export` - Export in multiple formats

### Advanced Analytics
- `GET /api/analytics/sentiment-trends` - Time-series analysis
- `GET /api/analytics/topic-evolution` - Topic change tracking
- `GET /api/analytics/entity-networks` - Relationship analysis

### Reporting & Export
- `POST /api/reports/executive` - Executive summary generation
- `POST /api/reports/technical` - Detailed technical reports
- `POST /api/export/schedule` - Schedule recurring reports

## Background Jobs (Celery)

### Analysis Tasks
- **Dataset Processing**: NLTK analysis pipeline
- **Topic Modeling**: LDA model training and inference
- **Sentiment Analysis**: Batch sentiment scoring
- **Entity Extraction**: Named entity processing
- **Report Generation**: Automated report creation

### Job Management
- Progress tracking with WebSocket updates
- Error handling and retry logic
- Resource monitoring and optimization
- Concurrent job limiting

## WebSocket Events
- `job_started` - Analysis job initiated
- `job_progress` - Progress updates with details
- `job_completed` - Completion with results
- `job_failed` - Error notification with recovery options
- `dataset_updated` - Real-time dataset changes

## Dependencies
- PostgreSQL database for persistent storage
- Redis for job queue and caching
- OpenAI API for LLM processing
- AWS S3 for file storage
- Clerk for user authentication

## Usage
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
celery -A celery_config.celery_app worker --loglevel=info
```

## Integration Points
- **Frontend**: REST API and WebSocket connections
- **Database**: SQLAlchemy ORM with connection pooling
- **File Storage**: Direct S3 integration for uploads
- **External APIs**: OpenAI, Clerk authentication
- **Job Queue**: Redis-backed Celery for background processing

## Environment Variables
```env
DATABASE_URL=postgresql://user:pass@host:port/dbname
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-proj-...
CLERK_SECRET_KEY=sk_test_...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

*Last Updated: Initial project structure creation*
