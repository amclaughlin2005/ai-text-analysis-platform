'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import SimpleWordCloud from '@/components/wordcloud/SimpleWordCloud';
import DatasetSelector from '@/components/datasets/DatasetSelector';
import { WordCloudFilters } from '@/lib/types';
import { Database, Users, Sparkles } from 'lucide-react';

const ANALYSIS_MODES = [
  { 
    id: 'all', 
    label: 'All Words',
    description: 'Complete vocabulary from your uploaded dataset'
  },
  { 
    id: 'verbs', 
    label: 'Action Words',
    description: 'Verbs and action-oriented language from your data'
  },
  { 
    id: 'themes', 
    label: 'Themes',
    description: 'Common themes and topics in your dataset'
  },
  { 
    id: 'emotions', 
    label: 'Emotions',
    description: 'Emotional language and sentiment indicators'
  },
  { 
    id: 'entities', 
    label: 'Entities',
    description: 'Named entities like people, places, and organizations'
  },
  { 
    id: 'topics', 
    label: 'Topics',
    description: 'Topic modeling results from machine learning analysis'
  }
];

export default function WordCloud() {
  const [selectedMode, setSelectedMode] = useState<string>('all');
  const filters: WordCloudFilters = {};
  const [selectedWord, setSelectedWord] = useState<string | null>(null);
  
  // Dataset selection state
  const [selectedDatasets, setSelectedDatasets] = useState<string[]>([]);
  const [selectedColumns, setSelectedColumns] = useState<number[]>([1, 2]); // Default: questions + responses
  
  // Check for dataset parameter in URL on load
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const datasetParam = urlParams.get('dataset');
    if (datasetParam) {
      console.log('📊 Using dataset from URL:', datasetParam);
      setSelectedDatasets([datasetParam]);
    } else {
      // Default to legal dataset if no URL parameter
      setSelectedDatasets(['06a8437a-27e8-412f-a530-6cb04f7b6dc9']);
    }
  }, []);

  const handleWordClick = (word: string) => {
    setSelectedWord(word === selectedWord ? null : word);
  };



  return (
    <div className="bg-gray-50 min-h-full">
      <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">

      {/* Mode Selection */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Analysis Modes
        </h2>
        <p className="text-gray-600 mb-6">
          Choose different analysis modes to explore your uploaded dataset from various analytical perspectives.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {ANALYSIS_MODES.map((mode) => (
            <motion.button
              key={mode.id}
              onClick={() => setSelectedMode(mode.id)}
              className={`p-4 text-left rounded-lg border-2 transition-all duration-200 ${
                selectedMode === mode.id
                  ? 'border-primary-500 bg-primary-50 text-primary-900'
                  : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
              }`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <h3 className="font-semibold mb-2">{mode.label}</h3>
              <p className="text-sm text-gray-600">{mode.description}</p>
              {selectedMode === mode.id && (
                <div className="mt-2">
                  <div className="h-1 w-8 bg-primary-600 rounded-full"></div>
                </div>
              )}
            </motion.button>
          ))}
        </div>
      </div>

      {/* Dataset Selection */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center space-x-2">
            <Database className="h-5 w-5 text-primary-600" />
            <span>Dataset Selection</span>
          </h2>
          {selectedDatasets.length > 1 && (
            <div className="flex items-center space-x-2 text-sm text-primary-600">
              <Users className="h-4 w-4" />
              <span>Multi-dataset analysis</span>
            </div>
          )}
        </div>
        
        <p className="text-gray-600 mb-4">
          Choose one or multiple datasets to analyze. Multi-dataset selection combines data for comprehensive insights.
        </p>
        
        <DatasetSelector
          selectedDatasets={selectedDatasets}
          onDatasetChange={setSelectedDatasets}
          multiSelect={true}
          placeholder="Select datasets for analysis"
          className="max-w-2xl"
        />
        
        {selectedDatasets.length > 0 && (
          <div className="mt-4 p-3 bg-primary-50 rounded-lg">
            <div className="flex items-center space-x-2 text-primary-800">
              <Sparkles className="h-4 w-4" />
              <span className="text-sm font-medium">
                {selectedDatasets.length === 1 
                  ? 'Analyzing 1 dataset' 
                  : `Combining ${selectedDatasets.length} datasets for analysis`}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Dataset Word Cloud Analysis */}
      {selectedDatasets.length > 0 ? (
        <div className="bg-white rounded-lg border border-primary-200 shadow-sm overflow-hidden">
          <div className="p-4 border-b bg-primary-50">
            <h4 className="text-lg font-semibold text-primary-900">
              📊 Dataset Analysis - {selectedMode.charAt(0).toUpperCase() + selectedMode.slice(1)} Mode
            </h4>
            <p className="text-sm text-primary-700 mt-1">
              Interactive word cloud with advanced filtering and column selection
            </p>
            <p className="text-xs text-primary-600 mt-2">
              {selectedDatasets.length === 1 
                ? `Dataset: ${selectedDatasets[0].slice(0, 8)}...` 
                : `Analyzing ${selectedDatasets.length} datasets combined`} 
              • Noise words automatically filtered • Column filtering available
            </p>
          </div>
          <SimpleWordCloud
            datasetIds={selectedDatasets} // Pass all selected datasets for multi-dataset analysis
            mode={selectedMode as any}
            filters={filters}
            selectedColumns={selectedColumns}
            showColumnFilter={true}
            onWordClick={handleWordClick}
            onColumnsChange={setSelectedColumns}
            className="w-full"
          />
        </div>
      ) : (
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-12 text-center">
          <Database className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No Dataset Selected
          </h3>
          <p className="text-gray-600 mb-6">
            Please select at least one dataset above to generate a word cloud analysis.
          </p>
          <div className="text-sm text-gray-500">
            💡 Upload datasets from the Upload page if you don't have any yet.
          </div>
        </div>
      )}

      {/* Features Highlight */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">
            Column Filtering
          </h3>
          <ul className="space-y-2 text-gray-600">
            <li>• Select specific CSV columns to analyze</li>
            <li>• Questions only, responses only, or combined</li>
            <li>• Real-time word cloud updates</li>
            <li>• Custom column combinations</li>
            <li>• Interactive preset filters</li>
          </ul>
        </div>

        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">
            Analysis Modes
          </h3>
          <ul className="space-y-2 text-gray-600">
            <li>• All significant words from your data</li>
            <li>• Action-oriented verbs and activities</li>
            <li>• Thematic categorization</li>
            <li>• Emotional language detection</li>
            <li>• Named entities extraction</li>
            <li>• Topic modeling insights</li>
          </ul>
        </div>

        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">
            Smart Filtering
          </h3>
          <ul className="space-y-2 text-gray-600">
            <li>• Automatic noise word removal</li>
            <li>• Custom stop word filtering</li>
            <li>• Frequency-based word selection</li>
            <li>• Sentiment-aware analysis</li>
            <li>• Interactive word exploration</li>
          </ul>
        </div>
      </div>


      {/* Selected Word Info */}
      {selectedWord && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-blue-50 border border-blue-200 rounded-lg p-6"
        >
          <h3 className="text-lg font-semibold text-blue-900 mb-2">
            Selected Word: &quot;{selectedWord}&quot;
          </h3>
          <p className="text-blue-700">
            Click on any word in the cloud to explore its usage patterns, frequency distribution, 
            and contextual relationships within your dataset. This interactive feature helps identify 
            key insights and recurring themes in your data.
          </p>
          <button
            onClick={() => setSelectedWord(null)}
            className="mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Clear Selection
          </button>
        </motion.div>
      )}

      </div>
    </div>
  );
}
