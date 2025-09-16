'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { RefreshCw, Download, Settings, Filter, LayoutGrid, List, ChevronDown, ChevronUp } from 'lucide-react';
import { WordCloudData, WordCloudFilters } from '@/lib/types';
import { cn, getSentimentColor, formatNumber } from '@/lib/utils';
import ColumnFilterSelector from './ColumnFilterSelector';
import ModernWordCloud from './ModernWordCloud';
import SimpleTextView from './SimpleTextView';

interface SimpleWordCloudProps {
  datasetId?: string; // Single dataset (for backwards compatibility)
  datasetIds?: string[]; // Multiple datasets (new feature)
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
  datasetIds,
  mode, 
  filters, 
  selectedColumns = [1, 2], // Default: questions and responses
  showColumnFilter = false,
  onWordClick,
  onColumnsChange,
  className 
}: SimpleWordCloudProps) {
  
  // Determine which datasets to use (prioritize datasetIds over datasetId)
  const datasetsToUse = datasetIds && datasetIds.length > 0 ? datasetIds : (datasetId ? [datasetId] : []);
  const isMultiDataset = datasetsToUse.length > 1;
  // Initialize with immediate data to prevent loading stuck
  const [words, setWords] = useState<WordCloudData[]>(() => generateSimpleWordData(mode));
  const [selectedWord, setSelectedWord] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [showColumnFilterUI, setShowColumnFilterUI] = useState(false); // Default collapsed to save space
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const [viewMode, setViewMode] = useState<'cloud' | 'text'>('cloud');
  
  // All datasets now use the Railway API with proper column filtering

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
      
      console.log('🚀 fetchWordCloudData called with datasets:', datasetsToUse, 'mode:', mode, 'columns:', selectedColumns);
      
      if (datasetsToUse.length === 0) {
        console.log('⚠️ No datasets provided, skipping API call');
        setWords(generateSimpleWordData(mode));
        isRequestingRef.current = false;
        setLoading(false);
        return;
      }
      
      try {        
        const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://ai-text-analysis-production.up.railway.app';
        console.log('🚀 Making API call with selectedColumns:', selectedColumns);
        
        let apiPayload: any;
        let endpoint: string;
        
        if (isMultiDataset) {
          // Use multi-dataset endpoint
          console.log('🚀 Using multi-dataset API for combined analysis');
          apiPayload = {
            dataset_ids: datasetsToUse,
            mode: mode,
            selected_columns: selectedColumns,
            exclude_words: filters?.excludeWords,
            max_words: filters?.maxWords || 100,
            filters: filters
          };
          endpoint = `${API_BASE_URL}/api/wordcloud/generate-multi`;
        } else {
          // Use single dataset endpoint
          console.log('🚀 Using single dataset API');
          apiPayload = {
            dataset_id: datasetsToUse[0],
            mode: mode,
            selected_columns: selectedColumns,
            exclude_words: filters?.excludeWords,
            max_words: filters?.maxWords || 100,
            filters: filters
          };
          endpoint = `${API_BASE_URL}/api/wordcloud/generate`;
        }
        
        console.log('📤 API Payload:', apiPayload);
        console.log('📤 API Endpoint:', endpoint);
        
        const response = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(apiPayload)
        });
        
        if (response.ok) {
          const data = await response.json();
          console.log('✅ API Response received:', data);
          
          // Handle different response formats
          let wordsArray: any[] = [];
          
          if (data.success && data.data && Array.isArray(data.data)) {
            wordsArray = data.data;
            console.log('📊 Using data.success.data format, words found:', wordsArray.length);
          } else if (data.words && Array.isArray(data.words)) {
            wordsArray = data.words;
            console.log('📊 Using data.words format, words found:', wordsArray.length);
          } else if (Array.isArray(data)) {
            wordsArray = data;
            console.log('📊 Using direct array format, words found:', wordsArray.length);
          } else {
            console.error('❌ Unexpected API response format:', data);
          }
          
          if (wordsArray.length > 0) {
            const apiWords = wordsArray.map((w: any) => ({
              word: w.word || w.text,  // Handle both formats
              frequency: w.frequency || w.value || w.weight,  // Handle both formats
              sentiment: w.sentiment || w.sentiment_association || 'neutral',
              category: mode,
              size: w.size || Math.max(0.1, (w.frequency || w.value || w.weight || 0) / 100),
              color: getSentimentColor(w.sentiment || w.sentiment_association || 'neutral')
            }));
            
            console.log('✅ Successfully processed API data:', apiWords.length, 'words');
            setWords(apiWords);
            setLoading(false);
            isRequestingRef.current = false;
            return;
          } else {
            console.error('❌ No words found in API response');
          }
        } else {
          const errorText = await response.text();
          console.error('❌ API request failed:', response.status, response.statusText, errorText);
          throw new Error(`API request failed: ${response.status} ${response.statusText}`);
        }
        
        throw new Error('API response invalid - no words found');
        
      } catch (error) {
        console.log('⚠️ API error:', error);
        setError(error instanceof Error ? error.message : 'Failed to load word cloud');
        
        // Auto-retry once after a short delay for CORS/network issues
        if (retryCount === 0) {
          console.log('🔄 Auto-retrying after 2 seconds...');
          setTimeout(() => {
            setRetryCount(1);
            setError(null);
            isRequestingRef.current = false;
            // This will trigger the useEffect again
          }, 2000);
        } else {
          // After retry fails, fallback to enhanced mock data
          console.log('⚠️ API retry failed, using enhanced mock data with column filtering:', error);
          
          // Generate enhanced mock data that respects column filtering
          let newWords;
          if (datasetsToUse.includes('06a8437a-27e8-412f-a530-6cb04f7b6dc9')) {
            // Use enhanced legal data with column filtering - up to 100 words
            newWords = generateFilteredLegalDataByColumns(mode, selectedColumns);
            // If still too few words, supplement with more
            if (newWords.length < 50) {
              const additionalWords = generateSimpleWordData(mode).slice(0, 100 - newWords.length);
              newWords = [...newWords, ...additionalWords];
            }
            console.log(`✅ Using enhanced legal mock data (${selectedColumns.join(',')} columns):`, newWords.length, 'words');
          } else {
            newWords = generateSimpleWordData(mode);
            console.log('Using standard mock data:', newWords.length, 'words');
          }
          setWords(newWords);
          setLoading(false);
          isRequestingRef.current = false;
        }
      }
    };
    
    console.log('🔄 useEffect triggered - mode:', mode, 'datasets:', datasetsToUse, 'selectedColumns:', selectedColumns, 'retryCount:', retryCount);
    fetchWordCloudData();
  }, [mode, JSON.stringify(datasetsToUse), JSON.stringify(selectedColumns), retryCount]); // Include retryCount for auto-retry

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
    setError(null);
    setRetryCount(0); // Reset retry count for manual refresh
    isRequestingRef.current = false; // Allow new request
    
    // Trigger useEffect to retry API call
    setTimeout(() => {
      setRetryCount(prev => prev + 1);
    }, 100);
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
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <span>{formatNumber(words.length)} words • Interactive mode enabled</span>
            {datasetsToUse.includes('06a8437a-27e8-412f-a530-6cb04f7b6dc9') && (
              <>
                <span>•</span>
                <div className="flex items-center gap-1">
                  <Filter className="h-3 w-3" />
                  <span>Columns: {selectedColumns.join(', ')}</span>
                  <span className="text-xs text-blue-600">
                    ({selectedColumns.length === 1 && selectedColumns[0] === 1 ? 'Questions Only' : 
                      selectedColumns.length === 1 && selectedColumns[0] === 2 ? 'Responses Only' :
                      selectedColumns.length === 2 ? 'Questions & Responses' : 'Custom'})
                  </span>
                </div>
              </>
            )}
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {/* Collapsible Column Filter Toggle (only for legal dataset) */}
          {datasetsToUse.includes('06a8437a-27e8-412f-a530-6cb04f7b6dc9') && (
            <button
              onClick={() => setShowColumnFilterUI(!showColumnFilterUI)}
              className={cn(
                "flex items-center gap-2 px-3 py-2 rounded-lg transition-all duration-200 text-sm font-medium border",
                showColumnFilterUI 
                  ? "bg-blue-100 text-blue-700 border-blue-200 shadow-sm" 
                  : "bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100 hover:border-gray-300"
              )}
              title={showColumnFilterUI ? "Hide column filters" : "Show column filters"}
            >
              <Filter className="h-4 w-4" />
              <span>Filters ({selectedColumns.length})</span>
              {showColumnFilterUI ? (
                <ChevronUp className="h-3 w-3 ml-1" />
              ) : (
                <ChevronDown className="h-3 w-3 ml-1" />
              )}
            </button>
          )}
          
          {/* View Mode Toggle */}
          <div className="flex border border-gray-300 rounded-lg overflow-hidden">
            <button
              onClick={() => setViewMode('cloud')}
              className={cn(
                "p-2 transition-colors text-sm",
                viewMode === 'cloud'
                  ? "bg-primary-600 text-white"
                  : "text-gray-500 hover:text-gray-700 hover:bg-gray-100"
              )}
              title="Cloud View"
            >
              <LayoutGrid className="h-4 w-4" />
            </button>
            <button
              onClick={() => setViewMode('text')}
              className={cn(
                "p-2 transition-colors text-sm",
                viewMode === 'text'
                  ? "bg-primary-600 text-white"
                  : "text-gray-500 hover:text-gray-700 hover:bg-gray-100"
              )}
              title="Text View"
            >
              <List className="h-4 w-4" />
            </button>
          </div>
          
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
        {showColumnFilterUI && datasetsToUse.includes('06a8437a-27e8-412f-a530-6cb04f7b6dc9') && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="border-b border-blue-200 shadow-sm"
          >
            <div className="px-4 py-3 bg-gradient-to-r from-blue-50 to-blue-100 border-b border-blue-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Filter className="h-4 w-4 text-blue-600" />
                  <span className="text-sm font-semibold text-blue-900">Column Filters</span>
                  <span className="text-xs bg-blue-200 text-blue-700 px-2 py-1 rounded-full">
                    {selectedColumns.length} selected
                  </span>
                </div>
                <button
                  onClick={() => setShowColumnFilterUI(false)}
                  className="p-1 text-blue-600 hover:bg-blue-200 rounded-lg transition-colors"
                  title="Collapse filters"
                >
                  <ChevronUp className="h-4 w-4" />
                </button>
              </div>
              <p className="text-xs text-blue-700 mt-1">
                Analyzing: {selectedColumns.map(col => 
                  col === 1 ? 'Questions' : col === 2 ? 'Responses' : `Column ${col}`
                ).join(' + ')}
              </p>
            </div>
            
            <ColumnFilterSelector
              datasetId={datasetsToUse[0] || ''} // Use first dataset or empty string
              selectedColumns={selectedColumns}
              onColumnsChange={(columns) => {
                console.log('📊 Column selection changed from:', selectedColumns, 'to:', columns);
                console.log('🔄 This should trigger a new API call...');
                if (onColumnsChange) {
                  onColumnsChange(columns);
                }
              }}
              className="border-none"
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error State with Auto-Retry */}
      {error && retryCount === 0 && (
        <div className="p-4">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
            <div className="flex items-center justify-center mb-2">
              <RefreshCw className="h-5 w-5 text-yellow-600 animate-spin mr-2" />
              <span className="text-yellow-800 font-medium">Connection Issue Detected</span>
            </div>
            <p className="text-yellow-700 text-sm mb-3">
              Auto-retrying in 2 seconds... This usually resolves CORS timing issues.
            </p>
          </div>
        </div>
      )}

      {/* Failed State (after retry) */}
      {error && retryCount > 0 && (
        <div className="p-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
            <p className="text-red-800 font-medium mb-3">Failed to load word cloud</p>
            <button
              onClick={refreshWordCloud}
              className="inline-flex items-center px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors text-sm"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </button>
          </div>
        </div>
      )}

      {/* Word Cloud Display - Conditional based on viewMode */}
      {!error && (
        <div className="p-4">
          <div className="w-full overflow-x-auto">
            {viewMode === 'cloud' ? (
              <div className="min-w-[1200px] w-full flex justify-center">
                <ModernWordCloud
                  datasetId={datasetsToUse[0] || ''} // Use first dataset or empty string
                  mode={mode === 'verbs' ? 'verbs' : mode === 'themes' ? 'all' : mode}
                  height={600}
                  width={1200}
                  words={words} // Pass the words from SimpleWordCloud
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
            ) : (
              <div className="min-w-[1200px] w-full flex justify-center">
                <SimpleTextView
                  words={words}
                  selectedWord={selectedWord}
                  onWordClick={(word) => {
                    setSelectedWord(selectedWord === word ? null : word);
                    if (onWordClick) {
                      const wordData = words.find(w => w.word === word);
                      if (wordData) {
                        onWordClick(word, wordData);
                      }
                    }
                  }}
                  height={600}
                  width={1200}
                  className="rounded-lg border bg-white"
                />
              </div>
            )}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between p-4 border-t bg-gray-50 text-sm text-gray-600">
        <div className="flex items-center gap-4">
          <span>Total words: {formatNumber(words.length)}</span>
          <span>•</span>
          <span>Mode: {mode}</span>
          <span>•</span>
          <span>View: {viewMode === 'cloud' ? 'Visual Cloud' : 'Text List'}</span>
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
