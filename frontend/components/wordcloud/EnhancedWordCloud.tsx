'use client';

import React, { useEffect, useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Palette, 
  Zap, 
  RotateCw, 
  Maximize2, 
  Download, 
  Eye,
  MousePointer,
  Sparkles,
  TrendingUp
} from 'lucide-react';
import { WordCloudData } from '@/lib/types';
import { cn } from '@/lib/utils';
import WordCloudExportPanel from './WordCloudExportPanel';

interface EnhancedWordCloudProps {
  datasetId: string;
  mode?: string;
  className?: string;
  height?: number;
  width?: number;
  onWordClick?: (word: string, data: WordCloudData) => void;
  words?: WordCloudData[];
  theme?: 'default' | 'vibrant' | 'minimal' | 'dark' | 'pastel' | 'neon';
  layoutMode?: 'spiral' | 'random' | 'cluster' | 'force';
  animationSpeed?: 'slow' | 'normal' | 'fast';
  showWordDetails?: boolean;
}

interface PositionedWord extends WordCloudData {
  x: number;
  y: number;
  fontSize: number;
  color: string;
  rotation: number;
  opacity: number;
  scale: number;
}

interface WordDetail {
  word: string;
  frequency: number;
  sentiment: string;
  category?: string;
  x: number;
  y: number;
}

// 🎨 Enhanced Color Themes
const COLOR_THEMES = {
  default: {
    name: 'Default',
    positive: ['#3B82F6', '#1D4ED8', '#2563EB', '#1E40AF'],
    negative: ['#EF4444', '#DC2626', '#B91C1C', '#991B1B'],
    neutral: ['#6366F1', '#8B5CF6', '#06B6D4', '#10B981', '#F59E0B', '#EF4444', '#3B82F6', '#14B8A6'],
    background: '#FFFFFF'
  },
  vibrant: {
    name: 'Vibrant',
    positive: ['#00D9FF', '#0099CC', '#007ACC', '#0066AA'],
    negative: ['#FF6B6B', '#FF5252', '#FF1744', '#D50000'],
    neutral: ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF', '#5F27CD'],
    background: '#F8F9FA'
  },
  minimal: {
    name: 'Minimal',
    positive: ['#2C3E50', '#34495E', '#555555', '#666666'],
    negative: ['#7F8C8D', '#95A5A6', '#BDC3C7', '#D5DBDB'],
    neutral: ['#2C3E50', '#34495E', '#555555', '#666666', '#7F8C8D', '#95A5A6'],
    background: '#FFFFFF'
  },
  dark: {
    name: 'Dark Mode',
    positive: ['#00D4AA', '#00BFA5', '#009688', '#00796B'],
    negative: ['#FF5722', '#E64A19', '#D84315', '#BF360C'],
    neutral: ['#00D4AA', '#64FFDA', '#40C4FF', '#448AFF', '#7C4DFF', '#E040FB', '#FF4081', '#FF5722'],
    background: '#121212'
  },
  pastel: {
    name: 'Pastel',
    positive: ['#A8E6CF', '#7FCDCD', '#6FB3D2', '#A8C8EC'],
    negative: ['#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9'],
    neutral: ['#A8E6CF', '#7FCDCD', '#6FB3D2', '#A8C8EC', '#C7CEEA', '#FFB3BA', '#FFDFBA', '#BAFFC9'],
    background: '#FEFEFE'
  },
  neon: {
    name: 'Neon',
    positive: ['#00FFFF', '#00FF00', '#FFFF00', '#FF00FF'],
    negative: ['#FF0080', '#FF0040', '#FF0000', '#FF4000'],
    neutral: ['#00FFFF', '#00FF00', '#FFFF00', '#FF00FF', '#FF0080', '#8000FF', '#0080FF', '#40FF00'],
    background: '#000000'
  }
};

// 🎪 Animation Presets
const ANIMATION_SPEEDS = {
  slow: { duration: 1.5, stagger: 0.1 },
  normal: { duration: 1.0, stagger: 0.05 },
  fast: { duration: 0.6, stagger: 0.02 }
};

export default function EnhancedWordCloud({
  datasetId,
  mode = 'all',
  className = '',
  height = 500,
  width = 800,
  onWordClick,
  words: propWords,
  theme = 'default',
  layoutMode = 'spiral',
  animationSpeed = 'normal',
  showWordDetails = true
}: EnhancedWordCloudProps) {
  const [words, setWords] = useState<PositionedWord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedWord, setSelectedWord] = useState<string | null>(null);
  const [hoveredWord, setHoveredWord] = useState<string | null>(null);
  const [wordDetail, setWordDetail] = useState<WordDetail | null>(null);
  const [isAnimating, setIsAnimating] = useState(false);
  const [currentTheme, setCurrentTheme] = useState(theme);
  const [currentLayout, setCurrentLayout] = useState(layoutMode);
  
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // 🎨 Enhanced color selection with themes
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

  // 📏 Dynamic font sizing with better distribution
  const getFontSize = useCallback((frequency: number, maxFreq: number): number => {
    const minSize = 12;
    const maxSize = 64;
    const normalized = frequency / maxFreq;
    
    // Use power curve for better size distribution
    return Math.max(minSize, maxSize * Math.pow(normalized, 0.6));
  }, []);

  // 🎯 Advanced collision detection
  const checkCollision = useCallback((
    newWord: { x: number; y: number; width: number; height: number },
    existingWords: { x: number; y: number; width: number; height: number }[],
    padding = 4
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

  // 🌀 Multiple layout algorithms
  const calculateWordPositions = useCallback((wordData: WordCloudData[]): PositionedWord[] => {
    if (!wordData.length) return [];

    const centerX = width / 2;
    const centerY = height / 2;
    const maxFreq = Math.max(...wordData.map(w => w.frequency || 1));
    const existingPositions: { x: number; y: number; width: number; height: number }[] = [];

    return wordData.map((word, index) => {
      const fontSize = getFontSize(word.frequency || 1, maxFreq);
      const wordWidth = word.word.length * fontSize * 0.6;
      const wordHeight = fontSize * 1.2;
      
      let position = { x: 0, y: 0 };
      
      switch (currentLayout) {
        case 'spiral':
          position = findSpiralPosition(word.word, fontSize, centerX, centerY, existingPositions);
          break;
        case 'random':
          position = findRandomPosition(wordWidth, wordHeight, existingPositions);
          break;
        case 'cluster':
          position = findClusterPosition(word, fontSize, centerX, centerY, existingPositions, index);
          break;
        case 'force':
          position = findForcePosition(word, fontSize, centerX, centerY, index, wordData.length);
          break;
        default:
          position = findSpiralPosition(word.word, fontSize, centerX, centerY, existingPositions);
      }

      existingPositions.push({
        x: position.x,
        y: position.y,
        width: wordWidth,
        height: wordHeight
      });

      return {
        ...word,
        x: position.x,
        y: position.y,
        fontSize,
        color: getWordColor(word, index),
        rotation: Math.random() * 60 - 30, // Random rotation between -30 and 30 degrees
        opacity: 0.9,
        scale: 1
      };
    });
  }, [width, height, currentLayout, getFontSize, getWordColor, checkCollision]);

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
    
    if (!checkCollision({ x: testX, y: testY, width: wordWidth, height: wordHeight }, existingWords)) {
      return { x: testX, y: testY };
    }

    // Spiral outward
    let radius = 20;
    let angle = 0;
    const spiralIncrement = 8;
    const angleIncrement = 0.5;

    for (let i = 0; i < 500; i++) {
      testX = centerX + radius * Math.cos(angle) - wordWidth / 2;
      testY = centerY + radius * Math.sin(angle) - wordHeight / 2;
      
      // Keep within bounds
      testX = Math.max(0, Math.min(width - wordWidth, testX));
      testY = Math.max(0, Math.min(height - wordHeight, testY));
      
      if (!checkCollision({ x: testX, y: testY, width: wordWidth, height: wordHeight }, existingWords)) {
        return { x: testX, y: testY };
      }
      
      angle += angleIncrement;
      radius += spiralIncrement / (2 * Math.PI);
    }
    
    // Fallback to random position
    return {
      x: Math.random() * (width - wordWidth),
      y: Math.random() * (height - wordHeight)
    };
  }, [width, height, checkCollision]);

  // 🎲 Random layout with collision avoidance
  const findRandomPosition = useCallback((
    wordWidth: number,
    wordHeight: number,
    existingWords: { x: number; y: number; width: number; height: number }[]
  ): { x: number; y: number } => {
    for (let i = 0; i < 100; i++) {
      const testX = Math.random() * (width - wordWidth);
      const testY = Math.random() * (height - wordHeight);
      
      if (!checkCollision({ x: testX, y: testY, width: wordWidth, height: wordHeight }, existingWords)) {
        return { x: testX, y: testY };
      }
    }
    
    return {
      x: Math.random() * (width - wordWidth),
      y: Math.random() * (height - wordHeight)
    };
  }, [width, height, checkCollision]);

  // 🎯 Cluster layout by sentiment/category
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
      clusterY = centerY - height * 0.2;
    } else if (word.sentiment === 'negative') {
      clusterX = centerX + width * 0.25;
      clusterY = centerY - height * 0.2;
    } else {
      clusterY = centerY + height * 0.2;
    }
    
    // Find position near cluster center
    const radius = 50 + (index % 3) * 30;
    const angle = (index * 2.5) % (2 * Math.PI);
    
    let testX = clusterX + radius * Math.cos(angle) - wordWidth / 2;
    let testY = clusterY + radius * Math.sin(angle) - wordHeight / 2;
    
    // Keep within bounds
    testX = Math.max(0, Math.min(width - wordWidth, testX));
    testY = Math.max(0, Math.min(height - wordHeight, testY));
    
    if (!checkCollision({ x: testX, y: testY, width: wordWidth, height: wordHeight }, existingWords)) {
      return { x: testX, y: testY };
    }
    
    // Fallback to spiral from cluster center
    return findSpiralPosition(word.word, fontSize, clusterX, clusterY, existingWords);
  }, [width, height, findSpiralPosition, checkCollision]);

  // ⚡ Force-directed layout
  const findForcePosition = useCallback((
    word: WordCloudData,
    fontSize: number,
    centerX: number,
    centerY: number,
    index: number,
    totalWords: number
  ): { x: number; y: number } => {
    const wordWidth = word.word.length * fontSize * 0.6;
    const wordHeight = fontSize * 1.2;
    
    // Distribute around a circle initially
    const angle = (index / totalWords) * 2 * Math.PI;
    const radius = Math.min(width, height) * 0.3;
    
    const testX = centerX + radius * Math.cos(angle) - wordWidth / 2;
    const testY = centerY + radius * Math.sin(angle) - wordHeight / 2;
    
    return {
      x: Math.max(0, Math.min(width - wordWidth, testX)),
      y: Math.max(0, Math.min(height - wordHeight, testY))
    };
  }, [width, height]);

  // 🔄 Regenerate word cloud with new layout/theme
  const regenerateCloud = useCallback(() => {
    if (propWords && propWords.length > 0) {
      setIsAnimating(true);
      const positioned = calculateWordPositions(propWords);
      setWords(positioned);
      setTimeout(() => setIsAnimating(false), ANIMATION_SPEEDS[animationSpeed].duration * 1000);
    }
  }, [propWords, calculateWordPositions, animationSpeed]);

  // Initialize and regenerate on changes
  useEffect(() => {
    regenerateCloud();
  }, [regenerateCloud, currentTheme, currentLayout]);

  // 🎯 Handle word interactions
  const handleWordClick = useCallback((word: PositionedWord) => {
    setSelectedWord(selectedWord === word.word ? null : word.word);
    
    if (showWordDetails) {
      setWordDetail({
        word: word.word,
        frequency: word.frequency || 0,
        sentiment: word.sentiment || 'neutral',
        category: word.category || undefined,
        x: word.x + word.fontSize * 0.5,
        y: word.y - 10
      });
    }
    
    if (onWordClick) {
      onWordClick(word.word, word);
    }
  }, [selectedWord, showWordDetails, onWordClick]);

  const handleWordHover = useCallback((word: string | null) => {
    setHoveredWord(word);
  }, []);

  if (loading && (!propWords || propWords.length === 0)) {
    return (
      <div className={cn("flex items-center justify-center bg-gray-50 rounded-lg", className)} style={{ height, width }}>
        <div className="text-center">
          <div className="animate-spin h-8 w-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-2"></div>
          <p className="text-gray-600">Generating word cloud...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={cn("flex items-center justify-center bg-red-50 rounded-lg border border-red-200", className)} style={{ height, width }}>
        <div className="text-center text-red-800">
          <p className="font-medium">Failed to generate word cloud</p>
          <p className="text-sm mt-1">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={cn("relative rounded-lg overflow-hidden", className)} ref={containerRef}>
      {/* 🎛️ Control Panel */}
      <div className="absolute top-4 right-4 z-10 flex gap-2">
        {/* Theme Selector */}
        <div className="relative group">
          <button className="p-2 bg-white/90 backdrop-blur-sm rounded-lg shadow-sm border hover:bg-white transition-colors">
            <Palette className="h-4 w-4 text-gray-600" />
          </button>
          <div className="absolute right-0 mt-1 bg-white rounded-lg shadow-lg border p-2 min-w-[120px] opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none group-hover:pointer-events-auto">
            {Object.entries(COLOR_THEMES).map(([key, themeData]) => (
              <button
                key={key}
                onClick={() => setCurrentTheme(key as any)}
                className={cn(
                  "w-full text-left px-2 py-1 text-sm rounded hover:bg-gray-100",
                  currentTheme === key && "bg-blue-100 text-blue-700"
                )}
              >
                {themeData.name}
              </button>
            ))}
          </div>
        </div>

        {/* Layout Selector */}
        <div className="relative group">
          <button className="p-2 bg-white/90 backdrop-blur-sm rounded-lg shadow-sm border hover:bg-white transition-colors">
            <RotateCw className="h-4 w-4 text-gray-600" />
          </button>
          <div className="absolute right-0 mt-1 bg-white rounded-lg shadow-lg border p-2 min-w-[100px] opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none group-hover:pointer-events-auto">
            {(['spiral', 'random', 'cluster', 'force'] as const).map((layout) => (
              <button
                key={layout}
                onClick={() => setCurrentLayout(layout)}
                className={cn(
                  "w-full text-left px-2 py-1 text-sm rounded hover:bg-gray-100 capitalize",
                  currentLayout === layout && "bg-blue-100 text-blue-700"
                )}
              >
                {layout}
              </button>
            ))}
          </div>
        </div>

        {/* Regenerate Button */}
        <button
          onClick={regenerateCloud}
          className="p-2 bg-white/90 backdrop-blur-sm rounded-lg shadow-sm border hover:bg-white transition-colors"
          title="Regenerate layout"
        >
          <Sparkles className="h-4 w-4 text-gray-600" />
        </button>

        {/* Export Panel */}
        <WordCloudExportPanel
          words={words}
          currentTheme={currentTheme}
          currentLayout={currentLayout}
          onExport={(options) => {
            console.log('Exporting with options:', options);
            // TODO: Implement actual export functionality
          }}
        />
      </div>

      {/* 🎨 Word Cloud SVG */}
      <svg
        ref={svgRef}
        width={width}
        height={height}
        className="cursor-pointer"
        style={{ background: COLOR_THEMES[currentTheme].background }}
      >
        <defs>
          {/* Gradient definitions for enhanced styling */}
          <linearGradient id="wordGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="currentColor" stopOpacity="0.8" />
            <stop offset="100%" stopColor="currentColor" stopOpacity="1" />
          </linearGradient>
          
          {/* Drop shadow filter */}
          <filter id="dropShadow" x="-50%" y="-50%" width="200%" height="200%">
            <feDropShadow dx="1" dy="1" stdDeviation="1" floodOpacity="0.3" />
          </filter>
        </defs>

        <AnimatePresence>
          {words.map((word, index) => {
            const isSelected = selectedWord === word.word;
            const isHovered = hoveredWord === word.word;
            const animationDelay = index * ANIMATION_SPEEDS[animationSpeed].stagger;

            return (
              <motion.text
                key={`${word.word}-${index}`}
                x={word.x}
                y={word.y + word.fontSize * 0.75}
                fontSize={word.fontSize}
                fill={word.color}
                fontWeight={isSelected ? 'bold' : word.frequency && word.frequency > 10 ? '600' : '400'}
                textAnchor="start"
                dominantBaseline="alphabetic"
                className="cursor-pointer select-none"
                transform={`rotate(${word.rotation} ${word.x + word.word.length * word.fontSize * 0.3} ${word.y + word.fontSize * 0.5})`}
                initial={{ 
                  opacity: 0, 
                  scale: 0.3,
                  y: word.y + 50
                }}
                animate={{ 
                  opacity: isHovered ? 1 : word.opacity,
                  scale: isSelected ? 1.2 : isHovered ? 1.1 : word.scale,
                  y: word.y + word.fontSize * 0.75
                }}
                exit={{ 
                  opacity: 0, 
                  scale: 0.3 
                }}
                transition={{
                  duration: ANIMATION_SPEEDS[animationSpeed].duration,
                  delay: animationDelay,
                  type: "spring",
                  stiffness: 100,
                  damping: 15
                }}
                whileHover={{
                  scale: 1.1,
                  transition: { duration: 0.2 }
                }}
                onClick={() => handleWordClick(word)}
                onMouseEnter={() => handleWordHover(word.word)}
                onMouseLeave={() => handleWordHover(null)}
                filter={isSelected || isHovered ? "url(#dropShadow)" : undefined}
              >
                {word.word}
              </motion.text>
            );
          })}
        </AnimatePresence>
      </svg>

      {/* 📋 Word Details Popup */}
      <AnimatePresence>
        {wordDetail && showWordDetails && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 10 }}
            className="absolute z-20 bg-white rounded-lg shadow-lg border p-3 pointer-events-none"
            style={{
              left: Math.min(wordDetail.x, width - 200),
              top: Math.max(wordDetail.y, 10),
              maxWidth: 200
            }}
          >
            <div className="space-y-1">
              <h4 className="font-semibold text-gray-900">{wordDetail.word}</h4>
              <div className="text-xs space-y-1">
                <div className="flex justify-between">
                  <span className="text-gray-500">Frequency:</span>
                  <span className="font-medium">{wordDetail.frequency}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Sentiment:</span>
                  <span className={cn(
                    "font-medium capitalize",
                    wordDetail.sentiment === 'positive' && "text-green-600",
                    wordDetail.sentiment === 'negative' && "text-red-600",
                    wordDetail.sentiment === 'neutral' && "text-gray-600"
                  )}>
                    {wordDetail.sentiment}
                  </span>
                </div>
                {wordDetail.category && (
                  <div className="flex justify-between">
                    <span className="text-gray-500">Category:</span>
                    <span className="font-medium">{wordDetail.category}</span>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 📊 Quick Stats */}
      <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-sm rounded-lg px-3 py-2 shadow-sm border">
        <div className="text-xs text-gray-600">
          <span className="font-medium">{words.length}</span> words • 
          <span className="font-medium"> {currentLayout}</span> layout • 
          <span className="font-medium"> {COLOR_THEMES[currentTheme].name}</span> theme
        </div>
      </div>
    </div>
  );
}
