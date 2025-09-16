'use client';

import React, { useEffect, useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { WordCloudData } from '@/lib/types';
import { 
  Palette, LayoutGrid, Shuffle, RotateCw, Sparkles, Download, Settings, 
  ChevronDown, ChevronUp, Info, Eye, EyeOff 
} from 'lucide-react';
import { cn } from '@/lib/utils';
import WordCloudExportPanel from './WordCloudExportPanel';

interface ModernWordCloudProps {
  datasetId: string;
  mode?: string;
  className?: string;
  height?: number;
  width?: number;
  onWordClick?: (word: string) => void;
  words?: WordCloudData[]; // Optional: if provided, skip API call
  theme?: 'default' | 'vibrant' | 'minimal' | 'dark' | 'pastel' | 'neon';
  layoutMode?: 'spiral' | 'random' | 'cluster' | 'force';
  animationSpeed?: 'slow' | 'normal' | 'fast';
  showControls?: boolean;
  showExport?: boolean;
}

interface PositionedWord extends WordCloudData {
  x: number;
  y: number;
  fontSize: number;
  color: string;
  rotation: number;
  opacity?: number;
  scale?: number;
}

interface WordDetail {
  word: string;
  frequency: number;
  sentiment: string;
  category?: string;
  x: number;
  y: number;
}

const COLOR_THEMES = {
  default: {
    positive: ['#3B82F6', '#1D4ED8', '#2563EB', '#1E40AF'],
    negative: ['#EF4444', '#DC2626', '#B91C1C', '#991B1B'],
    neutral: ['#6366F1', '#8B5CF6', '#06B6D4', '#10B981', '#F59E0B', '#EF4444', '#3B82F6', '#8B5CF6', '#14B8A6', '#F97316']
  },
  vibrant: {
    positive: ['#10B981', '#059669', '#047857', '#065F46'],
    negative: ['#F59E0B', '#D97706', '#B45309', '#92400E'],
    neutral: ['#8B5CF6', '#7C3AED', '#6D28D9', '#5B21B6', '#EC4899', '#DB2777', '#BE185D', '#9D174D', '#06B6D4', '#0891B2']
  },
  minimal: {
    positive: ['#374151', '#4B5563', '#6B7280', '#9CA3AF'],
    negative: ['#374151', '#4B5563', '#6B7280', '#9CA3AF'],
    neutral: ['#374151', '#4B5563', '#6B7280', '#9CA3AF', '#D1D5DB', '#E5E7EB', '#F3F4F6', '#F9FAFB']
  },
  dark: {
    positive: ['#34D399', '#10B981', '#059669', '#047857'],
    negative: ['#F87171', '#EF4444', '#DC2626', '#B91C1C'],
    neutral: ['#A78BFA', '#8B5CF6', '#7C3AED', '#6D28D9', '#F472B6', '#EC4899', '#60A5FA', '#3B82F6']
  },
  pastel: {
    positive: ['#A7F3D0', '#6EE7B7', '#34D399', '#10B981'],
    negative: ['#FED7D7', '#FCA5A5', '#F87171', '#EF4444'],
    neutral: ['#E0E7FF', '#C7D2FE', '#A5B4FC', '#818CF8', '#FECACA', '#FCA5A5', '#F87171', '#EF4444']
  },
  neon: {
    positive: ['#00FF88', '#00E5FF', '#FF6B9D', '#C77DFF'],
    negative: ['#FF073A', '#FF9500', '#FFD23F', '#06FFA5'],
    neutral: ['#7209B7', '#560BAD', '#480CA8', '#3A0CA3', '#3F37C9', '#4361EE', '#4895EF', '#4CC9F0']
  }
};

const ANIMATION_SPEEDS = {
  slow: { duration: 0.8, stagger: 0.1 },
  normal: { duration: 0.5, stagger: 0.05 },
  fast: { duration: 0.3, stagger: 0.02 }
};

export default function ModernWordCloud({
  datasetId,
  mode = 'all',
  className = '',
  height = 500,
  width = 800,
  onWordClick,
  words: propWords,
  theme = 'vibrant',
  layoutMode = 'spiral',
  animationSpeed = 'normal',
  showControls = true,
  showExport = true
}: ModernWordCloudProps) {
  const [words, setWords] = useState<PositionedWord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentTheme, setCurrentTheme] = useState<'default' | 'vibrant' | 'minimal' | 'dark' | 'pastel' | 'neon'>(theme);
  const [currentLayout, setCurrentLayout] = useState<'spiral' | 'random' | 'cluster' | 'force'>(layoutMode);
  const [currentAnimationSpeed, setCurrentAnimationSpeed] = useState<'slow' | 'normal' | 'fast'>(animationSpeed);
  const [showWordDetails, setShowWordDetails] = useState(true);
  const [wordDetail, setWordDetail] = useState<WordDetail | null>(null);
  const [hoveredWord, setHoveredWord] = useState<string | null>(null);
  const [showControlPanel, setShowControlPanel] = useState(false);
  const svgRef = useRef<SVGSVGElement>(null);

  // 🎨 Advanced color theming with multiple schemes
  const getWordColor = useCallback((word: WordCloudData, index: number): string => {
    const colors = COLOR_THEMES[currentTheme];
    
    if (word.sentiment === 'positive') {
      return colors.positive[index % colors.positive.length];
    } else if (word.sentiment === 'negative') {
      return colors.negative[index % colors.negative.length];
    } else {
      return colors.neutral[index % colors.neutral.length];
    }
  }, [currentTheme]);

  // Calculate font size based on frequency
  const getFontSize = (frequency: number, maxFreq: number, minSize = 14, maxSize = 48): number => {
    const normalized = frequency / maxFreq;
    return Math.max(minSize, maxSize * Math.pow(normalized, 0.7)); // Power scaling for better distribution
  };

  // Improved collision detection
  const checkCollision = (
    newWord: { x: number; y: number; width: number; height: number },
    existingWords: { x: number; y: number; width: number; height: number }[]
  ): boolean => {
    return existingWords.some(existing => {
      return !(
        newWord.x + newWord.width < existing.x ||
        newWord.x > existing.x + existing.width ||
        newWord.y + newWord.height < existing.y ||
        newWord.y > existing.y + existing.height
      );
    });
  };

  // 🎯 Enhanced collision detection
  const checkCollisionEnhanced = useCallback((
    newWord: { x: number; y: number; width: number; height: number },
    existingWords: { x: number; y: number; width: number; height: number }[],
    padding: number = 5
  ): boolean => {
    return existingWords.some(existing => {
      return !(
        newWord.x + newWord.width + padding < existing.x ||
        newWord.x > existing.x + existing.width + padding ||
        newWord.y + newWord.height + padding < existing.y ||
        newWord.y > existing.y + existing.height + padding
      );
    });
  }, []);

  // 🌀 Spiral layout algorithm
  const findSpiralPosition = useCallback((
    word: string,
    fontSize: number,
    centerX: number,
    centerY: number,
    existingWords: { x: number; y: number; width: number; height: number }[]
  ): { x: number; y: number } => {
    const wordWidth = word.length * fontSize * 0.6;
    const wordHeight = fontSize * 1.2;
    
    // Try center first
    let testX = centerX - wordWidth / 2;
    let testY = centerY - wordHeight / 2;
    
    if (!checkCollisionEnhanced({ x: testX, y: testY, width: wordWidth, height: wordHeight }, existingWords)) {
      return { x: testX, y: testY };
    }
    
    // Spiral outward
    let radius = 30;
    let angle = 0;
    const radiusIncrement = 15;
    const angleIncrement = 0.5;
    
    while (radius < Math.min(width, height) / 2) {
      testX = centerX + radius * Math.cos(angle) - wordWidth / 2;
      testY = centerY + radius * Math.sin(angle) - wordHeight / 2;
      
      if (testX >= 10 && testX + wordWidth <= width - 10 && 
          testY >= 10 && testY + wordHeight <= height - 10) {
        
        if (!checkCollisionEnhanced({ x: testX, y: testY, width: wordWidth, height: wordHeight }, existingWords)) {
          return { x: testX, y: testY };
        }
      }
      
      angle += angleIncrement;
      if (angle > 2 * Math.PI) {
        angle = 0;
        radius += radiusIncrement;
      }
    }
    
    return {
      x: Math.random() * (width - wordWidth - 20) + 10,
      y: Math.random() * (height - wordHeight - 20) + 10
    };
  }, [width, height, checkCollisionEnhanced]);

  // 🎲 Random layout with collision avoidance
  const findRandomPosition = useCallback((
    wordWidth: number,
    wordHeight: number,
    existingWords: { x: number; y: number; width: number; height: number }[]
  ): { x: number; y: number } => {
    const padding = 20;
    const maxAttempts = 100;
    
    for (let i = 0; i < maxAttempts; i++) {
      const x = padding + Math.random() * (width - wordWidth - 2 * padding);
      const y = padding + Math.random() * (height - wordHeight - 2 * padding);
      
      if (!checkCollisionEnhanced({ x, y, width: wordWidth, height: wordHeight }, existingWords)) {
        return { x, y };
      }
    }
    
    return {
      x: Math.random() * (width - wordWidth - 20) + 10,
      y: Math.random() * (height - wordHeight - 20) + 10
    };
  }, [width, height, checkCollisionEnhanced]);

  // 🌌 Cluster layout - groups words by sentiment/category
  const findClusterPosition = useCallback((
    word: WordCloudData,
    fontSize: number,
    centerX: number,
    centerY: number,
    existingWords: { x: number; y: number; width: number; height: number }[],
    index: number
  ): { x: number; y: number } => {
    const wordWidth = word.word.length * fontSize * 0.6;
    const wordHeight = fontSize * 1.2;
    
    // Define cluster centers based on sentiment
    let clusterX = centerX;
    let clusterY = centerY;
    
    if (word.sentiment === 'positive') {
      clusterX = centerX - width * 0.25;
      clusterY = centerY - height * 0.15;
    } else if (word.sentiment === 'negative') {
      clusterX = centerX + width * 0.25;
      clusterY = centerY - height * 0.15;
    }
    
    return findSpiralPosition(word.word, fontSize, clusterX, clusterY, existingWords);
  }, [width, height, findSpiralPosition]);

  // ⚚️ Force-directed layout simulation
  const findForcePosition = useCallback((
    word: WordCloudData,
    fontSize: number,
    centerX: number,
    centerY: number,
    index: number,
    totalWords: number
  ): { x: number; y: number } => {
    const angle = (index / totalWords) * 2 * Math.PI;
    const radius = 50 + (word.frequency || 1) * 5;
    
    const x = centerX + radius * Math.cos(angle) - (word.word.length * fontSize * 0.6) / 2;
    const y = centerY + radius * Math.sin(angle) - (fontSize * 1.2) / 2;
    
    return {
      x: Math.max(10, Math.min(x, width - word.word.length * fontSize * 0.6 - 10)),
      y: Math.max(10, Math.min(y, height - fontSize * 1.2 - 10))
    };
  }, [width, height]);

  // 🌀 Master positioning function
  const findPosition = useCallback((
    word: WordCloudData,
    fontSize: number,
    centerX: number,
    centerY: number,
    existingWords: { x: number; y: number; width: number; height: number }[],
    index: number,
    totalWords: number
  ): { x: number; y: number } => {
    const wordWidth = word.word.length * fontSize * 0.6;
    const wordHeight = fontSize * 1.2;
    
    switch (currentLayout) {
      case 'random':
        return findRandomPosition(wordWidth, wordHeight, existingWords);
      case 'cluster':
        return findClusterPosition(word, fontSize, centerX, centerY, existingWords, index);
      case 'force':
        return findForcePosition(word, fontSize, centerX, centerY, index, totalWords);
      case 'spiral':
      default:
        return findSpiralPosition(word.word, fontSize, centerX, centerY, existingWords);
    }
  }, [currentLayout, findSpiralPosition, findRandomPosition, findClusterPosition, findForcePosition]);

  // Fetch and process word cloud data
  const fetchWordCloudData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://ai-text-analysis-production.up.railway.app';
      const response = await fetch(`${API_BASE_URL}/api/wordcloud/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          dataset_id: datasetId,
          mode: mode,
          max_words: 100
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to generate word cloud: ${response.status}`);
      }

      const data = await response.json();
      console.log('Word cloud data:', data);

      // Handle different response formats
      let wordsArray: any[] = [];
      
      if (data.success && data.data && Array.isArray(data.data)) {
        wordsArray = data.data;
      } else if (data.success && data.words && Array.isArray(data.words)) {
        wordsArray = data.words;
      } else if (data.words && Array.isArray(data.words)) {
        wordsArray = data.words;
      } else if (Array.isArray(data)) {
        wordsArray = data;
      }

      // Convert API format to frontend format
      if (wordsArray.length > 0) {
        const convertedWords = wordsArray.map((w: any) => ({
          word: w.word || w.text,  // Handle both formats
          frequency: w.frequency || w.value || w.weight,  // Handle both formats
          sentiment: w.sentiment || 'neutral'
        }));
        wordsArray = convertedWords;
      }

      if (wordsArray.length > 0) {
        processWordPositions(wordsArray);
      } else {
        setWords([]);
      }
    } catch (err) {
      console.error('Error fetching word cloud:', err);
      setError(err instanceof Error ? err.message : 'Failed to load word cloud');
      setWords([]);
    } finally {
      setLoading(false);
    }
  };

  // 🌀 Enhanced word positioning with multiple layout algorithms
  const processWordPositions = useCallback((wordData: WordCloudData[]) => {
    const centerX = width / 2;
    const centerY = height / 2;
    const maxFreq = Math.max(...wordData.map(w => w.frequency));
    
    const positionedWords: PositionedWord[] = [];
    const occupiedAreas: { x: number; y: number; width: number; height: number }[] = [];
    
    // Sort by frequency for better placement
    const sortedWords = [...wordData].sort((a, b) => b.frequency - a.frequency);
    
    sortedWords.forEach((word, index) => {
      const fontSize = getFontSize(word.frequency, maxFreq);
      const color = getWordColor(word, index);
      const rotation = Math.random() > 0.8 ? (Math.random() - 0.5) * 30 : 0;
      
      const position = findPosition(
        word,
        fontSize,
        centerX,
        centerY,
        occupiedAreas,
        index,
        sortedWords.length
      );
      
      const wordWidth = word.word.length * fontSize * 0.6;
      const wordHeight = fontSize * 1.2;
      
      positionedWords.push({
        ...word,
        x: position.x,
        y: position.y,
        fontSize,
        color,
        rotation,
        opacity: 0.9,
        scale: 1
      });
      
      occupiedAreas.push({
        x: position.x,
        y: position.y,
        width: wordWidth,
        height: wordHeight
      });
    });
    
    setWords(positionedWords);
  }, [width, height, getFontSize, getWordColor, findPosition]);

  useEffect(() => {
    if (propWords && propWords.length > 0) {
      // Use provided words instead of fetching
      console.log('🎯 Using provided words:', propWords.length);
      setLoading(false);
      setError(null);
      processWordPositions(propWords);
    } else {
      // Fallback to API fetch
      fetchWordCloudData();
    }
  }, [datasetId, mode, propWords, currentLayout, currentTheme, processWordPositions]);

  if (loading) {
    return (
      <div className={`flex items-center justify-center ${className}`} style={{ height, width }}>
        <div className="flex flex-col items-center space-y-3">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="text-sm text-gray-600">Generating word cloud...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`flex items-center justify-center ${className}`} style={{ height, width }}>
        <div className="text-center">
          <p className="text-red-600 mb-2">Failed to load word cloud</p>
          <button
            onClick={fetchWordCloudData}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (words.length === 0) {
    return (
      <div className={`flex items-center justify-center ${className}`} style={{ height, width }}>
        <div className="text-center text-gray-500">
          <p className="mb-2">No words found for this analysis mode</p>
          <p className="text-sm">Try a different mode or check your data</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`relative overflow-hidden bg-gradient-to-br from-gray-50 to-white ${className}`} 
         style={{ height, width }}>
      
      {/* Enhanced Control Panel */}
      {showControls && (
        <div className="absolute top-4 left-4 flex gap-2 z-10">
          <button
            onClick={() => setShowControlPanel(!showControlPanel)}
            className="p-2 bg-white/90 backdrop-blur-sm rounded-lg shadow-sm border hover:bg-white transition-colors"
            title="Advanced Controls"
          >
            <Settings className="h-4 w-4 text-gray-600" />
          </button>
          
          {showExport && (
            <WordCloudExportPanel 
              words={words} 
              currentTheme={currentTheme}
              currentLayout={currentLayout}
              onExport={(options) => {
                console.log('Exporting with options:', options);
                // Export functionality handled by WordCloudExportPanel
              }}
            />
          )}
        </div>
      )}

      {/* Advanced Control Panel */}
      <AnimatePresence>
        {showControlPanel && (
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="absolute top-16 left-4 w-72 bg-white/95 backdrop-blur-sm rounded-lg shadow-lg border p-4 z-20"
          >
            <div className="space-y-4">
              {/* Theme Selection */}
              <div>
                <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                  <Palette className="h-4 w-4" />
                  Color Theme
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {(Object.keys(COLOR_THEMES) as Array<keyof typeof COLOR_THEMES>).map((themeKey) => (
                    <button
                      key={themeKey}
                      onClick={() => setCurrentTheme(themeKey)}
                      className={cn(
                        "px-3 py-2 text-xs rounded-lg border transition-all capitalize",
                        currentTheme === themeKey
                          ? "bg-primary-100 border-primary-500 text-primary-800"
                          : "bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100"
                      )}
                    >
                      {themeKey}
                    </button>
                  ))}
                </div>
              </div>

              {/* Layout Mode */}
              <div>
                <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                  <LayoutGrid className="h-4 w-4" />
                  Layout Algorithm
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { key: 'spiral', label: 'Spiral', icon: RotateCw },
                    { key: 'random', label: 'Random', icon: Shuffle },
                    { key: 'cluster', label: 'Cluster', icon: LayoutGrid },
                    { key: 'force', label: 'Force', icon: Sparkles }
                  ].map(({ key, label, icon: Icon }) => (
                    <button
                      key={key}
                      onClick={() => setCurrentLayout(key as any)}
                      className={cn(
                        "flex items-center gap-2 px-3 py-2 text-xs rounded-lg border transition-all",
                        currentLayout === key
                          ? "bg-primary-100 border-primary-500 text-primary-800"
                          : "bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100"
                      )}
                    >
                      <Icon className="h-3 w-3" />
                      {label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Animation Speed */}
              <div>
                <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                  <Sparkles className="h-4 w-4" />
                  Animation Speed
                </label>
                <div className="flex gap-2">
                  {['slow', 'normal', 'fast'].map((speed) => (
                    <button
                      key={speed}
                      onClick={() => setCurrentAnimationSpeed(speed as any)}
                      className={cn(
                        "px-3 py-2 text-xs rounded-lg border transition-all capitalize",
                        currentAnimationSpeed === speed
                          ? "bg-primary-100 border-primary-500 text-primary-800"
                          : "bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100"
                      )}
                    >
                      {speed}
                    </button>
                  ))}
                </div>
              </div>

              {/* Word Details Toggle */}
              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
                  {showWordDetails ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                  Word Details
                </label>
                <button
                  onClick={() => setShowWordDetails(!showWordDetails)}
                  className={cn(
                    "px-3 py-1 text-xs rounded-lg border transition-all",
                    showWordDetails
                      ? "bg-primary-100 border-primary-500 text-primary-800"
                      : "bg-gray-50 border-gray-200 text-gray-600"
                  )}
                >
                  {showWordDetails ? 'On' : 'Off'}
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Enhanced SVG Rendering */}
      <svg 
        ref={svgRef}
        width={width} 
        height={height}
        className="w-full h-full"
      >
        {words.map((word, index) => {
          const isHovered = hoveredWord === word.word;
          const animationSettings = ANIMATION_SPEEDS[currentAnimationSpeed];
          
          return (
            <motion.text
              key={`${word.word}-${index}-${currentLayout}-${currentTheme}`}
              x={word.x}
              y={word.y + word.fontSize * 0.75}
              fontSize={word.fontSize}
              fill={word.color}
              fontFamily="Inter, -apple-system, BlinkMacSystemFont, sans-serif"
              fontWeight={word.fontSize > 30 ? 'bold' : word.fontSize > 20 ? 'semibold' : 'medium'}
              transform={`rotate(${word.rotation} ${word.x + word.word.length * word.fontSize * 0.3} ${word.y + word.fontSize * 0.5})`}
              style={{ 
                cursor: onWordClick ? 'pointer' : 'default',
                userSelect: 'none'
              }}
              onClick={() => {
                onWordClick?.(word.word);
                if (showWordDetails) {
                  setWordDetail({
                    word: word.word,
                    frequency: word.frequency || 0,
                    sentiment: word.sentiment || 'neutral',
                    category: word.category,
                    x: word.x,
                    y: word.y
                  });
                }
              }}
              onMouseEnter={() => setHoveredWord(word.word)}
              onMouseLeave={() => setHoveredWord(null)}
              initial={{ 
                opacity: 0, 
                scale: 0.3,
                y: word.y + 50
              }}
              animate={{ 
                opacity: word.opacity || 1, 
                scale: isHovered ? 1.1 : (word.scale || 1),
                y: word.y + word.fontSize * 0.75
              }}
              transition={{ 
                duration: animationSettings.duration, 
                delay: index * animationSettings.stagger,
                type: 'spring',
                stiffness: 100
              }}
              whileHover={onWordClick ? { 
                scale: 1.15, 
                fill: currentTheme === 'dark' ? '#FFFFFF' : '#1F2937',
                transition: { duration: 0.2 }
              } : undefined}
              className="hover:drop-shadow-lg transition-all"
            >
              {word.word}
            </motion.text>
          );
        })}
      </svg>

      {/* Enhanced Word Detail Panel */}
      <AnimatePresence>
        {wordDetail && showWordDetails && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="absolute bottom-4 right-4 bg-white/95 backdrop-blur-sm rounded-lg shadow-lg border p-4 max-w-xs"
          >
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold text-gray-900">"{wordDetail.word}"</h3>
              <button
                onClick={() => setWordDetail(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>
            <div className="space-y-1 text-sm text-gray-600">
              <div>Frequency: <span className="font-medium">{wordDetail.frequency}</span></div>
              <div>Sentiment: <span className="font-medium capitalize">{wordDetail.sentiment}</span></div>
              {wordDetail.category && (
                <div>Category: <span className="font-medium">{wordDetail.category}</span></div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Enhanced Mode and Status Indicator */}
      <div className="absolute top-4 right-4 bg-white/80 backdrop-blur-sm rounded-lg px-3 py-1 text-sm text-gray-700 border">
        <div className="flex items-center gap-2">
          <span>
            {mode === 'all' ? 'All Words' : 
             mode === 'verbs' ? 'Action Words' :
             mode === 'nouns' ? 'Nouns' :
             mode === 'adjectives' ? 'Adjectives' :
             mode === 'emotions' ? 'Emotions' : 
             mode.charAt(0).toUpperCase() + mode.slice(1)}
          </span>
          <span className="text-xs text-gray-500">
            | {currentTheme} | {currentLayout}
          </span>
        </div>
      </div>
    </div>
  );
}
