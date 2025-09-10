'use client';

import React, { useEffect, useState, useMemo, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  RefreshCw, 
  Download, 
  Settings, 
  Info,
  ZoomIn,
  ZoomOut,
  RotateCcw 
} from 'lucide-react';
import { WordCloudProps, WordCloudData, WordCloudFilters } from '@/lib/types';
import { cn, getSentimentColor, formatNumber } from '@/lib/utils';
import WordCloudControls from './WordCloudControls';
import WordCloudExport from './WordCloudExport';

interface WordCloudVisualizationProps extends WordCloudProps {
  datasetId: string;
  className?: string;
  height?: number;
  width?: number | string;
  onDataUpdate?: (data: WordCloudData[]) => void;
}

interface WordPosition {
  x: number;
  y: number;
  word: string;
  size: number;
  color: string;
  rotation: number;
  opacity: number;
}

export default function WordCloudVisualization({
  datasetId,
  mode,
  filters,
  interactiveMode = true,
  onWordClick,
  onThemeClick,
  className,
  height = 500,
  width = 800,
  onDataUpdate,
}: WordCloudVisualizationProps) {
  // Convert width to number if it's a percentage string
  const numericWidth = typeof width === 'string' && width === '100%' ? 800 : (typeof width === 'number' ? width : 800);
  // State management
  const [words, setWords] = useState<WordCloudData[]>([]);
  const [positions, setPositions] = useState<WordPosition[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedWord, setSelectedWord] = useState<string | null>(null);
  const [showControls, setShowControls] = useState(false);
  const [showExport, setShowExport] = useState(false);
  const [zoom, setZoom] = useState(1);
  const [hoveredWord, setHoveredWord] = useState<string | null>(null);

  // Animation settings
  const [animationEnabled, setAnimationEnabled] = useState(true);
  const [layoutMode, setLayoutMode] = useState<'spiral' | 'random' | 'grid'>('spiral');

  // Generate word cloud data
  const generateWordCloud = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // This would connect to your API - for now, generating mock data
      const mockWords = generateMockWordData(mode, filters);
      setWords(mockWords);
      
      if (onDataUpdate) {
        onDataUpdate(mockWords);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate word cloud');
    } finally {
      setLoading(false);
    }
  }, [datasetId, mode, filters, onDataUpdate]);

  // Collision detection helper (defined before use)
  const hasCollision = useCallback((existing: WordPosition[], x: number, y: number, size: number, word: string): boolean => {
    if (existing.length === 0) return false;
    
    const wordWidth = word.length * size * 0.6;
    const wordHeight = size;
    const padding = 8; // Space between words
    
    return existing.some(pos => {
      const existingWidth = pos.word.length * pos.size * 0.6;
      const existingHeight = pos.size;
      
      // Check if rectangles overlap (with padding)
      return (
        x < pos.x + existingWidth/2 + padding &&
        x + wordWidth > pos.x - existingWidth/2 - padding &&
        y < pos.y + existingHeight/2 + padding &&
        y + wordHeight > pos.y - existingHeight/2 - padding
      );
    });
  }, []);

  // Calculate word positions using spiral algorithm
  const calculatePositions = useMemo(() => {
    if (words.length === 0) return [];

    const centerX = numericWidth / 2;
    const centerY = height / 2;
    const positions: WordPosition[] = [];
    const margin = 40; // Larger margin from edges

    // Sort words by frequency/size for better placement (largest first)
    const sortedWords = [...words].sort((a, b) => b.size - a.size);

    if (layoutMode === 'spiral') {
      // Improved spiral layout algorithm
      sortedWords.forEach((word, index) => {
        const fontSize = Math.max(16, Math.min(48, word.size * 32));
        const wordWidth = word.word.length * fontSize * 0.65;
        const wordHeight = fontSize;
        
        let x: number = centerX; // Default to center
        let y: number = centerY; // Default to center
        let placed = false;
        
        if (index === 0) {
          // Place first (largest) word in center
          x = centerX;
          y = centerY;
          placed = true;
        } else {
          // Spiral placement for subsequent words
          let radius = 60;
          let angle = index * 1.5; // Start with different angles for each word
          const angleIncrement = 0.8;
          const radiusIncrement = 12;
          let attempts = 0;
          
          while (!placed && attempts < 150) {
            x = centerX + radius * Math.cos(angle);
            y = centerY + radius * Math.sin(angle);
            
            // Ensure word stays within bounds with proper margins
            if (x - wordWidth/2 > margin && 
                x + wordWidth/2 < numericWidth - margin &&
                y - wordHeight/2 > margin && 
                y + wordHeight/2 < height - margin &&
                !hasCollision(positions, x, y, fontSize, word.word)) {
              placed = true;
            } else {
              angle += angleIncrement;
              if (angle > (index + 1) * 2 * Math.PI) {
                angle = index * 1.5; // Reset angle
                radius += radiusIncrement;
              }
              attempts++;
            }
          }
          
          // Fallback positioning if spiral fails
          if (!placed) {
            x = margin + (index % 8) * (numericWidth - 2 * margin) / 8;
            y = margin + Math.floor(index / 8) * 50;
          }
        }

        positions.push({
          x,
          y,
          word: word.word,
          size: fontSize,
          color: getSentimentColor(word.sentiment),
          rotation: 0, // Remove rotation for better readability
          opacity: word.frequency > 30 ? 1 : 0.9
        });
      });
    } else if (layoutMode === 'random') {
      // Improved random positioning with collision avoidance
      sortedWords.forEach((word) => {
        const fontSize = Math.max(16, Math.min(48, word.size * 32));
        const wordWidth = word.word.length * fontSize * 0.65;
        const wordHeight = fontSize;
        let x: number = centerX; // Default to center
        let y: number = centerY; // Default to center
        let attempts = 0;
        let placed = false;
        
        while (!placed && attempts < 100) {
          x = margin + Math.random() * (numericWidth - 2 * margin - wordWidth);
          y = margin + Math.random() * (height - 2 * margin - wordHeight);
          
          if (!hasCollision(positions, x, y, fontSize, word.word)) {
            placed = true;
          }
          attempts++;
        }
        
        // Grid fallback if random fails
        if (!placed) {
          const gridX = margin + (attempts % 6) * 120;
          const gridY = margin + Math.floor(attempts / 6) * 60;
          x = Math.min(gridX, numericWidth - margin - wordWidth);
          y = Math.min(gridY, height - margin - wordHeight);
        }

        positions.push({
          x,
          y,
          word: word.word,
          size: fontSize,
          color: getSentimentColor(word.sentiment),
          rotation: Math.random() * 20 - 10, // Very small rotation
          opacity: word.frequency > 30 ? 1 : 0.9
        });
      });
    } else if (layoutMode === 'grid') {
      // Grid layout with proper spacing
      const cols = Math.min(Math.ceil(Math.sqrt(sortedWords.length)), 6); // Max 6 columns
      const rows = Math.ceil(sortedWords.length / cols);
      const cellWidth = (numericWidth - 2 * margin) / cols;
      const cellHeight = (height - 2 * margin) / rows;

      sortedWords.forEach((word, index) => {
        const col = index % cols;
        const row = Math.floor(index / cols);
        const fontSize = Math.max(16, Math.min(40, word.size * 28));

        positions.push({
          x: margin + col * cellWidth + cellWidth / 2,
          y: margin + row * cellHeight + cellHeight / 2,
          word: word.word,
          size: fontSize,
          color: getSentimentColor(word.sentiment),
          rotation: 0,
          opacity: word.frequency > 30 ? 1 : 0.9
        });
      });
    }

    return positions;
  }, [words, numericWidth, height, layoutMode, hasCollision]);

  // Update positions when words change
  useEffect(() => {
    setPositions(calculatePositions);
  }, [calculatePositions]);

  // Generate word cloud on mount and when dependencies change
  useEffect(() => {
    generateWordCloud();
  }, [generateWordCloud]);

  // Handle word click
  const handleWordClick = (word: WordCloudData) => {
    setSelectedWord(word.word);
    if (onWordClick) {
      onWordClick(word.word, word);
    }
  };

  // Handle theme click
  const handleThemeClick = (theme: string) => {
    if (onThemeClick) {
      onThemeClick(theme);
    }
  };

  // Zoom functions
  const zoomIn = () => setZoom(prev => Math.min(prev * 1.2, 3));
  const zoomOut = () => setZoom(prev => Math.max(prev / 1.2, 0.5));
  const resetZoom = () => setZoom(1);

  if (loading) {
    return (
      <div className={cn("flex items-center justify-center bg-white rounded-lg border", className)} style={{ height, width: typeof width === 'string' ? width : numericWidth }}>
        <div className="text-center">
          <RefreshCw className="h-8 w-8 text-primary-600 animate-spin mx-auto mb-2" />
          <p className="text-gray-600">Generating word cloud...</p>
          <p className="text-xs text-gray-500">Mode: {mode}</p>
          <div className="mt-2">
            <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden mx-auto">
              <div className="h-full bg-primary-600 rounded-full animate-pulse w-3/4"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={cn("flex items-center justify-center bg-red-50 border border-red-200 rounded-lg", className)} style={{ height, width: typeof width === 'string' ? width : numericWidth }}>
        <div className="text-center text-red-600">
          <p className="font-medium">Failed to generate word cloud</p>
          <p className="text-sm mt-1">{error}</p>
          <button
            onClick={generateWordCloud}
            className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={cn("relative bg-white rounded-lg border shadow-sm", className)}>
      {/* Header with controls */}
      <div className="flex items-center justify-between p-4 border-b">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Word Cloud - {mode.charAt(0).toUpperCase() + mode.slice(1)} Analysis
          </h3>
          <p className="text-sm text-gray-500">
            {formatNumber(words.length)} words • {Object.keys(filters).length} filters applied
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowControls(!showControls)}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            title="Controls"
          >
            <Settings className="h-5 w-5" />
          </button>
          
          <button
            onClick={() => setShowExport(!showExport)}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            title="Export"
          >
            <Download className="h-5 w-5" />
          </button>
          
          <button
            onClick={generateWordCloud}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            title="Refresh"
          >
            <RefreshCw className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Controls Panel */}
      <AnimatePresence>
        {showControls && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="border-b"
          >
            <WordCloudControls
              mode={mode}
              filters={filters}
              animationEnabled={animationEnabled}
              layoutMode={layoutMode}
              onModeChange={(newMode) => {/* Handle mode change */}}
              onFiltersChange={(newFilters) => {/* Handle filters change */}}
              onAnimationToggle={setAnimationEnabled}
              onLayoutModeChange={setLayoutMode}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Export Panel */}
      <AnimatePresence>
        {showExport && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="border-b"
          >
            <WordCloudExport
              datasetId={datasetId}
              mode={mode}
              filters={filters}
              words={words}
              onExportComplete={() => setShowExport(false)}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Zoom Controls */}
      {interactiveMode && (
        <div className="absolute top-20 right-4 flex flex-col gap-2 bg-white border rounded-lg shadow-sm p-2">
          <button
            onClick={zoomIn}
            className="p-2 text-gray-600 hover:text-primary-600 hover:bg-primary-50 rounded transition-colors"
            title="Zoom In"
          >
            <ZoomIn className="h-4 w-4" />
          </button>
          <button
            onClick={resetZoom}
            className="p-2 text-gray-600 hover:text-primary-600 hover:bg-primary-50 rounded transition-colors"
            title="Reset Zoom"
          >
            <RotateCcw className="h-4 w-4" />
          </button>
          <button
            onClick={zoomOut}
            className="p-2 text-gray-600 hover:text-primary-600 hover:bg-primary-50 rounded transition-colors"
            title="Zoom Out"
          >
            <ZoomOut className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Word Cloud Canvas */}
      <div 
        className="relative overflow-hidden"
        style={{ height, width: typeof width === 'string' ? width : numericWidth }}
      >
        <svg
          data-testid="wordcloud-svg"
          width={numericWidth}
          height={height}
          className="cursor-grab active:cursor-grabbing w-full"
          style={{ transform: `scale(${zoom})`, transformOrigin: 'center' }}
          viewBox={`0 0 ${numericWidth} ${height}`}
        >
          <AnimatePresence>
            {positions.map((position, index) => {
              const word = words.find(w => w.word === position.word);
              if (!word) return null;

              return (
                <motion.g
                  key={position.word}
                  initial={animationEnabled ? { opacity: 0, scale: 0 } : {}}
                  animate={{ 
                    opacity: position.opacity,
                    scale: hoveredWord === position.word ? 1.1 : 1
                  }}
                  exit={{ opacity: 0, scale: 0 }}
                  transition={{ 
                    delay: animationEnabled ? index * 0.08 : 0,
                    duration: 0.4,
                    ease: "easeOut"
                  }}
                  className={interactiveMode ? "cursor-pointer" : ""}
                  onClick={() => interactiveMode && handleWordClick(word)}
                  onMouseEnter={() => interactiveMode && setHoveredWord(position.word)}
                  onMouseLeave={() => interactiveMode && setHoveredWord(null)}
                >
                  <text
                    x={position.x}
                    y={position.y}
                    fontSize={position.size}
                    fill={position.color}
                    transform={position.rotation !== 0 ? `rotate(${position.rotation}, ${position.x}, ${position.y})` : undefined}
                    className={cn(
                      "select-none font-semibold",
                      interactiveMode && "hover:opacity-90 transition-all duration-200",
                      selectedWord === position.word && "opacity-100 font-bold",
                      hoveredWord === position.word && "drop-shadow-sm"
                    )}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    style={{
                      fontFamily: 'Inter, system-ui, sans-serif',
                      paintOrder: 'stroke fill',
                      stroke: hoveredWord === position.word ? 'rgba(255,255,255,0.8)' : 'transparent',
                      strokeWidth: hoveredWord === position.word ? 3 : 0
                    }}
                  >
                    {position.word}
                  </text>
                  
                  {/* Hover effect background */}
                  {hoveredWord === position.word && interactiveMode && (
                    <motion.rect
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 0.1 }}
                      x={position.x - (position.word.length * position.size * 0.3)}
                      y={position.y - position.size * 0.6}
                      width={position.word.length * position.size * 0.6}
                      height={position.size * 1.2}
                      fill={position.color}
                      rx={4}
                      className="pointer-events-none"
                    />
                  )}
                </motion.g>
              );
            })}
          </AnimatePresence>
        </svg>

        {/* Word details tooltip */}
        {hoveredWord && interactiveMode && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="absolute bottom-4 left-4 bg-black text-white px-3 py-2 rounded-lg text-sm"
          >
            <div className="font-medium">{hoveredWord}</div>
            {(() => {
              const word = words.find(w => w.word === hoveredWord);
              if (word) {
                return (
                  <div className="text-xs opacity-75">
                    Frequency: {formatNumber(word.frequency)} • 
                    Sentiment: {word.sentiment || 'neutral'}
                    {word.category && ` • Category: ${word.category}`}
                  </div>
                );
              }
              return null;
            })()}
          </motion.div>
        )}
      </div>

      {/* Statistics Footer */}
      <div className="flex items-center justify-between p-4 border-t bg-gray-50 text-sm text-gray-600">
        <div className="flex items-center gap-4">
          <span>Total words: {formatNumber(words.length)}</span>
          <span>•</span>
          <span>Zoom: {Math.round(zoom * 100)}%</span>
          <span>•</span>
          <span>Layout: {layoutMode}</span>
          <span>•</span>
          <span>Canvas: {numericWidth}×{height}</span>
        </div>
        
        {selectedWord && (
          <div className="flex items-center gap-2">
            <Info className="h-4 w-4" />
            <span>Selected: <strong>{selectedWord}</strong></span>
          </div>
        )}
        
        {hoveredWord && !selectedWord && (
          <div className="flex items-center gap-2">
            <span>Hover: <strong>{hoveredWord}</strong></span>
          </div>
        )}
      </div>
    </div>
  );
}

// Mock data generator for development
function generateMockWordData(mode: string, filters: WordCloudFilters): WordCloudData[] {
  const baseWords = {
    all: ['customer', 'support', 'issue', 'help', 'service', 'problem', 'question', 'response', 'solution', 'experience', 'quality', 'team', 'product', 'feedback', 'process'],
    verbs: ['help', 'solve', 'fix', 'support', 'assist', 'resolve', 'provide', 'understand', 'explain', 'improve', 'create', 'update', 'manage', 'deliver', 'analyze'],
    themes: ['billing', 'technical', 'account', 'feature', 'bug', 'feedback', 'complaint', 'praise', 'suggestion', 'inquiry', 'training', 'documentation', 'integration', 'security', 'performance'],
    emotions: ['frustrated', 'satisfied', 'confused', 'happy', 'angry', 'grateful', 'disappointed', 'excited', 'worried', 'pleased', 'calm', 'surprised', 'motivated', 'concerned', 'optimistic'],
    entities: ['John Smith', 'Product X', 'Chicago', 'Department Y', 'System Z', 'Company ABC', 'Team Lead', 'Manager', 'Customer ID', 'Order #123', 'Sarah Johnson', 'Project Alpha', 'New York', 'Sales Team', 'Platform Beta'],
    topics: ['payment', 'interface', 'migration', 'performance', 'security', 'features', 'bugs', 'training', 'integration', 'mobile', 'analytics', 'workflow', 'automation', 'compliance', 'scalability']
  };

  const words = baseWords[mode as keyof typeof baseWords] || baseWords.all;
  const sentiments: Array<'positive' | 'negative' | 'neutral'> = ['positive', 'negative', 'neutral'];

  return words.map((word, index) => ({
    word,
    frequency: Math.random() * 80 + 20, // Higher minimum frequency
    sentiment: sentiments[index % sentiments.length], // More predictable distribution
    category: mode,
    size: 0.3 + (Math.random() * 0.7), // Better size distribution 0.3 to 1.0
    color: getSentimentColor(sentiments[index % sentiments.length]),
  }));
}
