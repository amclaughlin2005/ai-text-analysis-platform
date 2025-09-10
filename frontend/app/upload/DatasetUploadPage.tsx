'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Database, List, Bug, Sparkles } from 'lucide-react';
import DatasetUpload from '@/components/datasets/DatasetUpload';
import DatasetList from '@/components/datasets/DatasetList';
import UploadProgress from '@/components/datasets/UploadProgress';
import ConnectionTest from '@/components/debug/ConnectionTest';
import FlexibleDataUpload from '@/components/datasets/FlexibleDataUpload';
import { Dataset } from '@/lib/types';

type ViewMode = 'upload' | 'flexible' | 'progress' | 'list' | 'debug';

export default function DatasetUploadPage() {
  const [currentView, setCurrentView] = useState<ViewMode>('upload');
  const [uploadingJobId, setUploadingJobId] = useState<string | null>(null);
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);


  const handleUploadComplete = (datasetId: string) => {
    console.log('Upload completed for dataset:', datasetId);
    setUploadingJobId(null);
    setCurrentView('list');
  };

  const handleUploadError = (error: string) => {
    console.error('Upload error:', error);
    setUploadingJobId(null);
    setCurrentView('upload');
  };

  const handleDatasetSelect = (dataset: Dataset) => {
    setSelectedDataset(dataset);
    console.log('Dataset selected:', dataset.name);
  };

  const handleDatasetDelete = (datasetId: string) => {
    if (selectedDataset?.id === datasetId) {
      setSelectedDataset(null);
    }
  };

  const ViewSelector = () => (
    <div className="flex items-center gap-2 mb-6">
      <button
        onClick={() => setCurrentView('upload')}
        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
          currentView === 'upload'
            ? 'bg-primary-100 text-primary-700'
            : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
        }`}
      >
        <Upload className="h-4 w-4" />
        Upload
      </button>

      <button
        onClick={() => setCurrentView('flexible')}
        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
          currentView === 'flexible'
            ? 'bg-blue-100 text-blue-700'
            : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
        }`}
      >
        <Sparkles className="h-4 w-4" />
        Flexible Upload
      </button>
      
      <button
        onClick={() => setCurrentView('list')}
        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
          currentView === 'list'
            ? 'bg-primary-100 text-primary-700'
            : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
        }`}
      >
        <List className="h-4 w-4" />
        My Datasets
      </button>
      
      <button
        onClick={() => setCurrentView('debug')}
        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
          currentView === 'debug'
            ? 'bg-amber-100 text-amber-700'
            : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
        }`}
      >
        <Bug className="h-4 w-4" />
        Debug
      </button>
    </div>
  );

  return (
    <div className="bg-gray-50 min-h-full">
      <div className="max-w-6xl mx-auto px-4 py-8">
        
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Dataset Management
          </h1>
          <p className="text-lg text-gray-600">
            Upload and manage datasets for AI-powered analysis - supports CSV Q&A format and flexible JSON/CSV with any structure
          </p>
        </div>

        {/* View Selector */}
        <ViewSelector />

        {/* Content */}
        <div className="space-y-6">
          <AnimatePresence mode="wait">
            {currentView === 'upload' && (
              <motion.div
                key="upload"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3 }}
              >
                <div className="bg-white border border-gray-200 rounded-xl p-6">
                  <div className="flex items-center gap-2 mb-6">
                    <Upload className="h-5 w-5 text-primary-600" />
                    <h2 className="text-xl font-semibold text-gray-900">Upload New Dataset</h2>
                  </div>
                  
                  <DatasetUpload
                    onUploadComplete={handleUploadComplete}
                    onUploadProgress={(progress) => console.log('Upload progress:', progress)}
                  />
                </div>
              </motion.div>
            )}

            {currentView === 'flexible' && (
              <motion.div
                key="flexible"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3 }}
              >
                <FlexibleDataUpload
                  onUploadComplete={(datasetId, schema) => {
                    console.log('Flexible upload completed:', { datasetId, schema });
                    setCurrentView('list');
                  }}
                />
              </motion.div>
            )}

            {currentView === 'progress' && uploadingJobId && (
              <motion.div
                key="progress"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3 }}
              >
                <UploadProgress
                  jobId={uploadingJobId}
                  onComplete={handleUploadComplete}
                  onError={handleUploadError}
                />
                
                <div className="mt-4 text-center">
                  <button
                    onClick={() => setCurrentView('list')}
                    className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    View Other Datasets
                  </button>
                </div>
              </motion.div>
            )}

            {currentView === 'list' && (
              <motion.div
                key="list"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3 }}
                className="space-y-6"
              >
                <div className="bg-white border border-gray-200 rounded-xl p-6">
                  <div className="flex items-center gap-2 mb-6">
                    <Database className="h-5 w-5 text-primary-600" />
                    <h2 className="text-xl font-semibold text-gray-900">Your Datasets</h2>
                  </div>
                  
                  <DatasetList
                    onDatasetSelect={handleDatasetSelect}
                    onDatasetDelete={handleDatasetDelete}
                  />
                </div>
                
                {/* Quick Upload Button */}
                <div className="text-center">
                  <button
                    onClick={() => setCurrentView('upload')}
                    className="flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors mx-auto"
                  >
                    <Upload className="h-4 w-4" />
                    Upload New Dataset
                  </button>
                </div>
              </motion.div>
            )}

            {currentView === 'debug' && (
              <motion.div
                key="debug"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3 }}
              >
                <ConnectionTest />
                
                <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <h4 className="font-medium text-yellow-900 mb-2">Troubleshooting Upload Issues</h4>
                  <div className="text-sm text-yellow-700 space-y-1">
                    <p>• If tests fail, check that backend server is running on port 8001</p>
                    <p>• If CORS fails, verify the server allows requests from localhost:3000</p>
                    <p>• If upload fails, check browser dev tools (F12) Network tab for errors</p>
                    <p>• Try refreshing the page and retesting</p>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Selected Dataset Info */}
        {selectedDataset && currentView === 'list' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8 bg-primary-50 border border-primary-200 rounded-xl p-6"
          >
            <h3 className="text-lg font-semibold text-primary-900 mb-2">
              Selected: {selectedDataset.name}
            </h3>
            <p className="text-primary-700 mb-4">
              Database-stored dataset ready for analysis
            </p>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-primary-600 font-medium">Questions:</span>
                <span className="ml-2 text-primary-800">
                  {(selectedDataset.questions_count || selectedDataset.total_questions || selectedDataset.total_rows || 0).toLocaleString()}
                </span>
              </div>
              <div>
                <span className="text-primary-600 font-medium">Status:</span>
                <span className="ml-2 text-primary-800 capitalize">
                  {selectedDataset.processing_status || selectedDataset.upload_status || selectedDataset.status || 'unknown'}
                </span>
              </div>
              <div>
                <span className="text-primary-600 font-medium">Quality:</span>
                <span className="ml-2 text-primary-800">
                  {selectedDataset.data_quality_score 
                    ? `${Math.round(selectedDataset.data_quality_score * 100)}%`
                    : 'Not analyzed yet'
                  }
                </span>
              </div>
              <div>
                <span className="text-primary-600 font-medium">Sentiment:</span>
                <span className="ml-2 text-primary-800">
                  {selectedDataset.sentiment_avg 
                    ? selectedDataset.sentiment_avg.toFixed(2)
                    : 'Not analyzed yet'
                  }
                </span>
              </div>
            </div>
            
            <div className="flex gap-3 mt-4">
              <button
                onClick={() => window.open(`/wordcloud?dataset=${selectedDataset.id}`, '_blank')}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm"
              >
                Open Word Cloud
              </button>
              <button
                onClick={() => console.log('View analytics for:', selectedDataset.id)}
                className="px-4 py-2 border border-primary-600 text-primary-600 rounded-lg hover:bg-primary-50 transition-colors text-sm"
              >
                View Analytics
              </button>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
