'use client';

import React from 'react';
import { getSentimentColor } from '@/lib/utils';

const testWords = [
  { word: 'customer', frequency: 85, sentiment: 'positive' as const, size: 1.0 },
  { word: 'support', frequency: 72, sentiment: 'neutral' as const, size: 0.8 },
  { word: 'issue', frequency: 68, sentiment: 'negative' as const, size: 0.7 },
  { word: 'help', frequency: 65, sentiment: 'positive' as const, size: 0.6 },
  { word: 'service', frequency: 58, sentiment: 'neutral' as const, size: 0.5 },
  { word: 'problem', frequency: 45, sentiment: 'negative' as const, size: 0.4 },
  { word: 'solution', frequency: 42, sentiment: 'positive' as const, size: 0.4 },
  { word: 'quality', frequency: 38, sentiment: 'positive' as const, size: 0.3 },
  { word: 'team', frequency: 35, sentiment: 'neutral' as const, size: 0.3 },
  { word: 'experience', frequency: 32, sentiment: 'positive' as const, size: 0.3 },
];

interface TestWordCloudProps {
  mode: string;
  className?: string;
}

export default function TestWordCloud({ mode, className }: TestWordCloudProps) {
  console.log('TestWordCloud rendering with mode:', mode);
  
  return (
    <div className={`bg-white rounded-lg border shadow-sm ${className}`}>
      {/* Header */}
      <div className="p-4 border-b">
        <h3 className="text-lg font-semibold text-gray-900">
          Test Word Cloud - {mode.charAt(0).toUpperCase() + mode.slice(1)} Analysis
        </h3>
        <p className="text-sm text-gray-500">
          {testWords.length} test words
        </p>
      </div>

      {/* Word Display */}
      <div className="p-8">
        <div className="flex flex-wrap justify-center items-center gap-4 min-h-[400px]">
          {testWords.map((word, index) => {
            const fontSize = Math.max(16, Math.min(48, word.size * 32));
            
            return (
              <button
                key={word.word}
                className="inline-block px-3 py-2 rounded-lg border border-transparent hover:border-gray-200 hover:shadow-md transition-all duration-200"
                style={{
                  fontSize: `${fontSize}px`,
                  color: getSentimentColor(word.sentiment),
                  fontWeight: 600,
                }}
                onClick={() => console.log('Clicked word:', word.word)}
              >
                {word.word}
              </button>
            );
          })}
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t bg-gray-50 text-sm text-gray-600">
        <div className="flex items-center justify-between">
          <span>Test word cloud loaded successfully</span>
          <span>Mode: {mode}</span>
        </div>
      </div>
    </div>
  );
}
