# Frontend Components

## Purpose
React components organized by feature area, providing the complete user interface for the AI-Powered Text Analysis Platform.

## Directory Structure

### `/dashboard/`
Analytics and metrics visualization components
- `AdvancedSentimentPanel.tsx` - NLTK sentiment analysis with trends
- `TopicModelingView.tsx` - LDA topics with interactive exploration
- `EntityAnalysisPanel.tsx` - Named entity recognition results
- `QuestionClassificationView.tsx` - Question type distribution
- `ConversationQualityMetrics.tsx` - AI response quality analysis
- `BusinessInsightsPanel.tsx` - LLM-generated insights
- `ExportCenter.tsx` - Multi-format export options

### `/wordcloud/`
Interactive word cloud visualization system
- `WordCloudVisualization.tsx` - Main word cloud component (enhanced from MVP)
- `WordCloudControls.tsx` - Filtering and mode selection controls
- `WordCloudExport.tsx` - Export functionality for visualizations
- `InteractiveWordCloud.tsx` - Interactive exploration features

### `/datasets/`
Data upload and management interface components
- `DatasetUpload.tsx` - Password-protected upload with chunking
- `DatasetList.tsx` - Dataset listing with processing status
- `DatasetPreview.tsx` - Preview with NLTK analysis preview
- `UploadProgress.tsx` - Real-time progress with job status
- `ProcessingStatus.tsx` - Background job status display

### `/query/`
Natural language query interface components
- `NaturalLanguageQuery.tsx` - Natural language query interface (from MVP)
- `QueryBuilder.tsx` - Advanced query construction
- `QueryHistory.tsx` - Query history and saved queries
- `QueryExport.tsx` - Export query results

### `/auth/`
Authentication components and protected routes
- `AuthHeader.tsx` - Authentication header component (from MVP)
- `LoginForm.tsx` - User login interface
- `ProtectedRoute.tsx` - Route protection wrapper

### `/common/`
Shared UI components and layout elements
- `Layout.tsx` - Main application layout
- `LoadingSpinner.tsx` - Loading state indicators
- `ProgressBar.tsx` - Progress visualization
- `ErrorBoundary.tsx` - Error handling wrapper
- `WebSocketProvider.tsx` - WebSocket connection provider

## Component Patterns

### Standard Component Structure
```typescript
interface ComponentProps {
  // Typed props with JSDoc comments
}

export default function Component({ 
  prop1, 
  prop2 
}: ComponentProps) {
  // Hooks for state management
  // WebSocket integration where needed
  // Error handling
  // Loading states
  
  return (
    // JSX with proper accessibility
    // Responsive design with Tailwind
    // Interactive elements
  );
}
```

### Integration Points
- **API Communication**: All components use centralized API client
- **Real-time Updates**: WebSocket integration for live data
- **State Management**: React Context or Zustand for shared state
- **Error Handling**: Consistent error boundaries and user feedback
- **Authentication**: Clerk integration throughout protected components

### Design Standards
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Accessibility**: WCAG 2.1 compliance with proper ARIA labels
- **Loading States**: Skeleton loaders and progress indicators
- **Error States**: User-friendly error messages with recovery actions
- **Interactive Elements**: Hover states, animations, and feedback

*Last Updated: Initial project structure creation*
