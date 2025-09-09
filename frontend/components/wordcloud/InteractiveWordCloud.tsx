'use client';

import React, { useState, useCallback, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Info, 
  Search, 
  Filter, 
  Eye, 
  EyeOff, 
  Maximize, 
  Minimize,
  MousePointer,
  Move3D
} from 'lucide-react';
import { WordCloudData, WordCloudFilters } from '@/lib/types';
import { cn, formatNumber, getSentimentColor } from '@/lib/utils';

interface InteractiveWordCloudProps {
  words: WordCloudData[];
  selectedWord?: string | null;
  hoveredWord?: string | null;
  filters: WordCloudFilters;
  onWordSelect: (word: string | null) => void;
  onWordHover: (word: string | null) => void;
  onFilterChange: (filters: WordCloudFilters) => void;
  className?: string;
}

interface WordDetailPanel {
  word: WordCloudData;
  position: { x: number; y: number };
}

interface WordClusterInfo {
  center: { x: number; y: number };
  words: WordCloudData[];
  theme: string;
  avgSentiment: number;
}

export default function InteractiveWordCloud({
  words,
  selectedWord,
  hoveredWord,
  filters,
  onWordSelect,
  onWordHover,
  onFilterChange,
  className
}: InteractiveWordCloudProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [showDetails, setShowDetails] = useState(true);
  const [wordDetails, setWordDetails] = useState<WordDetailPanel | null>(null);
  const [highlightSimilar, setHighlightSimilar] = useState(false);
  const [showClusters, setShowClusters] = useState(false);
  const [clusters, setClusters] = useState<WordClusterInfo[]>([]);
  const [interactionMode, setInteractionMode] = useState<'hover' | 'click'>('hover');
  const [isFullscreen, setIsFullscreen] = useState(false);

  const containerRef = useRef<HTMLDivElement>(null);
  const detailsRef = useRef<HTMLDivElement>(null);

  // Filter words based on search query
  const filteredWords = words.filter(word =>
    word.word.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Find similar words (by sentiment, category, or co-occurrence)
  const findSimilarWords = useCallback((targetWord: string): string[] => {
    const target = words.find(w => w.word === targetWord);
    if (!target) return [];

    return words
      .filter(w => 
        w.word !== targetWord && (
          w.sentiment === target.sentiment ||
          w.category === target.category ||
          Math.abs((w.frequency || 0) - (target.frequency || 0)) < 10
        )
      )
      .map(w => w.word)
      .slice(0, 5); // Limit to 5 similar words
  }, [words]);

  // Calculate word clusters based on position and similarity
  useEffect(() => {
    if (!showClusters) {
      setClusters([]);
      return;
    }

    // Simple clustering algorithm based on word categories
    const clusterMap: { [key: string]: WordClusterInfo } = {};
    
    words.forEach(word => {
      const category = word.category || 'general';
      if (!clusterMap[category]) {
        clusterMap[category] = {
          center: { x: 0, y: 0 },
          words: [],
          theme: category,
          avgSentiment: 0
        };
      }
      clusterMap[category].words.push(word);
    });

    // Calculate cluster centers and average sentiment
    const clusterList = Object.values(clusterMap).map(cluster => {
      const sentimentSum = cluster.words.reduce((sum, word) => {
        const sentimentScore = word.sentiment === 'positive' ? 1 : 
                              word.sentiment === 'negative' ? -1 : 0;
        return sum + sentimentScore;
      }, 0);
      
      return {
        ...cluster,
        avgSentiment: sentimentSum / cluster.words.length,
        center: {
          x: Math.random() * 600 + 100, // Mock positions - would be calculated from actual layout
          y: Math.random() * 400 + 100
        }
      };
    });

    setClusters(clusterList);
  }, [words, showClusters]);

  // Handle word interaction
  const handleWordInteraction = useCallback((word: string, event: React.MouseEvent) => {
    const rect = event.currentTarget.getBoundingClientRect();
    const wordData = words.find(w => w.word === word);
    
    if (interactionMode === 'hover') {
      onWordHover(word);
    } else {
      onWordSelect(word === selectedWord ? null : word);
    }

    if (wordData && showDetails) {
      setWordDetails({
        word: wordData,
        position: {
          x: event.clientX - rect.left,
          y: event.clientY - rect.top
        }
      });
    }
  }, [interactionMode, selectedWord, words, showDetails, onWordHover, onWordSelect]);

  // Handle mouse leave
  const handleMouseLeave = useCallback(() => {
    if (interactionMode === 'hover') {
      onWordHover(null);
      if (!selectedWord) {
        setWordDetails(null);
      }
    }
  }, [interactionMode, selectedWord, onWordHover]);

  // Get similar words for highlighting
  const similarWords = highlightSimilar && (selectedWord || hoveredWord) 
    ? findSimilarWords(selectedWord || hoveredWord!) 
    : [];

  // Toggle fullscreen
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      containerRef.current?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  return (
    <div 
      ref={containerRef}
      className={cn("relative bg-white border border-gray-200 rounded-lg overflow-hidden", className)}
    >
      {/* Interactive Controls Header */}
      <div className="flex items-center justify-between p-3 border-b bg-gray-50">
        <div className="flex items-center gap-3">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search words..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 pr-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent w-48"
            />
          </div>

          {/* Interaction Mode Toggle */}
          <div className="flex items-center gap-1 p-1 bg-white border border-gray-300 rounded-lg">
            <button
              onClick={() => setInteractionMode('hover')}
              className={cn(
                "p-1.5 text-xs font-medium rounded transition-colors",
                interactionMode === 'hover' 
                  ? "bg-primary-600 text-white" 
                  : "text-gray-600 hover:text-gray-800"
              )}
              title="Hover to interact"
            >
              <MousePointer className="h-3 w-3" />
            </button>
            <button
              onClick={() => setInteractionMode('click')}
              className={cn(
                "p-1.5 text-xs font-medium rounded transition-colors",
                interactionMode === 'click' 
                  ? "bg-primary-600 text-white" 
                  : "text-gray-600 hover:text-gray-800"
              )}
              title="Click to select"
            >
              <Move3D className="h-3 w-3" />
            </button>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Toggle Options */}
          <button
            onClick={() => setHighlightSimilar(!highlightSimilar)}
            className={cn(
              "p-2 text-xs rounded-lg transition-colors",
              highlightSimilar 
                ? "bg-blue-100 text-blue-700" 
                : "text-gray-500 hover:text-gray-700 hover:bg-gray-100"
            )}
            title="Highlight similar words"
          >
            <Filter className="h-4 w-4" />
          </button>

          <button
            onClick={() => setShowClusters(!showClusters)}
            className={cn(
              "p-2 text-xs rounded-lg transition-colors",
              showClusters 
                ? "bg-purple-100 text-purple-700" 
                : "text-gray-500 hover:text-gray-700 hover:bg-gray-100"
            )}
            title="Show word clusters"
          >
            <Move3D className="h-4 w-4" />
          </button>

          <button
            onClick={() => setShowDetails(!showDetails)}
            className={cn(
              "p-2 text-xs rounded-lg transition-colors",
              showDetails 
                ? "bg-green-100 text-green-700" 
                : "text-gray-500 hover:text-gray-700 hover:bg-gray-100"
            )}
            title="Toggle details panel"
          >
            {showDetails ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
          </button>

          <button
            onClick={toggleFullscreen}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            title="Toggle fullscreen"
          >
            {isFullscreen ? <Minimize className="h-4 w-4" /> : <Maximize className="h-4 w-4" />}
          </button>
        </div>
      </div>

      {/* Word Cloud Interactive Layer */}
      <div className="relative">
        {/* Cluster Visualization */}
        {showClusters && (
          <div className="absolute inset-0 pointer-events-none z-10">
            <svg className="w-full h-full">
              {clusters.map((cluster, index) => (
                <g key={index}>
                  <circle
                    cx={cluster.center.x}
                    cy={cluster.center.y}
                    r={Math.sqrt(cluster.words.length) * 15}
                    fill={cluster.avgSentiment > 0 ? 'rgba(16, 185, 129, 0.1)' : 
                          cluster.avgSentiment < 0 ? 'rgba(239, 68, 68, 0.1)' : 
                          'rgba(107, 114, 128, 0.1)'}
                    stroke={cluster.avgSentiment > 0 ? 'rgba(16, 185, 129, 0.3)' : 
                            cluster.avgSentiment < 0 ? 'rgba(239, 68, 68, 0.3)' : 
                            'rgba(107, 114, 128, 0.3)'}
                    strokeWidth="2"
                    strokeDasharray="5,5"
                  />
                  <text
                    x={cluster.center.x}
                    y={cluster.center.y - Math.sqrt(cluster.words.length) * 15 - 10}
                    textAnchor="middle"
                    className="text-xs font-medium fill-gray-600"
                  >
                    {cluster.theme} ({cluster.words.length})
                  </text>
                </g>
              ))}
            </svg>
          </div>
        )}

        {/* Word Highlighting Effects */}
        {(selectedWord || hoveredWord) && (
          <div className="absolute inset-0 pointer-events-none z-20">
            <svg className="w-full h-full">
              {/* Connection lines to similar words */}
              {highlightSimilar && similarWords.map((similarWord, index) => {
                // Mock positions - in real implementation, these would come from word positions
                const startX = 300 + Math.cos(index * 0.5) * 100;
                const startY = 200 + Math.sin(index * 0.5) * 100;
                const endX = 300 + Math.cos((index + 1) * 0.5) * 120;
                const endY = 200 + Math.sin((index + 1) * 0.5) * 120;
                
                return (
                  <line
                    key={similarWord}
                    x1={startX}
                    y1={startY}
                    x2={endX}
                    y2={endY}
                    stroke="rgba(59, 130, 246, 0.4)"
                    strokeWidth="2"
                    strokeDasharray="3,3"
                  />
                );
              })}
            </svg>
          </div>
        )}

        {/* Main Word Cloud Container */}
        <div
          className="relative min-h-[400px] cursor-crosshair"
          onMouseLeave={handleMouseLeave}
        >
          {/* Words would be rendered here - this is a placeholder for the actual word cloud */}
          <div className="flex flex-wrap items-center justify-center gap-2 p-8 min-h-[400px]">
            {filteredWords.map((word, index) => {
              const isSelected = selectedWord === word.word;
              const isHovered = hoveredWord === word.word;
              const isSimilar = similarWords.includes(word.word);
              const shouldHighlight = isSelected || isHovered || isSimilar;
              const fontSize = Math.max(12, Math.min(36, (word.frequency || 0) / 3));
              
              return (
                <motion.span
                  key={word.word}
                  className={cn(
                    "inline-block px-2 py-1 rounded cursor-pointer transition-all duration-200 select-none",
                    shouldHighlight ? "opacity-100 z-10" : "opacity-70",
                    isSelected && "ring-2 ring-primary-500 bg-primary-50",
                    isHovered && !isSelected && "bg-gray-100 shadow-sm",
                    isSimilar && "ring-1 ring-blue-300 bg-blue-50"
                  )}
                  style={{
                    fontSize: `${fontSize}px`,
                    color: getSentimentColor(word.sentiment),
                    fontWeight: shouldHighlight ? 600 : 400,
                    transform: shouldHighlight ? 'scale(1.1)' : 'scale(1)'
                  }}
                  whileHover={{ scale: 1.1, zIndex: 20 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={(e) => handleWordInteraction(word.word, e)}
                  onMouseEnter={(e) => {
                    if (interactionMode === 'hover') {
                      handleWordInteraction(word.word, e);
                    }
                  }}
                  layout
                >
                  {word.word}
                </motion.span>
              );
            })}
          </div>
        </div>
      </div>

      {/* Word Details Panel */}
      <AnimatePresence>
        {wordDetails && showDetails && (
          <motion.div
            ref={detailsRef}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="absolute top-16 right-4 bg-white border border-gray-200 rounded-lg shadow-lg p-4 w-80 z-30"
            style={{
              maxHeight: 'calc(100% - 100px)',
              overflowY: 'auto'
            }}
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-lg font-semibold text-gray-900">
                {wordDetails.word.word}
              </h4>
              <button
                onClick={() => setWordDetails(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>

            {/* Word Stats */}
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="text-sm text-gray-600">Frequency</div>
                  <div className="text-lg font-semibold text-gray-900">
                    {formatNumber(wordDetails.word.frequency || 0)}
                  </div>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="text-sm text-gray-600">Sentiment</div>
                  <div 
                    className="text-lg font-semibold"
                    style={{ color: getSentimentColor(wordDetails.word.sentiment) }}
                  >
                    {wordDetails.word.sentiment || 'neutral'}
                  </div>
                </div>
              </div>

              {wordDetails.word.category && (
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="text-sm text-gray-600">Category</div>
                  <div className="text-lg font-semibold text-gray-900">
                    {wordDetails.word.category}
                  </div>
                </div>
              )}

              {/* Similar Words */}
              {highlightSimilar && (
                <div>
                  <div className="text-sm text-gray-600 mb-2">Similar Words</div>
                  <div className="flex flex-wrap gap-1">
                    {findSimilarWords(wordDetails.word.word).map(similar => (
                      <button
                        key={similar}
                        onClick={() => onWordSelect(similar)}
                        className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
                      >
                        {similar}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="pt-3 border-t border-gray-200">
                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      onFilterChange({
                        ...filters,
                        sentiment: wordDetails.word.sentiment || undefined
                      });
                    }}
                    className="flex-1 px-3 py-2 text-xs bg-primary-100 text-primary-700 rounded hover:bg-primary-200 transition-colors"
                  >
                    Filter by Sentiment
                  </button>
                  <button
                    onClick={() => {
                      setSearchQuery(wordDetails.word.word);
                    }}
                    className="flex-1 px-3 py-2 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                  >
                    Search Similar
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Status Bar */}
      <div className="flex items-center justify-between p-3 border-t bg-gray-50 text-sm text-gray-600">
        <div className="flex items-center gap-4">
          <span>
            {searchQuery ? `${filteredWords.length} of ${words.length}` : `${words.length}`} words
          </span>
          {selectedWord && (
            <>
              <span>•</span>
              <span>Selected: <strong>{selectedWord}</strong></span>
            </>
          )}
          {showClusters && (
            <>
              <span>•</span>
              <span>{clusters.length} clusters</span>
            </>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          <Info className="h-4 w-4" />
          <span>{interactionMode === 'hover' ? 'Hover' : 'Click'} to interact</span>
        </div>
      </div>
    </div>
  );
}
