'use client';

import React, { useEffect, useState, useRef, useCallback } from 'react';
import { motion } from 'framer-motion';
import { WordCloudData } from '@/lib/types';
import { Palette } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ModernWordCloudProps {
  datasetId: string;
  mode?: string;
  className?: string;
  height?: number;
  width?: number;
  onWordClick?: (word: string) => void;
  words?: WordCloudData[]; // Optional: if provided, skip API call
  theme?: 'vibrant' | 'light' | 'dark' | 'minimal' | 'ocean' | 'sunset';
  showThemeSelector?: boolean;
}

interface PositionedWord extends WordCloudData {
  x: number;
  y: number;
  fontSize: number;
  color: string;
  rotation: number;
}

// Theme color definitions
const THEMES = {
  vibrant: {
    name: 'Vibrant',
    background: 'from-blue-50 via-purple-50 to-pink-50',
    positive: ['#10B981', '#059669', '#047857', '#065F46'],
    negative: ['#F59E0B', '#D97706', '#B45309', '#92400E'],
    neutral: ['#8B5CF6', '#7C3AED', '#6D28D9', '#5B21B6', '#EC4899', '#DB2777', '#BE185D', '#9D174D', '#06B6D4', '#0891B2']
  },
  light: {
    name: 'Light',
    background: 'from-gray-50 to-white',
    positive: ['#3B82F6', '#1D4ED8', '#2563EB', '#1E40AF'],
    negative: ['#EF4444', '#DC2626', '#B91C1C', '#991B1B'],
    neutral: ['#6366F1', '#8B5CF6', '#06B6D4', '#10B981', '#F59E0B', '#EF4444', '#3B82F6', '#8B5CF6', '#14B8A6', '#F97316']
  },
  dark: {
    name: 'Dark',
    background: 'from-gray-900 via-blue-900 to-purple-900',
    positive: ['#34D399', '#10B981', '#059669', '#047857'],
    negative: ['#F87171', '#EF4444', '#DC2626', '#B91C1C'],
    neutral: ['#A78BFA', '#8B5CF6', '#7C3AED', '#6D28D9', '#F472B6', '#EC4899', '#60A5FA', '#3B82F6']
  },
  minimal: {
    name: 'Minimal',
    background: 'from-gray-50 to-gray-100',
    positive: ['#374151', '#4B5563', '#6B7280', '#9CA3AF'],
    negative: ['#374151', '#4B5563', '#6B7280', '#9CA3AF'],
    neutral: ['#374151', '#4B5563', '#6B7280', '#9CA3AF', '#6B7280', '#4B5563', '#374151', '#9CA3AF']
  },
  ocean: {
    name: 'Ocean',
    background: 'from-blue-50 via-cyan-50 to-teal-50',
    positive: ['#0891B2', '#0E7490', '#155E75', '#164E63'],
    negative: ['#0369A1', '#075985', '#0C4A6E', '#082F49'],
    neutral: ['#06B6D4', '#0891B2', '#0E7490', '#155E75', '#14B8A6', '#0D9488', '#0F766E', '#115E59']
  },
  sunset: {
    name: 'Sunset',
    background: 'from-orange-50 via-red-50 to-pink-50',
    positive: ['#F97316', '#EA580C', '#DC2626', '#B91C1C'],
    negative: ['#EF4444', '#DC2626', '#B91C1C', '#991B1B'],
    neutral: ['#F59E0B', '#D97706', '#B45309', '#92400E', '#EC4899', '#DB2777', '#BE185D', '#9D174D']
  }
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
  showThemeSelector = true
}: ModernWordCloudProps) {
  const [words, setWords] = useState<PositionedWord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentTheme, setCurrentTheme] = useState<'vibrant' | 'light' | 'dark' | 'minimal' | 'ocean' | 'sunset'>(theme);
  const [showThemePanel, setShowThemePanel] = useState(false);
  const svgRef = useRef<SVGSVGElement>(null);

  // Theme-aware color schemes for different word types/sentiments
  const getWordColor = useCallback((word: WordCloudData, index: number): string => {
    const themeColors = THEMES[currentTheme];
    
    if (word.sentiment === 'positive') {
      return themeColors.positive[index % themeColors.positive.length];
    } else if (word.sentiment === 'negative') {
      return themeColors.negative[index % themeColors.negative.length];
    } else {
      return themeColors.neutral[index % themeColors.neutral.length];
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

  // Spiral positioning algorithm
  const findPosition = (
    word: string,
    fontSize: number,
    centerX: number,
    centerY: number,
    existingWords: { x: number; y: number; width: number; height: number }[]
  ): { x: number; y: number } => {
    const wordWidth = word.length * fontSize * 0.6; // Approximate width
    const wordHeight = fontSize * 1.2; // Approximate height with line height
    
    // Try center first
    let testX = centerX - wordWidth / 2;
    let testY = centerY - wordHeight / 2;
    
    if (!checkCollision({ x: testX, y: testY, width: wordWidth, height: wordHeight }, existingWords)) {
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
      
      // Check bounds
      if (testX >= 10 && testX + wordWidth <= width - 10 && 
          testY >= 10 && testY + wordHeight <= height - 10) {
        
        if (!checkCollision({ x: testX, y: testY, width: wordWidth, height: wordHeight }, existingWords)) {
          return { x: testX, y: testY };
        }
      }
      
      angle += angleIncrement;
      if (angle > 2 * Math.PI) {
        angle = 0;
        radius += radiusIncrement;
      }
    }
    
    // Fallback to random position
    return {
      x: Math.random() * (width - wordWidth - 20) + 10,
      y: Math.random() * (height - wordHeight - 20) + 10
    };
  };

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

  // Process words and calculate positions
  const processWordPositions = (wordData: WordCloudData[]) => {
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
      const rotation = Math.random() > 0.8 ? (Math.random() - 0.5) * 30 : 0; // 20% chance of slight rotation
      
      const position = findPosition(
        word.word,
        fontSize,
        centerX,
        centerY,
        occupiedAreas
      );
      
      const wordWidth = word.word.length * fontSize * 0.6;
      const wordHeight = fontSize * 1.2;
      
      positionedWords.push({
        ...word,
        x: position.x,
        y: position.y,
        fontSize,
        color,
        rotation
      });
      
      occupiedAreas.push({
        x: position.x,
        y: position.y,
        width: wordWidth,
        height: wordHeight
      });
    });
    
    setWords(positionedWords);
  };

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
  }, [datasetId, mode, propWords, currentTheme]);

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
    <div className={`relative overflow-hidden bg-gradient-to-br ${THEMES[currentTheme].background} ${className}`} 
         style={{ height, width }}>
      
      {/* Theme Selector */}
      {showThemeSelector && (
        <div className="absolute top-4 left-4 z-30">
          <button
            onClick={() => setShowThemePanel(!showThemePanel)}
            className="flex items-center gap-2 px-3 py-2 bg-white/95 backdrop-blur-sm rounded-lg shadow-md border hover:bg-white hover:shadow-lg transition-all"
            title="Change Theme"
          >
            <Palette className="h-4 w-4 text-primary-600" />
            <span className="text-xs font-medium text-gray-700">Theme</span>
          </button>
          
          {showThemePanel && (
            <div className="absolute top-12 left-0 w-64 bg-white/98 backdrop-blur-sm rounded-lg shadow-xl border p-4 z-40">
              <h3 className="text-sm font-medium text-gray-900 mb-3">Color Theme</h3>
              <div className="grid grid-cols-2 gap-2">
                {(Object.keys(THEMES) as Array<keyof typeof THEMES>).map((themeKey) => (
                  <button
                    key={themeKey}
                    onClick={() => {
                      setCurrentTheme(themeKey);
                      setShowThemePanel(false);
                    }}
                    className={cn(
                      "flex items-center gap-2 px-3 py-2 text-xs rounded-lg border transition-all",
                      currentTheme === themeKey
                        ? "bg-primary-100 border-primary-500 text-primary-800"
                        : "bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100"
                    )}
                  >
                    <div 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: THEMES[themeKey].neutral[0] }}
                    />
                    {THEMES[themeKey].name}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <svg 
        ref={svgRef}
        width={width} 
        height={height}
        className="w-full h-full"
      >
        {words.map((word, index) => (
          <motion.text
            key={`${word.word}-${index}`}
            x={word.x}
            y={word.y + word.fontSize * 0.75} // Baseline adjustment
            fontSize={word.fontSize}
            fill={word.color}
            fontFamily="Inter, -apple-system, BlinkMacSystemFont, sans-serif"
            fontWeight={word.fontSize > 30 ? 'bold' : word.fontSize > 20 ? 'semibold' : 'medium'}
            transform={`rotate(${word.rotation} ${word.x + word.word.length * word.fontSize * 0.3} ${word.y + word.fontSize * 0.5})`}
            style={{ 
              cursor: onWordClick ? 'pointer' : 'default',
              userSelect: 'none'
            }}
            onClick={() => onWordClick?.(word.word)}
            initial={{ opacity: 0, scale: 0.3 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ 
              duration: 0.5, 
              delay: index * 0.05,
              type: 'spring',
              stiffness: 100
            }}
            whileHover={onWordClick ? { 
              scale: 1.1, 
              fill: '#1F2937',
              transition: { duration: 0.2 }
            } : undefined}
            className="hover:drop-shadow-sm"
          >
            {word.word}
          </motion.text>
        ))}
      </svg>
      
      {/* Mode and Theme indicator */}
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
            | {THEMES[currentTheme].name}
          </span>
        </div>
      </div>
    </div>
  );
}
