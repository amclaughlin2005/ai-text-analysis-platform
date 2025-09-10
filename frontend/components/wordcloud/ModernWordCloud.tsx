'use client';

import React, { useEffect, useState, useRef } from 'react';
import { motion } from 'framer-motion';

interface WordData {
  word: string;
  frequency: number;
  sentiment?: 'positive' | 'negative' | 'neutral';
  size?: number;
}

interface ModernWordCloudProps {
  datasetId: string;
  mode?: string;
  className?: string;
  height?: number;
  width?: number;
  onWordClick?: (word: string) => void;
}

interface PositionedWord extends WordData {
  x: number;
  y: number;
  fontSize: number;
  color: string;
  rotation: number;
}

export default function ModernWordCloud({
  datasetId,
  mode = 'all',
  className = '',
  height = 500,
  width = 800,
  onWordClick
}: ModernWordCloudProps) {
  const [words, setWords] = useState<PositionedWord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  // Color schemes for different word types/sentiments
  const getWordColor = (word: WordData, index: number): string => {
    if (word.sentiment === 'positive') {
      return ['#3B82F6', '#1D4ED8', '#2563EB', '#1E40AF'][index % 4]; // Blues
    } else if (word.sentiment === 'negative') {
      return ['#EF4444', '#DC2626', '#B91C1C', '#991B1B'][index % 4]; // Reds
    } else {
      // Neutral words - varied colors like your example
      const colors = [
        '#6366F1', // Indigo
        '#8B5CF6', // Purple  
        '#06B6D4', // Cyan
        '#10B981', // Emerald
        '#F59E0B', // Amber
        '#EF4444', // Red
        '#3B82F6', // Blue
        '#8B5CF6', // Purple
        '#14B8A6', // Teal
        '#F97316'  // Orange
      ];
      return colors[index % colors.length];
    }
  };

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
          max_words: 50
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
  const processWordPositions = (wordData: WordData[]) => {
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
    fetchWordCloudData();
  }, [datasetId, mode]);

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
      
      {/* Mode indicator */}
      <div className="absolute top-4 right-4 bg-white/80 backdrop-blur-sm rounded-lg px-3 py-1 text-sm text-gray-700 border">
        {mode === 'all' ? 'All Words' : 
         mode === 'verbs' ? 'Action Words' :
         mode === 'nouns' ? 'Nouns' :
         mode === 'adjectives' ? 'Adjectives' :
         mode === 'emotions' ? 'Emotions' : 
         mode.charAt(0).toUpperCase() + mode.slice(1)}
      </div>
    </div>
  );
}
