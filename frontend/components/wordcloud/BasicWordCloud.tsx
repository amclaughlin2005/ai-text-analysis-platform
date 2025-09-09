'use client';

import React, { useState } from 'react';

interface BasicWordCloudProps {
  mode: string;
}

// Basic static data
const staticWords = [
  { text: 'customer', color: '#10b981', size: 32 },
  { text: 'support', color: '#6b7280', size: 28 },
  { text: 'service', color: '#10b981', size: 24 },
  { text: 'help', color: '#10b981', size: 26 },
  { text: 'issue', color: '#ef4444', size: 22 },
  { text: 'solution', color: '#10b981', size: 20 },
  { text: 'team', color: '#6b7280', size: 18 },
  { text: 'quality', color: '#10b981', size: 18 },
  { text: 'response', color: '#6b7280', size: 16 },
  { text: 'feedback', color: '#10b981', size: 16 },
];

export default function BasicWordCloud({ mode }: BasicWordCloudProps) {
  const [selectedWord, setSelectedWord] = useState<string | null>(null);

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
      <div className="p-4 border-b">
        <h3 className="text-lg font-semibold text-gray-900">
          Basic Word Cloud - {mode}
        </h3>
        <p className="text-sm text-gray-500">Static test data</p>
      </div>
      
      <div className="p-8">
        <div className="flex flex-wrap justify-center items-center gap-4 min-h-[300px]">
          {staticWords.map((word, index) => (
            <button
              key={word.text}
              onClick={() => setSelectedWord(selectedWord === word.text ? null : word.text)}
              className={`px-3 py-2 rounded-lg transition-all duration-200 hover:shadow-md border ${
                selectedWord === word.text 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              style={{
                fontSize: `${word.size}px`,
                color: word.color,
                fontWeight: 600,
              }}
            >
              {word.text}
            </button>
          ))}
        </div>
      </div>
      
      <div className="p-4 border-t bg-gray-50 text-sm text-gray-600">
        <div className="flex justify-between items-center">
          <span>Static word cloud test</span>
          {selectedWord && <span>Selected: <strong>{selectedWord}</strong></span>}
        </div>
      </div>
    </div>
  );
}
