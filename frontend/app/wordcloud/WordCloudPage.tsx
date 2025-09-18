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
    selected_columns: [1], // Default: questions only 
    max_words: 100,
    min_word_length: 3
  });
  const [selectedWord, setSelectedWord] = useState<string | null>(null);
  
  // Dataset selection state
  const [selectedDatasets, setSelectedDatasets] = useState<string[]>([]);
  const [selectedColumns, setSelectedColumns] = useState<number[]>([1]); // Default: questions only
  
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
    <div className="bg-gray-50 min-h-screen">
      <div className="max-w-[1920px] mx-auto px-4 py-6">
        
        {/* Compact Controls Row - Top */}
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-4 mb-6">
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

        {/* Main Content Area - Side by Side Layout */}
        <div className="flex gap-6 h-[calc(100vh-200px)]">
          
          {/* Left Side Panel - Filters */}
          <div className="w-80 flex-shrink-0">
            <div className="bg-white rounded-lg border border-gray-200 shadow-sm h-full overflow-y-auto">
              <div className="sticky top-0 bg-white border-b border-gray-200 px-4 py-3 z-10">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <Database className="h-5 w-5 text-primary-600" />
                  Filters & Options
                </h3>
                <p className="text-sm text-gray-600">
                  Customize your word cloud analysis
                </p>
              </div>
              
              <div className="p-0">
                <EnhancedFilterPanel
                  filters={filters}
                  onFiltersChange={setFilters}
                  datasetIds={selectedDatasets}
                  availableOrgs={[]}
                  availableEmails={[]}
                  availableTenants={[]}
                  className="border-0 rounded-none"
                  sidebarMode={true}
                />
              </div>
            </div>
          </div>

          {/* Right Main Area - Word Cloud */}
          <div className="flex-1 min-w-0">
            {selectedDatasets.length > 0 ? (
              <div className="bg-white rounded-lg border border-primary-200 shadow-lg overflow-hidden h-full flex flex-col">
                <div className="px-4 py-3 border-b bg-gradient-to-r from-primary-50 to-primary-100 flex-shrink-0">
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
                
                <div className="flex-1 min-h-0 overflow-hidden">
                  <SimpleWordCloud
                    datasetIds={selectedDatasets}
                    mode={selectedMode as any}
                    filters={filters}
                    selectedColumns={selectedColumns}
                    showColumnFilter={true}
                    onWordClick={handleWordClick}
                    onColumnsChange={setSelectedColumns}
                    className="w-full h-full"
                  />
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg border border-gray-200 shadow-sm h-full flex items-center justify-center">
                <div className="text-center">
                  <Database className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-xl font-medium text-gray-900 mb-2">
                    Select Dataset to Begin
                  </h3>
                  <p className="text-gray-600">
                    Choose a dataset above to generate your word cloud analysis.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Selected Word Info - Floating Bottom Right */}
        {selectedWord && (
          <motion.div
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 100 }}
            className="fixed bottom-6 right-6 bg-blue-600 text-white rounded-lg shadow-lg p-4 z-50 max-w-sm"
          >
            <div className="flex items-start justify-between">
              <div>
                <h4 className="font-semibold text-white mb-1">
                  Selected: &quot;{selectedWord}&quot;
                </h4>
                <p className="text-blue-100 text-sm">
                  Click for detailed analysis
                </p>
              </div>
              <button
                onClick={() => setSelectedWord(null)}
                className="ml-3 text-blue-200 hover:text-white transition-colors"
              >
                ✕
              </button>
            </div>
          </motion.div>
        )}


      </div>
    </div>
  );
}
