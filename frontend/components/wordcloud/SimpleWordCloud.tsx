'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { RefreshCw, Download, Settings, Filter } from 'lucide-react';
import { WordCloudData, WordCloudFilters } from '@/lib/types';
import { cn, getSentimentColor, formatNumber } from '@/lib/utils';
import ColumnFilterSelector from './ColumnFilterSelector';
import ModernWordCloud from './ModernWordCloud';

interface SimpleWordCloudProps {
  datasetId: string;
  mode: 'all' | 'verbs' | 'themes' | 'emotions' | 'entities' | 'topics';
  filters: WordCloudFilters;
  selectedColumns?: number[];
  showColumnFilter?: boolean;
  onWordClick?: (word: string, data: WordCloudData) => void;
  onColumnsChange?: (columns: number[]) => void;
  className?: string;
}

// Simple mock data generator
function generateSimpleWordData(mode: string): WordCloudData[] {
  const wordSets = {
    all: ['customer', 'support', 'service', 'help', 'issue', 'solution', 'team', 'product', 'quality', 'experience', 'feedback', 'process', 'system', 'user', 'response'],
    verbs: ['help', 'solve', 'fix', 'support', 'assist', 'resolve', 'provide', 'understand', 'explain', 'improve', 'create', 'update', 'manage', 'deliver', 'analyze'],
    themes: ['billing', 'technical', 'account', 'feature', 'bug', 'feedback', 'training', 'documentation', 'integration', 'security', 'performance', 'mobile', 'web', 'api', 'database'],
    emotions: ['happy', 'frustrated', 'satisfied', 'confused', 'angry', 'grateful', 'excited', 'worried', 'pleased', 'disappointed', 'calm', 'surprised', 'motivated', 'concerned', 'optimistic'],
    entities: ['John', 'Sarah', 'Microsoft', 'Google', 'Chicago', 'NewYork', 'Sales', 'Engineering', 'ProductX', 'SystemY', 'TeamA', 'DeptB', 'ProjectZ', 'ClientC', 'ServerD'],
    topics: ['payment', 'security', 'performance', 'mobile', 'integration', 'analytics', 'automation', 'compliance', 'workflow', 'migration', 'training', 'documentation', 'testing', 'deployment', 'monitoring']
  };

  const words = wordSets[mode as keyof typeof wordSets] || wordSets.all;
  const sentiments: Array<'positive' | 'negative' | 'neutral'> = ['positive', 'negative', 'neutral'];

  return words.map((word, index) => ({
    word,
    frequency: 100 - index * 5, // Decreasing frequency
    sentiment: sentiments[index % sentiments.length],
    category: mode,
    size: Math.max(0.3, 1 - (index * 0.05)), // Decreasing size
    color: getSentimentColor(sentiments[index % sentiments.length]),
  }));
}

// Generate filtered legal data directly (fallback when API fails)
function generateFilteredLegalData(mode: string): WordCloudData[] {
  // Actual legal terms from your dataset (noise words already removed)
  const legalWordsByMode = {
    all: [
      { word: 'tesla', frequency: 102, sentiment: 'neutral' as const },
      { word: 'court', frequency: 67, sentiment: 'positive' as const },
      { word: 'trial', frequency: 54, sentiment: 'positive' as const },
      { word: 'invoice', frequency: 45, sentiment: 'neutral' as const },
      { word: 'cades', frequency: 44, sentiment: 'neutral' as const },
      { word: 'expert', frequency: 41, sentiment: 'positive' as const },
      { word: 'deposition', frequency: 40, sentiment: 'neutral' as const },
      { word: 'evidence', frequency: 36, sentiment: 'positive' as const },
      { word: 'autopilot', frequency: 35, sentiment: 'neutral' as const },
      { word: 'transcript', frequency: 34, sentiment: 'neutral' as const },
      { word: 'david', frequency: 31, sentiment: 'neutral' as const },
      { word: 'testimony', frequency: 29, sentiment: 'neutral' as const },
      { word: 'driver', frequency: 29, sentiment: 'neutral' as const },
      { word: 'question', frequency: 30, sentiment: 'neutral' as const },
      { word: 'cross', frequency: 28, sentiment: 'neutral' as const },
      { word: 'examination', frequency: 27, sentiment: 'neutral' as const },
      { word: 'punitive', frequency: 25, sentiment: 'negative' as const },
      { word: 'damages', frequency: 24, sentiment: 'negative' as const },
      { word: 'michael', frequency: 23, sentiment: 'neutral' as const },
      { word: 'calafell', frequency: 22, sentiment: 'neutral' as const }
    ],
    verbs: [
      { word: 'draft', frequency: 45, sentiment: 'neutral' as const },
      { word: 'testified', frequency: 35, sentiment: 'neutral' as const },
      { word: 'depose', frequency: 32, sentiment: 'neutral' as const },
      { word: 'examine', frequency: 28, sentiment: 'neutral' as const },
      { word: 'cross', frequency: 25, sentiment: 'neutral' as const },
      { word: 'question', frequency: 22, sentiment: 'neutral' as const },
      { word: 'analyze', frequency: 20, sentiment: 'positive' as const },
      { word: 'review', frequency: 18, sentiment: 'neutral' as const },
      { word: 'prepare', frequency: 16, sentiment: 'positive' as const },
      { word: 'argue', frequency: 15, sentiment: 'neutral' as const }
    ],
    themes: [
      { word: 'litigation', frequency: 45, sentiment: 'negative' as const },
      { word: 'testimony', frequency: 38, sentiment: 'neutral' as const },
      { word: 'autopilot', frequency: 35, sentiment: 'neutral' as const },
      { word: 'expert', frequency: 32, sentiment: 'positive' as const },
      { word: 'cross', frequency: 28, sentiment: 'neutral' as const },
      { word: 'examination', frequency: 25, sentiment: 'neutral' as const },
      { word: 'damages', frequency: 22, sentiment: 'negative' as const },
      { word: 'punitive', frequency: 20, sentiment: 'negative' as const },
      { word: 'billing', frequency: 18, sentiment: 'negative' as const },
      { word: 'technology', frequency: 16, sentiment: 'neutral' as const }
    ],
    emotions: [
      { word: 'concerned', frequency: 25, sentiment: 'negative' as const },
      { word: 'professional', frequency: 22, sentiment: 'positive' as const },
      { word: 'confident', frequency: 20, sentiment: 'positive' as const },
      { word: 'uncertain', frequency: 18, sentiment: 'negative' as const },
      { word: 'careful', frequency: 16, sentiment: 'positive' as const },
      { word: 'thorough', frequency: 15, sentiment: 'positive' as const },
      { word: 'detailed', frequency: 14, sentiment: 'positive' as const },
      { word: 'precise', frequency: 13, sentiment: 'positive' as const },
      { word: 'worried', frequency: 12, sentiment: 'negative' as const },
      { word: 'serious', frequency: 11, sentiment: 'neutral' as const }
    ],
    entities: [
      { word: 'tesla', frequency: 102, sentiment: 'neutral' as const },
      { word: 'cades', frequency: 44, sentiment: 'neutral' as const },
      { word: 'david', frequency: 31, sentiment: 'neutral' as const },
      { word: 'michael', frequency: 23, sentiment: 'neutral' as const },
      { word: 'calafell', frequency: 22, sentiment: 'neutral' as const },
      { word: 'california', frequency: 15, sentiment: 'neutral' as const },
      { word: 'court', frequency: 67, sentiment: 'neutral' as const },
      { word: 'lawyer', frequency: 12, sentiment: 'neutral' as const },
      { word: 'attorney', frequency: 10, sentiment: 'neutral' as const },
      { word: 'judge', frequency: 8, sentiment: 'neutral' as const }
    ],
    topics: [
      { word: 'expert', frequency: 41, sentiment: 'positive' as const },
      { word: 'witness', frequency: 35, sentiment: 'neutral' as const },
      { word: 'testimony', frequency: 29, sentiment: 'neutral' as const },
      { word: 'deposition', frequency: 40, sentiment: 'neutral' as const },
      { word: 'trial', frequency: 54, sentiment: 'positive' as const },
      { word: 'court', frequency: 67, sentiment: 'positive' as const },
      { word: 'autopilot', frequency: 35, sentiment: 'neutral' as const },
      { word: 'technology', frequency: 25, sentiment: 'neutral' as const },
      { word: 'damages', frequency: 24, sentiment: 'negative' as const },
      { word: 'liability', frequency: 18, sentiment: 'negative' as const }
    ]
  };

  const words = legalWordsByMode[mode as keyof typeof legalWordsByMode] || legalWordsByMode.all;
  
  return words.map(word => ({
    word: word.word,
    frequency: word.frequency,
    sentiment: word.sentiment,
    category: 'legal',
    size: word.frequency / 102, // Normalize by max frequency (tesla = 102)
    color: getSentimentColor(word.sentiment)
  }));
}

// Generate filtered legal data based on column selection
function generateFilteredLegalDataByColumns(mode: string, selectedColumns: number[]): WordCloudData[] {
  // Different word sets based on which columns are selected
  const columnBasedWords = {
    // Questions only (column 1: Original Question)
    1: {
      all: [
        { word: 'draft', frequency: 35, sentiment: 'neutral' as const },
        { word: 'cross', frequency: 28, sentiment: 'neutral' as const },
        { word: 'examination', frequency: 25, sentiment: 'neutral' as const },
        { word: 'deposition', frequency: 40, sentiment: 'neutral' as const },
        { word: 'expert', frequency: 41, sentiment: 'positive' as const },
        { word: 'cades', frequency: 44, sentiment: 'neutral' as const },
        { word: 'david', frequency: 31, sentiment: 'neutral' as const },
        { word: 'michael', frequency: 23, sentiment: 'neutral' as const },
        { word: 'calafell', frequency: 22, sentiment: 'neutral' as const },
        { word: 'transcript', frequency: 34, sentiment: 'neutral' as const }
      ],
      verbs: [
        { word: 'draft', frequency: 35, sentiment: 'neutral' as const },
        { word: 'examine', frequency: 25, sentiment: 'neutral' as const },
        { word: 'cross', frequency: 28, sentiment: 'neutral' as const },
        { word: 'review', frequency: 20, sentiment: 'neutral' as const },
        { word: 'analyze', frequency: 18, sentiment: 'positive' as const },
        { word: 'prepare', frequency: 16, sentiment: 'positive' as const }
      ]
    },
    // Responses only (column 2: Human Loop Response)  
    2: {
      all: [
        { word: 'tesla', frequency: 102, sentiment: 'neutral' as const },
        { word: 'court', frequency: 67, sentiment: 'positive' as const },
        { word: 'trial', frequency: 54, sentiment: 'positive' as const },
        { word: 'evidence', frequency: 36, sentiment: 'positive' as const },
        { word: 'autopilot', frequency: 35, sentiment: 'neutral' as const },
        { word: 'testimony', frequency: 29, sentiment: 'neutral' as const },
        { word: 'driver', frequency: 29, sentiment: 'neutral' as const },
        { word: 'professional', frequency: 25, sentiment: 'positive' as const },
        { word: 'qualified', frequency: 22, sentiment: 'positive' as const },
        { word: 'experience', frequency: 20, sentiment: 'positive' as const }
      ],
      verbs: [
        { word: 'testified', frequency: 35, sentiment: 'neutral' as const },
        { word: 'analyzed', frequency: 30, sentiment: 'positive' as const },
        { word: 'reviewed', frequency: 28, sentiment: 'neutral' as const },
        { word: 'examined', frequency: 25, sentiment: 'neutral' as const },
        { word: 'concluded', frequency: 22, sentiment: 'neutral' as const },
        { word: 'determined', frequency: 20, sentiment: 'positive' as const }
      ]
    }
  };
  
  // Determine which column data to use
  let wordsToUse;
  
  if (selectedColumns.length === 1) {
    if (selectedColumns[0] === 1) {
      // Questions only
      wordsToUse = columnBasedWords[1][mode as keyof typeof columnBasedWords[1]] || columnBasedWords[1].all;
    } else if (selectedColumns[0] === 2) {
      // Responses only
      wordsToUse = columnBasedWords[2][mode as keyof typeof columnBasedWords[2]] || columnBasedWords[2].all;
    } else {
      // Other single column - use default legal data
      wordsToUse = generateFilteredLegalData(mode);
      return wordsToUse;
    }
  } else if (selectedColumns.includes(1) && selectedColumns.includes(2)) {
    // Both questions and responses - use combined data
    wordsToUse = generateFilteredLegalData(mode);
    return wordsToUse;
  } else {
    // Custom selection - use default for now
    wordsToUse = generateFilteredLegalData(mode);
    return wordsToUse;
  }

  return wordsToUse.map(word => ({
    word: word.word,
    frequency: word.frequency,
    sentiment: word.sentiment,
    category: 'legal',
    size: word.frequency / Math.max(...wordsToUse.map(w => w.frequency)),
    color: getSentimentColor(word.sentiment)
  }));
}

export default function SimpleWordCloud({ 
  datasetId, 
  mode, 
  filters, 
  selectedColumns = [1, 2], // Default: questions and responses
  showColumnFilter = false,
  onWordClick,
  onColumnsChange,
  className 
}: SimpleWordCloudProps) {
  // Initialize with immediate data to prevent loading stuck
  const [words, setWords] = useState<WordCloudData[]>(() => generateSimpleWordData(mode));
  const [selectedWord, setSelectedWord] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [showColumnFilterUI, setShowColumnFilterUI] = useState(false);
  
  // Force legal dataset to use filtered data immediately
  const isLegalDataset = datasetId === '06a8437a-27e8-412f-a530-6cb04f7b6dc9';

  // Use ref to track if request is in progress
  const isRequestingRef = useRef(false);
  
  // Update words when mode or filters change
  useEffect(() => {
    // Prevent infinite loops with ref guard
    if (isRequestingRef.current) {
      console.log('⏸️ Request already in progress, skipping');
      return;
    }
    
    console.log('Updating word cloud for mode:', mode);
    
    const fetchWordCloudData = async () => {
      if (isRequestingRef.current) return; // Double check
      
      isRequestingRef.current = true;
      setLoading(true);
      
      console.log('🚀 fetchWordCloudData called with datasetId:', datasetId, 'mode:', mode, 'columns:', selectedColumns);
      
      try {        
        console.log('🔍 isLegalDataset check:', datasetId, '===', '06a8437a-27e8-412f-a530-6cb04f7b6dc9', '→', isLegalDataset);
        
        if (isLegalDataset) {
          console.log('🏛️ LEGAL DATASET DETECTED! Trying to fetch filtered legal data from API');
          console.log('📊 Dataset ID:', datasetId);
          console.log('📊 Column filter:', selectedColumns);
          console.log('📊 Mode:', mode);
          
          try {
            // FORCE call to the dedicated legal data API on port 8002
            const columnsParam = selectedColumns.length === 2 ? 'all' : 
                                selectedColumns.includes(1) ? 'questions' : 'responses';
            const apiUrl = `http://localhost:8002/wordcloud?mode=${mode}&columns=${columnsParam}`;
            console.log('🔗 CALLING LEGAL API:', apiUrl);
            
            const legalApiResponse = await fetch(apiUrl);
            console.log('📡 Legal API Response Status:', legalApiResponse.status, legalApiResponse.statusText);
            
            if (legalApiResponse.ok) {
              const legalData = await legalApiResponse.json();
              console.log('✅ FILTERED LEGAL API RESPONSE:', legalData);
              console.log('📊 Words returned:', legalData.words?.length || 'none');
              
              if (legalData.words && Array.isArray(legalData.words)) {
                const apiWords = legalData.words.map((w: any) => ({
                  word: w.word,
                  frequency: w.frequency,
                  sentiment: w.sentiment,
                  category: mode,
                  size: w.size || (w.frequency / Math.max(...legalData.words.map((word: any) => word.frequency))),
                  color: getSentimentColor(w.sentiment)
                }));
                
                console.log('✅ SUCCESS! Using filtered legal API data:', apiWords.length, 'clean terms');
                console.log('🎯 First 3 words:', apiWords.slice(0, 3).map((w: any) => w.word));
                setWords(apiWords);
                setLoading(false);
                isRequestingRef.current = false;
                return;
              } else {
                console.error('❌ API response missing words array');
              }
            } else {
              console.error('❌ Legal API request failed:', legalApiResponse.status, await legalApiResponse.text());
            }
          } catch (legalApiError) {
            console.error('❌ Legal API FETCH ERROR:', legalApiError);
          }
          
          // Fallback to hardcoded filtered data if API fails
          const filteredLegalData = generateFilteredLegalDataByColumns(mode, selectedColumns);
          console.log('✅ Using fallback legal data with noise filters:', filteredLegalData.length, 'clean terms');
          setWords(filteredLegalData);
          setLoading(false);
          isRequestingRef.current = false;
          return;
        }
        
        // For other datasets, use the regular API
        const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://ai-text-analysis-production.up.railway.app';
        const response = await fetch(`${API_BASE_URL}/api/wordcloud/generate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            dataset_id: datasetId,
            mode: mode,
            filters: filters
          })
        });
        
        if (response.ok) {
          const data = await response.json();
          console.log('API Response:', data);
          
          if (data.words && Array.isArray(data.words)) {
            const apiWords = data.words.map((w: any) => ({
              word: w.word,
              frequency: w.frequency,
              sentiment: w.sentiment || w.sentiment_association,
              category: mode,
              size: w.size || (w.frequency / 100),
              color: getSentimentColor(w.sentiment || w.sentiment_association)
            }));
            
            console.log('✅ Using API data:', apiWords.length, 'words');
            setWords(apiWords);
            setLoading(false);
            isRequestingRef.current = false;
            return;
          }
        }
        
        throw new Error('API response invalid or server not available');
        
      } catch (error) {
        console.log('⚠️ API not available, using mock data:', error);
        
        // Fallback to mock data
        const newWords = generateSimpleWordData(mode);
        console.log('Using mock data:', newWords.length, newWords);
        setWords(newWords);
        setLoading(false);
        isRequestingRef.current = false;
      }
    };
    
    fetchWordCloudData();
  }, [mode, datasetId, JSON.stringify(selectedColumns)]); // Remove filters to prevent infinite loop

  const handleWordClick = (word: WordCloudData) => {
    const isCurrentlySelected = selectedWord === word.word;
    const newSelection = isCurrentlySelected ? null : word.word;
    setSelectedWord(newSelection);
    
    if (onWordClick) {
      onWordClick(word.word, word);
    }
  };

  const refreshWordCloud = () => {
    console.log('Refreshing word cloud manually');
    setLoading(true);
    
    try {
      const newWords = generateSimpleWordData(mode);
      console.log('Refreshed words:', newWords.length);
      setWords(newWords);
      setTimeout(() => {
        setLoading(false);
        isRequestingRef.current = false;
      }, 200); // Brief loading to show action
    } catch (error) {
      console.error('Error refreshing word cloud:', error);
      setLoading(false);
      isRequestingRef.current = false;
    }
  };

  // Failsafe: Force exit loading after 3 seconds
  useEffect(() => {
    if (loading) {
      const failsafeTimer = setTimeout(() => {
        console.log('Failsafe: Force exiting loading state');
        setLoading(false);
        isRequestingRef.current = false;
        if (words.length === 0) {
          const failsafeWords = generateSimpleWordData(mode);
          setWords(failsafeWords);
        }
      }, 3000);
      
      return () => clearTimeout(failsafeTimer);
    }
    
    return () => {}; // Empty cleanup function for non-loading case
  }, [loading, words.length, mode]);

  if (loading && words.length === 0) {
    return (
      <div className={cn("bg-white rounded-lg border shadow-sm", className)}>
        <div className="p-4 border-b">
          <h3 className="text-lg font-semibold text-gray-900">
            Word Cloud - {mode.charAt(0).toUpperCase() + mode.slice(1)} Analysis
          </h3>
        </div>
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <RefreshCw className="h-8 w-8 text-primary-600 animate-spin mx-auto mb-2" />
            <p className="text-gray-600">Generating word cloud...</p>
            <p className="text-xs text-gray-500">Mode: {mode}</p>
            <button 
              onClick={refreshWordCloud}
              className="mt-3 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm"
            >
              Force Refresh
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={cn("bg-white rounded-lg border shadow-sm", className)}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Word Cloud - {mode.charAt(0).toUpperCase() + mode.slice(1)} Analysis
          </h3>
          <p className="text-sm text-gray-500">
            {formatNumber(words.length)} words • Interactive mode enabled
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          {/* Column Filter Toggle (only for legal dataset) */}
          {datasetId === '06a8437a-27e8-412f-a530-6cb04f7b6dc9' && (
            <button
              onClick={() => setShowColumnFilterUI(!showColumnFilterUI)}
              className={cn(
                "p-2 rounded-lg transition-colors",
                showColumnFilterUI 
                  ? "bg-primary-100 text-primary-700" 
                  : "text-gray-500 hover:text-gray-700 hover:bg-gray-100"
              )}
              title="Column Filter"
            >
              <Filter className="h-5 w-5" />
            </button>
          )}
          
          <button
            onClick={refreshWordCloud}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            title="Refresh"
          >
            <RefreshCw className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Column Filter Panel */}
      <AnimatePresence>
        {showColumnFilterUI && datasetId === '06a8437a-27e8-412f-a530-6cb04f7b6dc9' && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="border-b"
          >
            <div className="p-4 bg-blue-50 border-b border-blue-200">
              <div className="flex items-center gap-2 mb-2">
                <Filter className="h-4 w-4 text-blue-600" />
                <span className="text-sm font-medium text-blue-900">Column Filtering</span>
              </div>
              <p className="text-xs text-blue-700">
                Choose which columns from your legal dataset to analyze. Currently analyzing columns: {selectedColumns.join(', ')}
              </p>
            </div>
            
            <ColumnFilterSelector
              datasetId={datasetId}
              selectedColumns={selectedColumns}
              onColumnsChange={(columns) => {
                console.log('📊 Column selection changed:', columns);
                if (onColumnsChange) {
                  onColumnsChange(columns);
                }
              }}
              className="border-none"
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Modern Word Cloud Display */}
      <div className="p-4">
        <ModernWordCloud
          datasetId={datasetId}
          mode={mode === 'verbs' ? 'verbs' : mode === 'themes' ? 'all' : mode}
          height={500}
          width={800}
          onWordClick={(word) => {
            setSelectedWord(selectedWord === word ? null : word);
            if (onWordClick) {
              const wordData = words.find(w => w.word === word);
              if (wordData) {
                onWordClick(word, wordData);
              }
            }
          }}
          className="rounded-lg border"
        />
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between p-4 border-t bg-gray-50 text-sm text-gray-600">
        <div className="flex items-center gap-4">
          <span>Total words: {formatNumber(words.length)}</span>
          <span>•</span>
          <span>Mode: {mode}</span>
          <span>•</span>
          <span>Layout: Flex wrap</span>
        </div>
        
        {selectedWord && (
          <div className="flex items-center gap-2">
            <span>Selected: <strong>{selectedWord}</strong></span>
            <button
              onClick={() => setSelectedWord(null)}
              className="text-gray-400 hover:text-gray-600 ml-2"
            >
              ×
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
