# Frontend - Next.js 14 Application

## Purpose
Frontend user interface for the AI-Powered Text Analysis Platform. Provides data upload, interactive visualizations, and analytics dashboard functionality.

## Technology Stack
- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS with custom components
- **State Management**: React Context API / Zustand
- **Authentication**: Clerk integration
- **Charts**: Recharts for data visualization
- **Real-time**: WebSocket client for job status updates
- **File Upload**: React Dropzone for bulk data ingestion

## Directory Structure

### `/components/`
- **`dashboard/`** - Analytics and metrics visualization components
- **`wordcloud/`** - Interactive word cloud visualization system
- **`datasets/`** - Data upload and management interface components
- **`query/`** - Natural language query interface components
- **`auth/`** - Authentication components and protected routes
- **`common/`** - Shared UI components and layout elements

### `/lib/`
- **`api.ts`** - API client for backend communication
- **`websocket.ts`** - WebSocket connection management
- **`types.ts`** - TypeScript type definitions
- **`auth.ts`** - Clerk authentication utilities
- **`utils.ts`** - Shared utility functions

### `/pages/`
- Next.js routing and page components
- API routes for client-side processing

### `/styles/`
- Tailwind CSS configuration and custom styles
- Component-specific styling

## Key Features

### Data Management
- Secure CSV file upload with progress tracking
- Real-time dataset processing status updates
- Dataset preview and validation

### Interactive Visualizations
- Multi-mode word cloud generation (entities, topics, sentiment)
- Comparative analysis between queries and responses
- Interactive filtering and drill-down capabilities
- Export functionality (PNG, SVG, PDF)

### Analytics Dashboard
- Sentiment analysis trends over time
- Topic modeling visualization
- Entity relationship networks
- Response quality metrics
- Business intelligence insights

### Real-time Features
- WebSocket integration for live processing updates
- Progress tracking for large dataset analysis
- Error notification and recovery

## Dependencies
- Backend API (FastAPI) for data processing
- Clerk for user authentication and management
- WebSocket server for real-time communication

## Setup and Installation

```bash
# Install dependencies
npm install

# Create environment variables
cp .env.local.example .env.local
# Edit .env.local with your configuration

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linting
npm run lint

# Run type checking
npm run type-check
```

## Environment Variables

Create a `.env.local` file with the following variables:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_key_here
CLERK_SECRET_KEY=sk_test_your_secret_key_here
```

## Current Implementation Status

✅ **Completed:**
- Next.js 14 with TypeScript setup
- Tailwind CSS configuration with custom design system
- Clerk authentication integration (structure ready)
- API client with comprehensive service classes
- WebSocket client for real-time updates
- TypeScript types matching backend models
- Utility functions and helpers
- Landing page with feature showcase
- Basic dashboard structure
- ESLint and Prettier configuration

⏳ **Pending Implementation:**
- Complete dataset upload components
- Interactive word cloud visualization
- Analytics dashboard components
- Real-time progress tracking
- Export functionality
- Advanced filtering and search
- Mobile responsiveness optimization

## Integration Points
- **Backend API**: REST endpoints for data and analysis
- **WebSocket**: Real-time processing updates
- **Clerk**: User authentication and session management
- **File Storage**: Direct S3 integration for large file handling

## Environment Variables
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

*Last Updated: Initial project structure creation*
