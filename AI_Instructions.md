# AI-Powered Text Analysis Platform - AI Instructions

## Project Overview
This is an AI-driven development project building a comprehensive web application for analyzing user queries, context, and AI responses using NLTK and LLM APIs. The platform combines proven word cloud functionality with a robust FastAPI backend for large-scale data processing.

## Development Guidelines

### Git Commit Standards ⚠️ CRITICAL
**IMPORTANT**: Use SHORT commit messages only. Long commit messages break deployment pipelines.

**Format Rules:**
- Maximum 50 characters
- Start with action verb (Add, Fix, Update, Remove)
- No multi-line descriptions
- No excessive emojis

**Examples:**
- ✅ "Add analytics dashboard"
- ✅ "Fix CORS configuration" 
- ✅ "Update database models"
- ❌ "🎯 NEW: Comprehensive Analytics Dashboard with multiple features..."

## Core Architecture

### Frontend Stack (Next.js 14 on Vercel)
- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS with custom components
- **Data Tables**: AG Grid React for interactive data visualization
- **State Management**: React Context API or Zustand
- **Authentication**: Clerk integration
- **Real-time**: WebSocket client for job status updates
- **Visualization**: Custom CSS-based word cloud + Recharts

### Backend Stack (Unified FastAPI on Railway)
- **Framework**: FastAPI with Python 3.11+ (Consolidated Architecture)
- **Database**: PostgreSQL with SQLAlchemy ORM + Service Layer
- **Job Queue**: Celery with Redis broker  
- **File Storage**: Local filesystem with robust validation (AWS S3 ready)
- **Authentication**: JWT tokens + Clerk integration (temporarily disabled)
- **WebSocket**: FastAPI WebSocket for real-time updates
- **Text Analysis**: NLTK + OpenAI LLM integration
- **Architecture**: Unified server with separated service and API layers

## Service Map

### Core Services (Unified Architecture)
1. **Dataset Service Layer** (`backend/app/services/dataset_service.py`)
   - **ROBUST**: Comprehensive file validation and error handling
   - **SECURE**: Multi-encoding support, file type validation, size limits
   - **ATOMIC**: Database transactions with automatic rollback
   - **SCALABLE**: Pagination, efficient queries, background processing
   - Upload, preview, and manage query-response datasets
   - Real-time processing status updates

2. **Analysis Service Layer** (`backend/app/services/analysis_service.py`)
   - **NLTK-Powered**: POS tagging for precise word categorization
   - **CACHED**: Intelligent caching with force-regeneration options
   - **MODES**: True analysis mode differentiation (verbs, nouns, adjectives, emotions)
   - Sentiment analysis with enhanced word filtering
   - Word frequency generation with database persistence

3. **Dataset API Endpoints** (`backend/app/api/datasets.py`)
   - **RESTful**: Complete CRUD operations with proper HTTP methods
   - **VALIDATED**: Pydantic models and comprehensive input validation  
   - **DOCUMENTED**: OpenAPI/Swagger documentation with examples
   - **ROBUST**: Proper error handling and status codes
   - Upload, list, retrieve, delete, and reprocess datasets
   - Word frequency generation and retrieval

4. **Word Cloud System** (`frontend/components/wordcloud/WordCloudVisualization.tsx`)
   - Multi-mode support (entities, topics, sentiment, themes)
   - Interactive exploration with drill-down capability  
   - Real-time filtering and comparative analysis
   - Export functionality (PNG, SVG, PDF)

4. **Dataset Table View** (`frontend/components/datasets/DatasetTableView.tsx`)
   - AG Grid React integration for high-performance data tables
   - Interactive sorting, filtering, and search functionality
   - Auto-sizing columns with text wrapping for long content
   - CSV export functionality with filtered data
   - Pagination support for large datasets

5. **Real-time Processing** (`backend/app/websocket/manager.py`)
   - WebSocket connection management
   - Background job status updates
   - Progress tracking for large dataset processing

6. **Advanced Analytics** (`backend/app/api/analytics.py`)
   - Sentiment trend analysis over time
   - Topic evolution tracking
   - Entity relationship networks
   - Conversation quality metrics

7. **Export & Reporting** (`backend/app/reporting/`)
   - Executive summary generation
   - Multi-format exports (PDF, Excel, PowerPoint)
   - Scheduled report generation
   - Custom report templates

## Database Schema

### Core Tables
- **users**: Clerk integration for user management
- **datasets**: Enhanced with processing status and metrics
- **questions**: Query-response pairs with NLTK analysis results
- **nltk_analysis**: Detailed analysis results (entities, topics, keywords)
- **word_frequencies**: Word cloud data with sentiment associations
- **analysis_jobs**: Background processing job tracking
- **llm_analysis_cache**: Cached LLM responses for efficiency
- **org_usage_analytics**: Organization-level usage metrics

## Key Features

### 1. Enhanced Data Processing
- Bulk upload of query-response CSV files
- Real-time processing with progress updates
- NLTK preprocessing and analysis pipeline
- Quality validation and error handling

### 2. Advanced Text Analysis
- **Sentiment Analysis**: Multi-model approach with confidence scoring
- **Topic Modeling**: LDA with coherence metrics and evolution tracking
- **Entity Extraction**: Named entity recognition and relationship mapping
- **Question Classification**: Type classification and complexity scoring
- **Response Quality**: Relevance, completeness, and alignment analysis

### 3. Interactive Visualizations
- **Enhanced Word Clouds**: Multi-mode analysis with interactive features
- **Sentiment Dashboards**: Time-series analysis with trend identification
- **Topic Exploration**: Interactive topic modeling with drill-down
- **Entity Networks**: Relationship visualization between extracted entities

### 4. Real-time Processing
- WebSocket-based progress updates
- Background job queue with Celery
- Status tracking and error handling
- Concurrent processing optimization

## File Structure

```
WordCloud/
├── AI_Instructions.md (this file)
├── AI_System_Prompt.md
├── frontend/
│   ├── components/
│   │   ├── dashboard/ (analytics components)
│   │   ├── wordcloud/ (visualization components)
│   │   ├── datasets/ (data management with AG Grid tables)
│   │   ├── auth/ (authentication)
│   │   └── common/ (shared components)
│   ├── lib/ (utilities and API clients)
│   ├── pages/ (Next.js pages)
│   └── styles/ (Tailwind CSS)
├── backend/
│   ├── app/ (UNIFIED FASTAPI APPLICATION)
│   │   ├── main.py (Main FastAPI application with proper architecture)
│   │   ├── models/ (SQLAlchemy database models with relationships)
│   │   ├── api/ (REST API endpoints - FULLY IMPLEMENTED)
│   │   ├── services/ (Business logic and data access layer - NEW)
│   │   ├── analysis/ (NLTK processing engines)
│   │   ├── tasks/ (Celery background tasks)
│   │   ├── websocket/ (real-time connections)
│   │   ├── reporting/ (export functionality)
│   │   └── core/ (configuration, database, logging)
│   ├── unified_production_server.py (Production server - REPLACES old servers)
│   ├── test_unified_system.py (End-to-end testing script)
│   ├── requirements.txt
│   ├── railway.toml (Updated for unified server)
│   └── alembic/ (database migrations)
└── docs/ (additional documentation)
```

## Development Workflow

### Phase 1: Infrastructure Setup ✅ (Current)
- Core documentation and project structure
- Database models and migrations
- Authentication integration
- Basic API endpoints

### Phase 2: NLTK Analysis Engine ✅ **COMPLETED**
- ✅ Sentiment analysis pipeline (VADER + TextBlob + custom models)
- ✅ Topic modeling implementation (LDA with coherence scoring)
- ✅ Entity extraction setup (spaCy integration with fallback)
- ✅ Question classification system (intent analysis and complexity scoring)
- ✅ Keyword extraction (TF-IDF, YAKE, TextRank methods)
- ✅ Readability analysis and text similarity metrics

### Phase 3: Word Cloud Enhancement ✅ **COMPLETED**
- ✅ Multi-mode visualization (entities, topics, sentiment, themes)
- ✅ Interactive features (hover, click, zoom, filter)
- ✅ Real-time updates (dynamic column filtering)
- ✅ Export functionality (PNG, SVG support)
- ✅ Advanced word filtering with user-specified exclusions
- ✅ Column selection and data filtering capabilities

### Phase 4: LLM Integration
- OpenAI API integration
- Response quality analysis
- Business insights generation
- Intelligent caching

### Phase 5: Dashboard & Reporting
- Analytics dashboard
- Multi-format exports
- Report templates
- Scheduled reporting

### Phase 6: Frontend Integration
- Component integration
- Responsive design
- Error handling
- Performance optimization

### Phase 7: Testing & Deployment
- Comprehensive testing
- Security audit
- Performance optimization
- Production deployment

## Deployment Configuration

### Environment Variables
- Database: PostgreSQL connection
- Redis: Job queue and caching
- OpenAI: LLM API integration
- Clerk: Authentication services
- AWS: S3 file storage
- Security: JWT and rate limiting

### Infrastructure
- **Frontend**: Vercel deployment
- **Backend**: Railway hosting
- **Database**: Railway PostgreSQL
- **Cache/Queue**: Railway Redis
- **Storage**: AWS S3 with CloudFront

## AI Development Guidelines

### When Working on This Project:
1. **Always** update this AI_Instructions.md when adding new services or features
2. **Always** create/update README.md files in directories when adding new components
3. **Follow** the established architecture patterns and file structure
4. **Maintain** the service map and database schema documentation
5. **Document** all API endpoints and their purposes
6. **Update** the development phase status as features are completed

### Code Standards:
- Use TypeScript for all frontend code
- Use Pydantic models for all API schemas
- Include comprehensive error handling
- Add proper logging for debugging
- Follow RESTful API design principles
- Implement proper security measures

### Testing Requirements:
- Unit tests for all analysis functions
- Integration tests for API endpoints
- E2E tests for critical user flows
- Load testing for large datasets
- Security testing for authentication

## Current Status (v3.0.0 - UNIFIED ARCHITECTURE)

### ✅ **MAJOR CONSOLIDATION COMPLETED** (January 2025)
- **🆕 Server Architecture Unified**: All duplicate servers consolidated into single FastAPI application
- **🆕 Service Layer Implementation**: Robust business logic separation with `DatasetService` and `AnalysisService`
- **🆕 Enhanced Data Upload**: Comprehensive file validation, atomic transactions, automatic rollback
- **🆕 Production Server Updated**: `unified_production_server.py` replaces fragmented server implementations
- **🆕 End-to-End Testing**: Automated testing script validates complete system functionality

### ✅ **Robust Data Upload & Storage System** 
- **SECURE**: Multi-encoding support, file type validation, size limits, directory traversal protection
- **ATOMIC**: Database transactions with automatic cleanup on failure
- **VALIDATED**: Comprehensive CSV structure validation with flexible column matching
- **CACHED**: Intelligent word frequency caching with force-regeneration options
- **SCALABLE**: Pagination, efficient queries, background job tracking

### ✅ **Production Infrastructure Stabilized**
- **Frontend**: Vercel deployment with auto-deployment from GitHub
- **Backend**: Railway deployment updated to use unified server architecture  
- **Database**: PostgreSQL with enhanced connection pooling and health checks
- **CORS**: Fixed for cross-origin communication between Vercel and Railway
- **Configuration**: Railway.toml updated for unified production server

### ✅ **Previous Achievements Maintained**
- NLTK Analysis Engine Enhanced (v2.5.0) with POS tagging
- Professional frontend with AG Grid dataset tables
- Word cloud system with multiple analysis modes
- Database persistence with comprehensive schema
- GitHub Actions deployment workflow
- Professional landing page and navigation

### ✅ **Architecture Improvements**
- **No More Server Fragmentation**: Single source of truth for API endpoints
- **Proper Separation of Concerns**: API layer → Service layer → Database layer
- **Enhanced Error Handling**: Comprehensive exception handling with proper HTTP status codes
- **Development-Production Parity**: Same codebase for all environments
- **Maintainable Codebase**: Clear file organization and documentation

### ⚠️ **Temporary Configurations**
- Authentication integration temporarily disabled for development
- File storage using local filesystem (AWS S3 integration ready)

### 🎯 **Ready for Production**
The application now has a consolidated, robust architecture suitable for production deployment with enhanced data upload and storage capabilities.

## Next Steps
1. ✅ ~~Set up database persistence (SQLite for development)~~ **COMPLETED**
2. ✅ ~~Migrate existing datasets to database storage~~ **COMPLETED**  
3. ✅ ~~Enhance frontend to use database API~~ **COMPLETED**
4. ✅ ~~Frontend deployment to Vercel~~ **COMPLETED**
   - ✅ GitHub repository setup and connected
   - ✅ Vercel frontend deployment with auto-deployment
   - ✅ Build errors resolved and configuration optimized
   - ✅ Professional landing page and navigation restored
5. ✅ ~~Complete backend deployment to Railway~~ **COMPLETED**
   - ✅ Deploy FastAPI backend to Railway with PostgreSQL
   - ✅ Configure environment variables for production
   - ✅ Connect frontend to production backend API
   - ✅ Fix CORS configuration for cross-origin requests
   - ✅ Streamline GitHub Actions deployment workflow
6. ✅ ~~Connect uploaded datasets to NLTK analysis pipeline~~ **COMPLETED**
   - ✅ Full sentiment analysis (VADER + TextBlob)
   - ✅ Entity extraction and topic analysis
   - ✅ Enhanced word filtering with user exclusions
   - ✅ **Part-of-Speech tagging for analysis mode differentiation**
   - ✅ **NLTK-powered word categorization (verbs, nouns, adjectives, emotions)**
   - ✅ **Force regeneration endpoints for testing enhanced filtering**
7. **🚀 CURRENT: Test and refine NLTK analysis modes** to ensure distinct results between word cloud modes
8. **Implement real-time processing** with WebSocket updates and background jobs
9. **Build comprehensive analytics dashboard** components with database-powered insights
10. **Set up Celery workers** for background processing (async dataset processing)
11. **Add advanced analysis endpoints** (sentiment analysis API, entity extraction API, topic modeling)
12. **Enhance LLM integration** for business insights and response quality analysis
13. **Re-implement authentication** when ready for multi-user production

## **🎯 Immediate Priorities (December 2024)**
1. **Verify NLTK analysis modes are working** - Test that "all words" vs "action words" show different results
2. **Deploy NLTK enhancements** - Push version 2.5.0 with POS tagging to production
3. **User acceptance testing** - Validate the enhanced word filtering meets user requirements
4. **Performance optimization** - Ensure NLTK processing doesn't slow down word cloud generation

## **Working Application URLs**

### **🌐 Production (LIVE) - UNIFIED ARCHITECTURE**
- **Frontend**: https://ai-text-analysis-platform.vercel.app (deployed on Vercel with auto-deployment)
- **Backend**: https://ai-text-analysis-production.up.railway.app (UNIFIED FastAPI server on Railway with PostgreSQL)
- **API Documentation**: https://ai-text-analysis-production.up.railway.app/docs (comprehensive API docs)
- **Health Check**: https://ai-text-analysis-production.up.railway.app/production/health (enhanced health monitoring)
- **System Info**: https://ai-text-analysis-production.up.railway.app/production/info (deployment details)

### **🏠 Local Development**
- **Frontend**: http://localhost:3000 or http://localhost:3001 (Next.js application)
- **Dataset Upload**: http://localhost:3000/upload (CSV file upload interface)
- **Dashboard**: http://localhost:3000/dashboard (basic dashboard)
- **Word Cloud Demo**: http://localhost:3000/wordcloud-demo (interactive demo with backend data)
- **Legal Word Cloud**: http://localhost:3000/legal-wordcloud (filtered legal dataset visualization)

### **Backend API Server (Local Development):**
- **🆕 Unified API Server**: http://localhost:8000 (Consolidated FastAPI application)
- **API Documentation**: http://localhost:8000/docs (comprehensive API documentation)
- **Health Check**: http://localhost:8000/health (basic health status)
- **Production Health**: http://localhost:8000/production/health (detailed health information)
- **System Info**: http://localhost:8000/production/info (development environment details)

### **🧪 Testing & Validation:**
- **End-to-End Test**: `python backend/test_unified_system.py` (automated system validation)
- **Local Testing**: Tests unified server at http://localhost:8000
- **Production Testing**: Validates live deployment functionality

---

*This file should be updated by any AI working on this project to maintain current understanding of the system architecture and implementation status.*
