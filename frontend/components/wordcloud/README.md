# Word Cloud Components

This directory contains the enhanced word cloud visualization system with multiple analysis modes, interactive features, and comprehensive export capabilities.

## Components Overview

### `WordCloudVisualization.tsx`
**Main word cloud component with advanced features**

- **Multiple Analysis Modes**: All words, verbs, themes, emotions, entities, topics
- **Interactive Features**: Click/hover interactions, zooming, word selection
- **Layout Algorithms**: Spiral, random, and grid positioning with collision detection
- **Real-time Animations**: Entrance animations and hover effects
- **Responsive Design**: Adapts to different screen sizes and containers

**Key Props:**
```typescript
interface WordCloudVisualizationProps {
  datasetId: string;
  mode: 'all' | 'verbs' | 'themes' | 'emotions' | 'entities' | 'topics';
  filters: WordCloudFilters;
  interactiveMode?: boolean;
  onWordClick?: (word: string, data: WordCloudData) => void;
  onThemeClick?: (theme: string) => void;
  className?: string;
  height?: number;
  width?: number;
}
```

### `WordCloudControls.tsx`
**Comprehensive control panel for word cloud customization**

- **Analysis Mode Selection**: Visual mode picker with descriptions
- **Advanced Filtering**: Organization, sentiment, date range, question type, complexity
- **Display Options**: Layout mode, animation settings, color schemes
- **Active Filter Management**: Visual filter summary with quick removal

**Features:**
- Tabbed interface (Mode, Filters, Display)
- Real-time filter preview
- Intuitive form controls
- Filter persistence and management

### `WordCloudExport.tsx`
**Multi-format export system with advanced settings**

- **Export Formats**: PNG, SVG, PDF, CSV, JSON
- **Custom Settings**: Image dimensions, quality, background color, metadata inclusion
- **Share Functionality**: Generate shareable links with embedded filters
- **Progress Tracking**: Real-time export status and error handling

**Export Capabilities:**
- **PNG**: High-resolution raster images with quality control
- **SVG**: Scalable vector graphics for print and web
- **PDF**: Professional documents with metadata and analysis summary
- **CSV/JSON**: Raw data export for further analysis
- **Share Links**: Shareable URLs with embedded configuration

### `InteractiveWordCloud.tsx`
**Enhanced interactive features and word relationship visualization**

- **Advanced Interactions**: Hover vs. click modes, word selection, similar word highlighting
- **Cluster Visualization**: Automatic word clustering with theme detection
- **Search and Filter**: Real-time word search with instant results
- **Detail Panels**: Comprehensive word information and statistics
- **Fullscreen Support**: Immersive fullscreen viewing experience

## Usage Examples

### Basic Word Cloud
```typescript
import WordCloudVisualization from '@/components/wordcloud/WordCloudVisualization';

function MyComponent() {
  const handleWordClick = (word: string, data: WordCloudData) => {
    console.log('Word clicked:', word, data);
  };

  return (
    <WordCloudVisualization
      datasetId="dataset-123"
      mode="all"
      filters={{}}
      onWordClick={handleWordClick}
      height={500}
      width={800}
    />
  );
}
```

### With Controls and Export
```typescript
import WordCloudVisualization from '@/components/wordcloud/WordCloudVisualization';
import { useState } from 'react';

function AdvancedWordCloud() {
  const [mode, setMode] = useState<'all' | 'verbs' | 'themes'>('all');
  const [filters, setFilters] = useState<WordCloudFilters>({});

  return (
    <div className="space-y-4">
      <WordCloudVisualization
        datasetId="dataset-123"
        mode={mode}
        filters={filters}
        interactiveMode={true}
      />
      {/* Controls and export panels are integrated within the component */}
    </div>
  );
}
```

### Standalone Interactive Features
```typescript
import InteractiveWordCloud from '@/components/wordcloud/InteractiveWordCloud';

function InteractiveDemo() {
  const [selectedWord, setSelectedWord] = useState<string | null>(null);
  const [hoveredWord, setHoveredWord] = useState<string | null>(null);

  return (
    <InteractiveWordCloud
      words={wordData}
      selectedWord={selectedWord}
      hoveredWord={hoveredWord}
      filters={filters}
      onWordSelect={setSelectedWord}
      onWordHover={setHoveredWord}
      onFilterChange={setFilters}
    />
  );
}
```

## Features

### Analysis Modes
- **All Words**: Complete vocabulary analysis
- **Verbs**: Action-oriented language focus
- **Themes**: Thematic categorization
- **Emotions**: Emotional language detection
- **Entities**: Named entity recognition results
- **Topics**: Topic modeling visualization

### Interactive Features
- **Word Selection**: Click or hover to select words
- **Similar Word Highlighting**: Automatic similarity detection
- **Cluster Visualization**: Theme-based word grouping
- **Search and Filter**: Real-time word search
- **Zoom and Pan**: Navigate large word clouds
- **Fullscreen Mode**: Immersive viewing experience

### Layout Algorithms
- **Spiral Layout**: Traditional spiral arrangement from center
- **Random Layout**: Collision-avoiding random positioning
- **Grid Layout**: Organized grid-based arrangement

### Export Capabilities
- **Image Formats**: PNG (raster) and SVG (vector)
- **Documents**: PDF with analysis summary and metadata
- **Data Formats**: CSV and JSON for further analysis
- **Sharing**: Generate shareable links with embedded settings

### Customization Options
- **Dimensions**: Configurable width and height
- **Colors**: Sentiment-based color coding
- **Fonts**: Configurable font sizes and weights
- **Animations**: Entrance animations and transitions
- **Themes**: Multiple color schemes (expandable)

## Integration with Backend

The word cloud components integrate seamlessly with the backend API:

- **Data Fetching**: Automatic API calls to generate word cloud data
- **Real-time Updates**: WebSocket integration for processing status
- **Export API**: Server-side export generation for complex formats
- **Caching**: Intelligent caching of generated word clouds

## Performance Optimizations

- **Collision Detection**: Efficient spatial algorithms for word positioning
- **Virtualization**: Large dataset handling with performance optimization
- **Lazy Loading**: On-demand component loading
- **Memoization**: React.memo and useMemo for expensive calculations
- **Canvas Rendering**: Hardware-accelerated rendering for smooth animations

## Accessibility Features

- **Keyboard Navigation**: Full keyboard support for interactive elements
- **Screen Reader Support**: Proper ARIA labels and descriptions
- **Color Contrast**: Sufficient contrast for all text elements
- **Focus Management**: Clear focus indicators and logical tab order

## Browser Support

- **Modern Browsers**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Mobile Support**: Responsive design with touch interactions
- **SVG Support**: Full SVG rendering capabilities required
- **HTML5 Canvas**: Required for image export functionality

## Development Notes

### Mock Data Generation
The components include mock data generators for development and testing:
- Realistic word frequency distributions
- Sentiment assignment based on word categories
- Category-based clustering for demonstration

### Extensibility
The architecture supports easy extension:
- New analysis modes can be added to `ANALYSIS_MODES`
- Additional export formats can be implemented in `WordCloudExport`
- Custom layout algorithms can be added to the positioning system
- New interactive features can be integrated into `InteractiveWordCloud`

### Testing Considerations
- Unit tests for positioning algorithms
- Integration tests for API communication
- Visual regression tests for rendering consistency
- Performance tests for large datasets
- Accessibility tests for screen reader compatibility

*Last Updated: Initial implementation*
