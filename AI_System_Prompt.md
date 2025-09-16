# AI-Powered Text Analysis Platform - System Prompt

## High-Level Application Purpose

This is an **AI-Powered Text Analysis Platform** designed to analyze user queries, context, and AI responses using advanced NLP techniques. The application combines proven word cloud visualization with robust backend processing for large-scale data analysis.

**Core Function**: Upload CSV files containing query-response pairs → Process with advanced NLTK analysis (POS tagging, sentiment, entities) → Generate interactive word clouds with mode-specific filtering → Export comprehensive reports.

**🌟 Latest Enhancement**: NLTK-powered Part-of-Speech tagging enables precise word categorization for analysis modes (verbs, nouns, adjectives, emotions).

## Directory Structure & Responsibilities

### Root Level Files
- `AI_Instructions.md` - **CRITICAL**: Detailed technical documentation for AI developers
- `AI_System_Prompt.md` - **THIS FILE**: High-level system overview and instructions
- `enhanced_project_plan (1).md` - Complete project specification and requirements
- `claude.md` - Documentation requirements and AI development guidelines

### `/frontend/` - Next.js 14 TypeScript Application
**Purpose**: User interface for data upload, visualization, and analysis
- `/components/dashboard/` - Analytics and metrics visualization components
- `/components/wordcloud/` - Interactive word cloud visualization system
- `/components/datasets/` - **ENHANCED**: Data upload and management with flexible upload modes
  - `DatasetUpload.tsx` - Traditional CSV Q&A format upload
  - `FlexibleDataUpload.tsx` - **NEW**: Upload any JSON/CSV structure
  - `AppendDataUpload.tsx` - **NEW**: Add data to existing datasets
  - `DatasetList.tsx` - Browse and manage uploaded datasets
- `/components/auth/` - Authentication components (Clerk integration)
- `/components/common/` - Shared UI components and utilities
- `/lib/` - API clients, utilities, WebSocket connections
- `/app/` - **UPDATED**: Next.js 13+ app directory routing
  - `/upload/` - **ENHANCED**: Multi-mode upload interface with append support
- `/styles/` - Tailwind CSS styling and themes

### `/backend/` - FastAPI Python Application
**Purpose**: API server, data processing, and analysis engine
- `/app/main.py` - FastAPI application entry point and configuration
- `/app/models/` - SQLAlchemy database models and schemas
- `/app/api/` - REST API endpoints organized by feature
- `/app/analysis/` - **CORE**: NLTK processing and LLM integration
- `/app/tasks/` - Celery background job definitions
- `/app/websocket/` - Real-time WebSocket connection management
- `/app/reporting/` - Report generation and export functionality
- `/app/core/` - Configuration, database, security, logging
- `/requirements.txt` - Python dependencies
- `/celery_config.py` - Background job queue configuration
- `/alembic/` - Database migration scripts

### `/docs/` - Additional Documentation
**Purpose**: Extended documentation and guides
- API documentation, deployment guides, user manuals

## Development Guidelines

### Git Commit Standards
**CRITICAL**: Use SHORT, concise commit messages only. Long commit messages break deployment.
- ✅ Good: "Add analytics dashboard"
- ✅ Good: "Fix word cloud styling" 
- ✅ Good: "Update API endpoints"
- ❌ Bad: Multi-line commits with detailed descriptions
- ❌ Bad: Emoji-heavy or overly descriptive messages

Keep commits under 50 characters when possible.

## Key System Components

### 1. Data Processing Pipeline
**Flow**: CSV Upload → Validation → NLTK Analysis → LLM Enhancement → Database Storage → Visualization
- Handles query-response pair analysis
- Real-time progress updates via WebSocket
- Background processing with Celery

### 2. Analysis Engine (NLTK + OpenAI)
**Core Capabilities**:
- Sentiment analysis (multi-model approach)
- Topic modeling with LDA
- Named entity recognition
- Question classification and response quality scoring
- Text similarity and semantic alignment

### 3. Visualization System
**Interactive Word Clouds**:
- Multi-mode analysis (entities, topics, sentiment, themes)
- Comparative visualization (query vs response)
- Real-time filtering and drill-down capabilities
- Export in multiple formats

### 4. Real-time Communication
**WebSocket Integration**:
- Live processing status updates
- Progress tracking for large datasets
- Error notification and recovery

## AI Development Instructions

### When Starting Work on This Project:

1. **ALWAYS READ** `AI_Instructions.md` first for detailed technical context
2. **UNDERSTAND** the current development phase from the project plan
3. **FOLLOW** the established file structure and naming conventions
4. **UPDATE** documentation when making changes

### Documentation Maintenance Requirements:

#### Every New Directory MUST Have:
- `README.md` explaining its purpose and how it fits into the overall system
- Clear description of component responsibilities
- Examples of how to use/interact with components in that directory

#### Every Significant File MUST Have:
- Header comments explaining purpose and dependencies
- Clear function/class documentation
- Integration points with other system components

#### When Adding New Features:
1. Update `AI_Instructions.md` with new service information
2. Add to the service map and file structure documentation
3. Update the current status and next steps
4. Create/update relevant directory READMEs

### Code Standards and Patterns:

#### Frontend (Next.js/TypeScript):
```typescript
// All components should follow this pattern
interface ComponentProps {
  // Typed props
}

export default function Component({ props }: ComponentProps) {
  // Component logic with proper error handling
  // WebSocket integration where needed
  // Proper state management
}
```

#### Backend (FastAPI/Python):
```python
# All API endpoints should follow this pattern
from pydantic import BaseModel

class RequestModel(BaseModel):
    # Typed request schema

class ResponseModel(BaseModel):
    # Typed response schema

@router.post("/endpoint", response_model=ResponseModel)
async def endpoint(request: RequestModel):
    # Proper error handling and logging
    # Background job integration where needed
```

### Critical Integration Points:

1. **Authentication**: Clerk integration across frontend/backend
2. **Real-time Updates**: WebSocket connections for job progress
3. **Data Processing**: Celery jobs with progress tracking
4. **Analysis Pipeline**: NLTK → LLM → Database → Visualization flow
5. **Export System**: Multi-format report generation

### Development Phases Priority:

1. **Infrastructure** (Database, API, Auth) - Foundation
2. **Analysis Engine** (NLTK, LLM) - Core functionality  
3. **Visualization** (Word clouds, Dashboard) - User interface
4. **Integration** (Real-time, Export) - Complete experience
5. **Polish** (Testing, Performance, Security) - Production ready

## Error Handling Strategy

### Frontend:
- Graceful degradation for failed API calls
- Loading states for all async operations
- User-friendly error messages
- Retry mechanisms for transient failures

### Backend:
- Comprehensive exception handling
- Structured error responses with correlation IDs
- Background job failure recovery
- Rate limiting and security protections

## Performance Considerations

### Database:
- Proper indexing on frequently queried fields
- Connection pooling for high concurrent load
- Batch operations for large datasets
- Read replicas for analytics queries

### Processing:
- Parallel processing for CPU-intensive NLTK operations
- Intelligent caching for expensive LLM calls
- Progressive loading for large datasets
- Resource monitoring and auto-scaling

## Security Requirements

### Authentication & Authorization:
- Clerk-based user management
- JWT token validation
- Role-based access control
- API key rotation and management

### Data Protection:
- Input validation using Pydantic
- SQL injection prevention
- File upload security (virus scanning, type validation)
- Data encryption at rest and in transit

## Instructions for Creating New Instruction Files

### When Creating README.md Files:
```markdown
# [Directory/Component Name]

## Purpose
Brief description of what this directory/component does

## Structure
List of files and their responsibilities

## Dependencies
Other components this depends on

## Usage
How to use/interact with components in this directory

## Integration Points
How this connects to other parts of the system
```

### When Updating AI_Instructions.md:
1. Always update the service map when adding new services
2. Update the file structure when adding new directories
3. Update the current status when completing features
4. Add new database tables to the schema section
5. Document new API endpoints in the appropriate section

---

**Remember**: This is an AI-driven development project. Every AI working on this codebase should be able to understand the complete system architecture and current implementation status from these documentation files.

## 🚀 **Current System Status (September 2024)**

### **✅ PRODUCTION DEPLOYMENT COMPLETED** ✅
- **Frontend**: Successfully deployed to Vercel at https://ai-text-analysis-platform.vercel.app
- **Backend**: Successfully deployed to Railway at https://ai-text-analysis-platform-production.up.railway.app
- **Database**: PostgreSQL production database with full persistence
- **Auto-Deployment**: GitHub Actions workflow for seamless updates
- **CORS**: Cross-origin communication working between Vercel and Railway
- **Build System**: All TypeScript, import, and configuration issues resolved

### **✅ ENHANCED UPLOAD SYSTEM** (LATEST)
- **Multi-Mode Interface**: Traditional upload, flexible upload, and append modes
- **Flexible Data Support**: Upload any JSON/CSV structure with automatic processing
- **Append Functionality**: Add data to existing datasets via URL parameters
- **Smart Mode Detection**: Automatic interface switching based on URL parameters
- **Enhanced UX**: Improved upload page with clear mode separation

### **🆕 Latest Enhancements (v3.5.0)**
- **Production Deployment**: Complete end-to-end deployment with comprehensive documentation
- **Enhanced Upload System**: Multiple upload modes for different data structures
- **Append Mode**: URL parameter support for adding data to existing datasets (`?append=datasetId&name=datasetName`)
- **Deployment Documentation**: Created DEPLOYMENT.md and DEPLOYMENT_WALKTHROUGH.md guides
- **Build System**: Dockerized Railway deployment with proper Python environment
- **Error Resolution**: Fixed multiple TypeScript, import, and configuration issues

### **✅ Previous Enhancements (v2.5.0) - MAINTAINED**
- **NLTK Analysis Modes**: True differentiation between analysis modes
- **Enhanced Filtering**: NLTK stopwords + comprehensive user exclusions
- **Debug Logging**: Analysis mode processing verification in production
- **Force Regeneration**: API endpoints to clear cached word frequencies

### **🔧 Infrastructure Status** (DEPLOYMENT COMPLETED ✅)
- **GitHub Repository**: Connected to both Vercel and Railway for auto-deployment
- **Vercel Configuration**: Fixed build settings, module resolution, and TypeScript issues
- **Railway Configuration**: Dockerized deployment with PostgreSQL database
- **Environment Variables**: Production configuration working across both platforms
- **API Documentation**: Live Swagger docs available at production backend URL
- **Database Schema**: PostgreSQL tables created and data persistence verified
- **Health Monitoring**: Railway health checks and monitoring active
- **CORS Headers**: Proper cross-origin configuration for frontend-backend communication

### **🎯 PRODUCTION READY**
The application is fully deployed and operational with:
- ✅ Live frontend at Vercel with auto-deployment
- ✅ Live backend at Railway with PostgreSQL database
- ✅ Enhanced upload system with multiple data format support
- ✅ Comprehensive deployment documentation
- ✅ All build and configuration issues resolved

### **📋 Deployment Documentation Created**
- `DEPLOYMENT.md` - Complete deployment guide for GitHub, Vercel, and Railway
- `DEPLOYMENT_WALKTHROUGH.md` - Step-by-step manual deployment instructions
- `env.template` - Environment variable template
- `README.md` - Updated project documentation
- `.github/workflows/deploy.yml` - GitHub Actions workflow

*Last Updated: September 2024 - Production Deployment Completed*
