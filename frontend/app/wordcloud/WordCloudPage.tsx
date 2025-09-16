'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import SimpleWordCloud from '@/components/wordcloud/SimpleWordCloud';
import DatasetSelector from '@/components/datasets/DatasetSelector';
import EnhancedFilterPanel, { EnhancedFilters } from '@/components/wordcloud/EnhancedFilterPanel';
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
  const [filters, setFilters] = useState<EnhancedFilters>({
    selected_columns: [1, 2], // Default: questions + responses
    max_words: 100,
    min_word_length: 3
  });
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
      <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">

        {/* Enhanced Filter Panel */}
        <EnhancedFilterPanel
          filters={filters}
          onFiltersChange={setFilters}
          availableOrgs={[]} // TODO: Fetch from API
          availableEmails={[]} // TODO: Fetch from API
          availableTenants={[]} // TODO: Fetch from API
        />

        {/* Compact Controls Row */}
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* Analysis Mode - Compact Horizontal */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-primary-600" />
                Analysis Mode
              </h3>
              <div className="flex flex-wrap gap-2">
                {ANALYSIS_MODES.map((mode) => (
                  <motion.button
                    key={mode.id}
                    onClick={() => setSelectedMode(mode.id)}
                    className={`px-3 py-2 text-sm font-medium rounded-lg border transition-all duration-200 ${
                      selectedMode === mode.id
                        ? 'border-primary-500 bg-primary-100 text-primary-900'
                        : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50'
                    }`}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    title={mode.description}
                  >
                    {mode.label}
                  </motion.button>
                ))}
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Current: {ANALYSIS_MODES.find(m => m.id === selectedMode)?.description}
              </p>
            </div>

            {/* Dataset Selection - Compact */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <Database className="h-5 w-5 text-primary-600" />
                Dataset
                {selectedDatasets.length > 1 && (
                  <span className="text-xs bg-primary-100 text-primary-700 px-2 py-1 rounded-full">
                    Multi-dataset
                  </span>
                )}
              </h3>
              
              <DatasetSelector
                selectedDatasets={selectedDatasets}
                onDatasetChange={setSelectedDatasets}
                multiSelect={true}
                placeholder="Select datasets for analysis"
                className="w-full"
              />
              
              {selectedDatasets.length > 0 && (
                <p className="text-xs text-primary-600 mt-2">
                  {selectedDatasets.length === 1 
                    ? `Analyzing dataset ${selectedDatasets[0].slice(0, 8)}...` 
                    : `Combining ${selectedDatasets.length} datasets`}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Word Cloud - Now Prominent and Higher */}
        {selectedDatasets.length > 0 ? (
          <div className="bg-white rounded-lg border border-primary-200 shadow-lg overflow-hidden">
            <div className="px-4 py-3 border-b bg-gradient-to-r from-primary-50 to-primary-100">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-primary-900">
                    {selectedMode.charAt(0).toUpperCase() + selectedMode.slice(1)} Analysis
                  </h2>
                  <p className="text-sm text-primary-700">
                    {selectedDatasets.length === 1 
                      ? `Dataset ${selectedDatasets[0].slice(0, 8)}...` 
                      : `${selectedDatasets.length} datasets combined`}
                  </p>
                </div>
                <div className="text-xs text-primary-600 text-right">
                  <div>Interactive • Click words to explore</div>
                  <div>Auto-filtered • Column selection available</div>
                </div>
              </div>
            </div>
            <SimpleWordCloud
              datasetIds={selectedDatasets}
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
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-8 text-center">
            <Database className="h-12 w-12 text-gray-300 mx-auto mb-3" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Select Dataset to Begin
            </h3>
            <p className="text-gray-600 text-sm">
              Choose a dataset above to generate your word cloud analysis.
            </p>
          </div>
        )}

        {/* Selected Word Info - Above Features */}
        {selectedWord && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-blue-50 border border-blue-200 rounded-lg p-4"
          >
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-blue-900">
                  Selected: &quot;{selectedWord}&quot;
                </h3>
                <p className="text-blue-700 text-sm">
                  Explore usage patterns and contextual relationships for this word.
                </p>
              </div>
              <button
                onClick={() => setSelectedWord(null)}
                className="px-3 py-1 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
              >
                Clear
              </button>
            </div>
          </motion.div>
        )}


      </div>
    </div>
  );
}
