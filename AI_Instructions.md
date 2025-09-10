# AI-Powered Text Analysis Platform - AI Instructions

## Project Overview
This is an AI-driven development project building a comprehensive web application for analyzing user queries, context, and AI responses using NLTK and LLM APIs. The platform combines proven word cloud functionality with a robust FastAPI backend for large-scale data processing.

## Core Architecture

### Frontend Stack (Next.js 14 on Vercel)
- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS with custom components
- **State Management**: React Context API or Zustand
- **Authentication**: Clerk integration
- **Real-time**: WebSocket client for job status updates
- **Visualization**: Custom CSS-based word cloud + Recharts

### Backend Stack (FastAPI on Railway)
- **Framework**: FastAPI with Python 3.11+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Job Queue**: Celery with Redis broker
- **File Storage**: AWS S3 for raw data storage
- **Authentication**: JWT tokens + Clerk integration
- **WebSocket**: FastAPI WebSocket for real-time updates
- **Text Analysis**: NLTK + OpenAI LLM integration

## Service Map

### Core Services
1. **Dataset Management Service** (`backend/app/api/datasets.py`)
   - Upload, preview, and manage query-response datasets
   - Password-protected uploads with chunking
   - Real-time processing status updates

2. **NLTK Analysis Engine** (`backend/app/analysis/nltk_processor.py`)
   - Sentiment analysis (VADER + TextBlob + custom models)
   - Named entity recognition with spaCy integration
   - Topic modeling using LDA with coherence scoring
   - Keyword extraction (TF-IDF, YAKE, TextRank)
   - Question classification and response quality assessment

3. **Word Cloud System** (`frontend/components/wordcloud/WordCloudVisualization.tsx`)
   - Multi-mode support (entities, topics, sentiment, themes)
   - Interactive exploration with drill-down capability
   - Real-time filtering and comparative analysis
   - Export functionality (PNG, SVG, PDF)

4. **Real-time Processing** (`backend/app/websocket/manager.py`)
   - WebSocket connection management
   - Background job status updates
   - Progress tracking for large dataset processing

5. **Advanced Analytics** (`backend/app/api/analytics.py`)
   - Sentiment trend analysis over time
   - Topic evolution tracking
   - Entity relationship networks
   - Conversation quality metrics

6. **Export & Reporting** (`backend/app/reporting/`)
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
│   │   ├── datasets/ (data management)
│   │   ├── auth/ (authentication)
│   │   └── common/ (shared components)
│   ├── lib/ (utilities and API clients)
│   ├── pages/ (Next.js pages)
│   └── styles/ (Tailwind CSS)
├── backend/
│   ├── app/
│   │   ├── main.py (FastAPI application)
│   │   ├── models/ (database models)
│   │   ├── api/ (REST endpoints)
│   │   ├── analysis/ (NLTK processing)
│   │   ├── tasks/ (Celery background tasks)
│   │   ├── websocket/ (real-time connections)
│   │   ├── reporting/ (export functionality)
│   │   └── core/ (configuration and utilities)
│   ├── requirements.txt
│   ├── celery_config.py
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

## Current Status
- ✅ Documentation infrastructure created
- ✅ Project structure setup completed
- ✅ Backend core implementation completed
- ✅ Database schema implementation completed  
- ✅ Celery job queue setup completed
- ✅ WebSocket connections implemented
- ✅ Frontend initialization completed (Next.js 14 + TypeScript + Tailwind CSS)
- ✅ Enhanced word cloud system implemented with multiple analysis modes and interactive features
- ✅ Application running successfully without authentication (Clerk temporarily removed)
- ✅ **Backend API server working on localhost:8001 with word cloud endpoints**
- ✅ **Frontend-Backend integration functional**
- ✅ **NLTK analysis engine implemented** (comprehensive text processing pipeline)
- ✅ **LLM integration implemented** (OpenAI API with intelligent fallbacks)
- ✅ **CSV dataset upload functionality working** (frontend dropzone + backend processing)
- ✅ **File storage system operational** (local uploads directory)
- ✅ **Dataset management interface complete** (upload, list, preview, delete)
- ✅ **Column filtering system implemented** (users can select which CSV columns to analyze)
  - Interactive column selection UI with preset filters
  - Backend API supports dynamic column filtering
  - Real-time word cloud updates based on column selection
- ✅ **Word cloud page cleaned up** (removed test/demo components, focus on real data analysis)
- ✅ **Noise word filtering working** (calls port 8002 API with comprehensive debugging)
- ✅ **Database persistence implemented** (SQLite with SQLAlchemy models)
  - Complete database schema with 6 tables (datasets, questions, word_frequencies, etc.)
  - Database initialization script and service layer
  - Background job processing framework
  - Application settings management
- ✅ **Database-powered API server** (port 8003 with persistent storage)
  - Enhanced dataset management with database persistence
  - Word frequency caching and retrieval
  - Background job tracking and status updates
  - Database statistics and health monitoring
- ✅ **Production deployment LIVE** (GitHub + Vercel + Railway configuration)
  - ✅ Frontend successfully deployed to Vercel with auto-deployment
  - ✅ Build errors resolved (TypeScript unused variables, ESLint configuration)
  - ✅ Vercel.json configuration optimized for Next.js monorepo structure
  - ✅ Professional landing page with navigation restored
  - ✅ Complete deployment guide and step-by-step walkthrough
  - ✅ Production-optimized servers and database configuration
  - ✅ **Railway backend deployment COMPLETED** (FastAPI + PostgreSQL production-ready)
    - Full backend API deployed to Railway with PostgreSQL database
    - Advanced word filtering with user-specified exclusions implemented
    - Enhanced NLTK processing with multi-model sentiment analysis
    - Column filtering and data selection functionality restored
    - Configurable noise words via API endpoints
- ✅ **Frontend user interface complete** 
  - Professional landing page with feature overview
  - App-wide navigation with all main sections
  - Responsive design with Tailwind CSS
  - Interactive components and smooth transitions
- ⚠️ Authentication integration temporarily disabled for development
- ⏳ Advanced analytics dashboard components pending

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
6. ✅ ~~Connect uploaded datasets to NLTK analysis pipeline~~ **COMPLETED**
   - ✅ Full sentiment analysis (VADER + TextBlob)
   - ✅ Entity extraction and topic analysis
   - ✅ Enhanced word filtering with user exclusions
7. **🚀 NEXT: Implement real-time processing** with WebSocket updates and background jobs
8. **Build comprehensive analytics dashboard** components with database-powered insights
9. **Set up Celery workers** for background processing (async dataset processing)
10. **Add advanced analysis endpoints** (sentiment analysis API, entity extraction API, topic modeling)
11. **Enhance LLM integration** for business insights and response quality analysis
12. Re-implement authentication when ready for multi-user production

## **Working Application URLs**

### **🌐 Production (LIVE)**
- **Frontend**: https://ai-text-analysis-platform.vercel.app (deployed on Vercel)
- **Backend**: *Railway deployment pending*

### **🏠 Local Development**
- **Frontend**: http://localhost:3000 or http://localhost:3001 (Next.js application)
- **Dataset Upload**: http://localhost:3000/upload (CSV file upload interface)
- **Dashboard**: http://localhost:3000/dashboard (basic dashboard)
- **Word Cloud Demo**: http://localhost:3000/wordcloud-demo (interactive demo with backend data)
- **Legal Word Cloud**: http://localhost:3000/legal-wordcloud (filtered legal dataset visualization)

### **Backend API Servers:**
- **Main API (In-Memory)**: http://localhost:8001 (FastAPI with basic upload and word cloud)
- **Legal Data API**: http://localhost:8002 (dedicated filtered legal dataset API with column selection)
- **🆕 Database API**: http://localhost:8003 (FastAPI with SQLite persistence, enhanced features)

### **API Documentation:**
- **Main API Docs**: http://localhost:8001/docs
- **🆕 Database API Docs**: http://localhost:8003/docs (enhanced endpoints with persistence)
- **🆕 Database Health Check**: http://localhost:8003/health (database status and statistics)

---

*This file should be updated by any AI working on this project to maintain current understanding of the system architecture and implementation status.*
