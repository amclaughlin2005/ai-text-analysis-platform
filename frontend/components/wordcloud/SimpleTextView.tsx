'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { WordCloudData } from '@/lib/types';
import { cn } from '@/lib/utils';

interface SimpleTextViewProps {
  words: WordCloudData[];
  selectedWord: string | null;
  onWordClick?: (word: string) => void;
  className?: string;
  height?: number;
  width?: number;
}

export default function SimpleTextView({
  words,
  selectedWord,
  onWordClick,
  className = '',
  height = 500,
  width = 800
}: SimpleTextViewProps) {
  
  // Sort words by frequency (highest first)
  const sortedWords = [...words].sort((a, b) => b.frequency - a.frequency);
  
  // Get font size based on frequency
  const getFontSize = (frequency: number, maxFreq: number): number => {
    const minSize = 12;
    const maxSize = 28;
    const normalized = frequency / maxFreq;
    return Math.max(minSize, maxSize * Math.pow(normalized, 0.6));
  };
  
  // Get color based on sentiment
  const getSentimentColor = (sentiment: string | null): string => {
    switch (sentiment) {
      case 'positive':
        return 'text-green-600';
      case 'negative':
        return 'text-red-600';
      case 'neutral':
      default:
        return 'text-gray-700';
    }
  };
  
  const maxFrequency = Math.max(...words.map(w => w.frequency));
  
  if (words.length === 0) {
    return (
      <div 
        className={cn("flex items-center justify-center", className)} 
        style={{ height, width }}
      >
        <div className="text-center text-gray-500">
          <p className="mb-2">No words to display</p>
          <p className="text-sm">Try a different analysis mode</p>
        </div>
      </div>
    );
  }
  
  return (
    <div 
      className={cn("overflow-auto p-6", className)} 
      style={{ height, width }}
    >
      <div className="flex flex-wrap gap-x-4 gap-y-2 justify-center items-center leading-relaxed">
        {sortedWords.map((word, index) => {
          const fontSize = getFontSize(word.frequency, maxFrequency);
          const isSelected = selectedWord === word.word;
          
          return (
            <motion.span
              key={word.word}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ 
                delay: index * 0.02,
                duration: 0.3,
                ease: "easeOut"
              }}
              className={cn(
                "inline-block px-2 py-1 rounded-md cursor-pointer transition-all duration-200 select-none",
                getSentimentColor(word.sentiment),
                isSelected 
                  ? "bg-blue-100 ring-2 ring-blue-500 font-semibold transform scale-110" 
                  : "hover:bg-gray-100 hover:shadow-sm hover:transform hover:scale-105",
                "font-medium"
              )}
              style={{
                fontSize: `${fontSize}px`,
                fontWeight: isSelected ? 600 : Math.max(400, 400 + (word.frequency / maxFrequency) * 200)
              }}
              onClick={() => onWordClick?.(word.word)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.98 }}
            >
              {word.word}
              <span className="text-xs opacity-60 ml-1">
                ({word.frequency})
              </span>
            </motion.span>
          );
        })}
      </div>
      
      {/* Word count info */}
      <div className="mt-6 pt-4 border-t border-gray-200 text-center">
        <p className="text-sm text-gray-600">
          Displaying {words.length} words • Sorted by frequency
        </p>
      </div>
    </div>
  );
}
