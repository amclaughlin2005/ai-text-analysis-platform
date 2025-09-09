'use client';

import React, { useState, useEffect } from 'react';

interface DebugWordCloudProps {
  mode: string;
}

export default function DebugWordCloud({ mode }: DebugWordCloudProps) {
  const [debugInfo, setDebugInfo] = useState<string[]>([]);
  const [words, setWords] = useState<string[]>([]);

  useEffect(() => {
    const logs: string[] = [];
    logs.push(`Effect triggered with mode: ${mode}`);
    
    try {
      const simpleWords = ['test', 'word', 'cloud', 'demo', 'simple'];
      logs.push(`Generated ${simpleWords.length} words`);
      setWords(simpleWords);
      logs.push('Words set successfully');
    } catch (error) {
      logs.push(`Error: ${error}`);
    }
    
    setDebugInfo(logs);
  }, [mode]);

  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-yellow-800 mb-4">
        Debug Word Cloud - Mode: {mode}
      </h3>
      
      <div className="space-y-4">
        <div>
          <h4 className="font-medium text-yellow-700 mb-2">Debug Log:</h4>
          <div className="text-sm text-yellow-600 space-y-1">
            {debugInfo.map((log, index) => (
              <div key={index}>• {log}</div>
            ))}
          </div>
        </div>
        
        <div>
          <h4 className="font-medium text-yellow-700 mb-2">Generated Words ({words.length}):</h4>
          <div className="flex flex-wrap gap-2">
            {words.map((word, index) => (
              <span 
                key={index}
                className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-lg border border-yellow-300"
              >
                {word}
              </span>
            ))}
          </div>
        </div>
        
        {words.length === 0 && (
          <div className="text-red-600 font-medium">
            ⚠️ No words generated - this indicates a problem with data generation
          </div>
        )}
      </div>
    </div>
  );
}
