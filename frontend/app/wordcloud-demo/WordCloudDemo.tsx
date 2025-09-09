'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, Code, ExternalLink, Github } from 'lucide-react';
import Link from 'next/link';
import SimpleWordCloud from '@/components/wordcloud/SimpleWordCloud';
import { WordCloudFilters } from '@/lib/types';

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

export default function WordCloudDemo() {
  const [selectedMode, setSelectedMode] = useState<string>('all');
  const [filters, setFilters] = useState<WordCloudFilters>({});
  const [selectedWord, setSelectedWord] = useState<string | null>(null);
  
  // Check for dataset parameter in URL
  const [datasetId, setDatasetId] = useState<string>('06a8437a-27e8-412f-a530-6cb04f7b6dc9'); // Default to legal dataset
  const [selectedColumns, setSelectedColumns] = useState<number[]>([1, 2]); // Default: questions + responses
  
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const datasetParam = urlParams.get('dataset');
    if (datasetParam) {
      console.log('📊 Using dataset from URL:', datasetParam);
      setDatasetId(datasetParam);
    }
  }, []);

  const handleWordClick = (word: string) => {
    setSelectedWord(word === selectedWord ? null : word);
  };

  const handleThemeClick = (theme: string) => {
    console.log('Theme clicked:', theme);
    // Could implement theme-based filtering here
  };

  const handleDataUpdate = (data: any[]) => {
    console.log('Word cloud data updated:', data.length, 'words');
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

      {/* Dataset Word Cloud Analysis */}
      <div className="bg-white rounded-lg border border-primary-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b bg-primary-50">
          <h4 className="text-lg font-semibold text-primary-900">
            📊 Dataset Analysis - {selectedMode.charAt(0).toUpperCase() + selectedMode.slice(1)} Mode
          </h4>
          <p className="text-sm text-primary-700 mt-1">
            Interactive word cloud with advanced filtering and column selection
          </p>
          <p className="text-xs text-primary-600 mt-2">
            Dataset ID: {datasetId} • Noise words automatically filtered • Column filtering available
          </p>
        </div>
        <SimpleWordCloud
          datasetId={datasetId}
          mode={selectedMode as any}
          filters={filters}
          selectedColumns={selectedColumns}
          showColumnFilter={true}
          onWordClick={handleWordClick}
          onColumnsChange={setSelectedColumns}
          className="w-full"
        />
      </div>

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

      {/* Technical Details */}
      <div className="bg-gray-900 text-white rounded-lg p-8">
        <div className="flex items-center gap-3 mb-6">
          <Code className="h-6 w-6" />
          <h2 className="text-2xl font-semibold">Technical Implementation</h2>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div>
            <h3 className="text-lg font-semibold mb-4 text-blue-300">
              Frontend Stack
            </h3>
            <ul className="space-y-2 text-gray-300">
              <li>• Next.js 14 with TypeScript</li>
              <li>• Framer Motion for animations</li>
              <li>• Tailwind CSS for styling</li>
              <li>• SVG-based word cloud rendering</li>
              <li>• Canvas API for image export</li>
              <li>• WebSocket for real-time updates</li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold mb-4 text-green-300">
              Analysis Features
            </h3>
            <ul className="space-y-2 text-gray-300">
              <li>• NLTK sentiment analysis</li>
              <li>• spaCy entity recognition</li>
              <li>• LDA topic modeling</li>
              <li>• TF-IDF keyword extraction</li>
              <li>• Custom collision detection</li>
              <li>• Spiral positioning algorithm</li>
            </ul>
          </div>
        </div>

        <div className="mt-8 p-4 bg-gray-800 rounded-lg">
          <h4 className="font-semibold mb-2 text-yellow-300">Usage Example:</h4>
          <pre className="text-sm text-gray-300 overflow-x-auto">
{`<SimpleWordCloud
  datasetId="${datasetId}"
  mode="${selectedMode}"
  selectedColumns={${JSON.stringify(selectedColumns)}}
  showColumnFilter={true}
  onWordClick={(word, data) => console.log(word, data)}
  onColumnsChange={setSelectedColumns}
/>`}
          </pre>
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
            Selected Word: "{selectedWord}"
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

      {/* Call to Action */}
      <div className="bg-gradient-to-r from-primary-600 to-accent-600 text-white rounded-lg p-8 text-center">
        <h2 className="text-2xl font-bold mb-4">
          Upload More Datasets
        </h2>
        <p className="text-xl mb-6 opacity-90">
          Analyze additional CSV datasets with the same powerful word cloud and column filtering features.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/upload"
            className="px-8 py-3 bg-white text-primary-600 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
          >
            Upload Dataset
          </Link>
          <Link
            href="/dashboard"
            className="px-8 py-3 border-2 border-white text-white rounded-lg font-semibold hover:bg-white hover:text-primary-600 transition-colors"
          >
            View Dashboard
          </Link>
        </div>
      </div>
      </div>
    </div>
  );
}
