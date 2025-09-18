'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Database, 
  MoreHorizontal, 
  Eye, 
  Download, 
  Trash2,
  RefreshCw,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Cloud,
  Plus,
  BarChart3,
  ExternalLink,
  Square,
  CheckSquare,
  Search,
  Filter,
  Archive,
  Merge
} from 'lucide-react';
import { Dataset, DatasetStatus } from '@/lib/types';
import { cn, formatFileSize, formatRelativeTime, getStatusColor } from '@/lib/utils';
import toast from 'react-hot-toast';

interface DatasetListProps {
  onDatasetSelect?: (dataset: Dataset) => void;
  onDatasetDelete?: (datasetId: string) => void;
  className?: string;
}

interface DatasetListState {
  datasets: Dataset[];
  loading: boolean;
  error: string | null;
  selectedDataset: string | null;
  actionMenuOpen: string | null; // ID of dataset with open action menu
  bulkSelectedDatasets: Set<string>; // IDs of datasets selected for bulk operations
  bulkMode: boolean; // Whether bulk selection mode is active
}

export default function DatasetList({
  onDatasetSelect,
  onDatasetDelete,
  className
}: DatasetListProps) {
  const [state, setState] = useState<DatasetListState>({
    datasets: [],
    loading: true,
    error: null,
    selectedDataset: null,
    actionMenuOpen: null,
    bulkSelectedDatasets: new Set<string>(),
    bulkMode: false
  });
  
  // Debug: Log state changes (TODO: Remove after action menu is working)
  console.log('DatasetList state:', { actionMenuOpen: state.actionMenuOpen, bulkMode: state.bulkMode, selectedCount: state.bulkSelectedDatasets.size });

  // Fetch datasets from backend
  const fetchDatasets = async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://ai-text-analysis-production.up.railway.app';
      const response = await fetch(`${API_BASE_URL}/api/datasets`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch datasets: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Datasets fetched:', data);
      
      // Handle both direct array and nested data structure
      const datasets = Array.isArray(data) ? data : (data.data || data.datasets || []);
      
      setState(prev => ({
        ...prev,
        datasets: datasets,
        loading: false
      }));
      
    } catch (error) {
      console.error('Failed to fetch datasets:', error);
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to load datasets',
        loading: false,
        // Use mock data as fallback
        datasets: generateMockDatasets()
      }));
      toast.error('Using mock data - backend connection needed for real datasets');
    }
  };

  // Generate mock datasets for development
  const generateMockDatasets = (): Dataset[] => [
    {
      id: 'demo-dataset-1',
      user_id: 'demo-user',
      name: 'Customer Support Q1 2024',
      description: 'Customer support conversations from Q1 2024',
      original_filename: 'support_q1_2024.csv',
      file_size: 2456789,
      status: 'completed' as DatasetStatus,
      progress_percentage: 100,
      status_message: 'Analysis completed successfully',
      total_questions: 1247,
      processed_questions: 1247,
      valid_questions: 1198,
      invalid_questions: 49,
      sentiment_avg: 0.65,
      sentiment_distribution: { positive: 0.6, neutral: 0.3, negative: 0.1 },
      top_topics: [
        { topic: 'billing issues', score: 0.85 },
        { topic: 'technical support', score: 0.78 }
      ],
      top_entities: [
        { entity: 'Support Team', count: 45 },
        { entity: 'Product X', count: 32 }
      ],
      top_keywords: [
        { keyword: 'help', score: 0.92 },
        { keyword: 'issue', score: 0.88 }
      ],
      avg_question_length: 85.5,
      avg_response_length: 156.2,
      avg_complexity_score: 0.42,
      data_quality_score: 0.86,
      organizations_count: 12,
      organization_names: ['Acme Corp', 'Tech Solutions', 'Global Industries'],
      is_public: false,
      created_at: '2024-01-15T10:30:00Z',
      updated_at: '2024-01-15T12:45:00Z',
      processing_started_at: '2024-01-15T10:35:00Z',
      processing_completed_at: '2024-01-15T12:45:00Z'
    },
    {
      id: 'demo-dataset-2',
      user_id: 'demo-user',
      name: 'Feature Requests Analysis',
      description: 'User feature requests and feedback',
      original_filename: 'feature_requests.csv',
      file_size: 892345,
      status: 'processing' as DatasetStatus,
      progress_percentage: 67,
      status_message: 'Analyzing sentiment and topics...',
      total_questions: 589,
      processed_questions: 395,
      valid_questions: 380,
      invalid_questions: 15,
      sentiment_avg: 0.32,
      sentiment_distribution: null,
      top_topics: null,
      top_entities: null,
      top_keywords: null,
      avg_question_length: null,
      avg_response_length: null,
      avg_complexity_score: null,
      data_quality_score: null,
      organizations_count: 0,
      organization_names: null,
      is_public: false,
      created_at: '2024-01-16T14:20:00Z',
      updated_at: '2024-01-16T14:25:00Z',
      processing_started_at: '2024-01-16T14:22:00Z',
      processing_completed_at: null
    }
  ];

  // Refresh datasets
  const refreshDatasets = () => {
    fetchDatasets();
  };

  // Handle dataset selection
  const handleDatasetClick = (dataset: Dataset) => {
    setState(prev => ({
      ...prev,
      selectedDataset: prev.selectedDataset === dataset.id ? null : dataset.id
    }));
    
    if (onDatasetSelect) {
      onDatasetSelect(dataset);
    }
  };

  // Handle action menu toggle
  const toggleActionMenu = (datasetId: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    console.log('Toggling action menu for dataset:', datasetId);
    setState(prev => ({
      ...prev,
      actionMenuOpen: prev.actionMenuOpen === datasetId ? null : datasetId
    }));
  };

  // Close action menu when clicking outside
  const closeActionMenu = (e?: React.MouseEvent) => {
    // Don't close if clicking on action menu button or dropdown
    if (e && e.target instanceof Element) {
      if (e.target.closest('[data-action-menu]')) {
        return;
      }
    }
    setState(prev => ({ ...prev, actionMenuOpen: null }));
  };

  // Dataset action handlers
  const handleViewDataset = (dataset: Dataset, e: React.MouseEvent) => {
    e.stopPropagation();
    window.open(`/dataset/${dataset.id}`, '_blank');
    closeActionMenu();
  };

  const handleWordCloud = (dataset: Dataset, e: React.MouseEvent) => {
    e.stopPropagation();
    window.open(`/wordcloud?dataset=${dataset.id}`, '_blank');
    closeActionMenu();
  };

  const handleAppendData = (dataset: Dataset, e: React.MouseEvent) => {
    e.stopPropagation();
    window.location.href = `/upload?append=${dataset.id}&name=${encodeURIComponent(dataset.name)}`;
    closeActionMenu();
  };

  const handleAnalytics = (dataset: Dataset, e: React.MouseEvent) => {
    e.stopPropagation();
    toast('Analytics feature coming soon!', {
      icon: '📊',
      duration: 3000,
    });
    closeActionMenu();
  };

  // Bulk operation handlers
  const toggleBulkMode = () => {
    setState(prev => ({
      ...prev,
      bulkMode: !prev.bulkMode,
      bulkSelectedDatasets: new Set<string>(), // Clear selections when toggling mode
      actionMenuOpen: null // Close any open action menus
    }));
  };

  const toggleDatasetSelection = (datasetId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setState(prev => {
      const newSelected = new Set(prev.bulkSelectedDatasets);
      if (newSelected.has(datasetId)) {
        newSelected.delete(datasetId);
      } else {
        newSelected.add(datasetId);
      }
      return {
        ...prev,
        bulkSelectedDatasets: newSelected
      };
    });
  };

  const selectAllDatasets = () => {
    setState(prev => ({
      ...prev,
      bulkSelectedDatasets: new Set(prev.datasets.map(d => d.id))
    }));
  };

  const clearAllSelections = () => {
    setState(prev => ({
      ...prev,
      bulkSelectedDatasets: new Set<string>()
    }));
  };

  const handleBulkDelete = async () => {
    const selectedCount = state.bulkSelectedDatasets.size;
    if (selectedCount === 0) {
      toast.error('No datasets selected');
      return;
    }

    if (!confirm(`Are you sure you want to delete ${selectedCount} datasets? This action cannot be undone.`)) {
      return;
    }

    toast('Bulk delete functionality coming soon!', {
      icon: '🗑️',
      duration: 3000,
    });
  };

  const handleBulkExport = () => {
    const selectedCount = state.bulkSelectedDatasets.size;
    if (selectedCount === 0) {
      toast.error('No datasets selected');
      return;
    }

    toast('Bulk export functionality coming soon!', {
      icon: '📦',
      duration: 3000,
    });
  };

  const handleBulkMerge = async () => {
    const selectedCount = state.bulkSelectedDatasets.size;
    if (selectedCount < 2) {
      toast.error('Select at least 2 datasets to merge');
      return;
    }

    const selectedDatasets = state.datasets.filter(d => state.bulkSelectedDatasets.has(d.id));
    const totalQuestions = selectedDatasets.reduce((sum, d) => sum + (d.questions_count || d.total_questions || 0), 0);
    
    const mergedName = prompt(`Enter name for merged dataset (${selectedCount} datasets, ${totalQuestions} questions):`);
    if (!mergedName) return;

    const deleteSource = confirm('Delete source datasets after merge? (This cannot be undone)');

    try {
      setState(prev => ({ ...prev, loading: true }));
      
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://ai-text-analysis-production.up.railway.app';
      
      const formData = new FormData();
      Array.from(state.bulkSelectedDatasets).forEach(id => {
        formData.append('source_dataset_ids', id);
      });
      formData.append('target_name', mergedName);
      formData.append('delete_source', deleteSource.toString());
      
      const response = await fetch(`${API_BASE_URL}/api/datasets/merge`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Merge failed: ${response.status}`);
      }

      const result = await response.json();
      
      toast.success(`Successfully merged ${result.total_source_datasets} datasets into "${result.target_dataset_name}"!`, {
        duration: 5000
      });

      // Refresh the dataset list and clear selections
      await fetchDatasets();
      setState(prev => ({ 
        ...prev, 
        bulkSelectedDatasets: new Set<string>(),
        bulkMode: false
      }));

    } catch (error) {
      console.error('Merge failed:', error);
      toast.error(`Merge failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setState(prev => ({ ...prev, loading: false }));
    }
  };

  // Handle dataset deletion
  const handleDelete = async (datasetId: string, datasetName: string) => {
    if (!confirm(`Are you sure you want to delete "${datasetName}"? This action cannot be undone.`)) {
      return;
    }

    try {
            const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://ai-text-analysis-production.up.railway.app';
      const response = await fetch(`${API_BASE_URL}/api/datasets/${datasetId}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error('Delete failed');
      }

      toast.success(`Dataset "${datasetName}" deleted successfully`);
      
      // Remove from local state
      setState(prev => ({
        ...prev,
        datasets: prev.datasets.filter(d => d.id !== datasetId)
      }));
      
      if (onDatasetDelete) {
        onDatasetDelete(datasetId);
      }

    } catch (error) {
      console.error('Delete failed:', error);
      toast.error('Failed to delete dataset');
    }
  };

  // Get status icon
  const getStatusIcon = (status: DatasetStatus) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'processing':
      case 'uploading':
      case 'validating':
        return <RefreshCw className="h-5 w-5 text-blue-500 animate-spin" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'cancelled':
        return <AlertCircle className="h-5 w-5 text-gray-500" />;
      default:
        return <Clock className="h-5 w-5 text-gray-500" />;
    }
  };

  // Load datasets on mount
  useEffect(() => {
    fetchDatasets();
  }, []);

  if (state.loading) {
    return (
      <div className={cn("space-y-4", className)}>
        {[...Array(3)].map((_, index) => (
          <div key={index} className="bg-white border border-gray-200 rounded-xl p-6 animate-pulse">
            <div className="flex items-center justify-between mb-4">
              <div className="h-6 bg-gray-300 rounded w-48"></div>
              <div className="h-8 bg-gray-300 rounded w-16"></div>
            </div>
            <div className="space-y-2">
              <div className="h-4 bg-gray-200 rounded w-32"></div>
              <div className="h-4 bg-gray-200 rounded w-full"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div 
      className={cn("space-y-4", className)}
      onClick={closeActionMenu}
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h3 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
            <Database className="h-5 w-5" />
            Datasets ({state.datasets.length})
          </h3>
          {state.bulkSelectedDatasets.size > 0 && (
            <span className="text-sm text-primary-600 font-medium">
              {state.bulkSelectedDatasets.size} selected
            </span>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          {state.bulkMode && (
            <>
              <button
                onClick={selectAllDatasets}
                className="text-sm text-primary-600 hover:text-primary-700 px-2 py-1 rounded"
              >
                Select All
              </button>
              <button
                onClick={clearAllSelections}
                className="text-sm text-gray-600 hover:text-gray-700 px-2 py-1 rounded"
              >
                Clear
              </button>
            </>
          )}
          <button
            onClick={toggleBulkMode}
            className={cn(
              "flex items-center gap-2 px-3 py-2 text-sm rounded-lg transition-colors",
              state.bulkMode 
                ? "bg-primary-100 text-primary-700 hover:bg-primary-200" 
                : "text-gray-600 hover:text-gray-800 hover:bg-gray-100"
            )}
          >
            <CheckSquare className="h-4 w-4" />
            {state.bulkMode ? 'Exit Select' : 'Select'}
          </button>
          <button
            onClick={refreshDatasets}
            disabled={state.loading}
            className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
          >
            <RefreshCw className={cn("h-4 w-4", state.loading && "animate-spin")} />
            Refresh
          </button>
        </div>
      </div>

      {/* Bulk Actions Toolbar */}
      {state.bulkMode && state.bulkSelectedDatasets.size > 0 && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-primary-50 border border-primary-200 rounded-lg p-4"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckSquare className="h-5 w-5 text-primary-600" />
              <span className="text-sm font-medium text-primary-900">
                {state.bulkSelectedDatasets.size} dataset{state.bulkSelectedDatasets.size !== 1 ? 's' : ''} selected
              </span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handleBulkExport}
                className="flex items-center gap-2 px-3 py-2 text-sm text-primary-700 hover:text-primary-800 hover:bg-primary-100 rounded-lg transition-colors"
              >
                <Download className="h-4 w-4" />
                Export
              </button>
              <button
                onClick={handleBulkMerge}
                className="flex items-center gap-2 px-3 py-2 text-sm text-primary-700 hover:text-primary-800 hover:bg-primary-100 rounded-lg transition-colors"
              >
                <Merge className="h-4 w-4" />
                Merge
              </button>
              <button
                onClick={handleBulkDelete}
                className="flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
              >
                <Trash2 className="h-4 w-4" />
                Delete
              </button>
            </div>
          </div>
        </motion.div>
      )}

      {/* Error State */}
      {state.error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-red-800">
            <AlertCircle className="h-4 w-4" />
            <span className="font-medium">Error loading datasets</span>
          </div>
          <p className="text-red-600 text-sm mt-1">{state.error}</p>
          <button
            onClick={refreshDatasets}
            className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm"
          >
            Retry
          </button>
        </div>
      )}

      {/* Dataset List */}
      <div className="space-y-4">
        <AnimatePresence>
          {state.datasets.map((dataset, index) => {
            const isSelected = state.selectedDataset === dataset.id;
            const isBulkSelected = state.bulkSelectedDatasets.has(dataset.id);
            
            return (
              <motion.div
                key={dataset.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ delay: index * 0.1 }}
                className={cn(
                  "bg-white border rounded-xl p-6 cursor-pointer transition-all duration-200",
                  state.bulkMode && isBulkSelected 
                    ? "border-primary-300 ring-2 ring-primary-100 bg-primary-25" 
                    : isSelected 
                      ? "border-primary-300 ring-2 ring-primary-100" 
                      : "border-gray-200 hover:border-gray-300 hover:shadow-sm"
                )}
                onClick={() => state.bulkMode ? toggleDatasetSelection(dataset.id, {} as React.MouseEvent) : handleDatasetClick(dataset)}
              >
                {/* Header */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    {state.bulkMode && (
                      <button
                        onClick={(e) => toggleDatasetSelection(dataset.id, e)}
                        className="flex items-center justify-center w-5 h-5 transition-colors"
                      >
                        {isBulkSelected ? (
                          <CheckSquare className="h-5 w-5 text-primary-600" />
                        ) : (
                          <Square className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                        )}
                      </button>
                    )}
                    {getStatusIcon((dataset.processing_status || dataset.upload_status || 'failed') as DatasetStatus)}
                    <div>
                      <h4 className="text-lg font-semibold text-gray-900">{dataset.name}</h4>
                      <p className="text-sm text-gray-600">{dataset.filename || dataset.original_filename}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    {(() => {
                      const currentStatus = dataset.processing_status || dataset.upload_status || dataset.status || 'unknown';
                      return (
                        <span
                          className="px-3 py-1 text-xs font-medium rounded-full"
                          style={{ 
                            backgroundColor: `${getStatusColor(currentStatus)}20`,
                            color: getStatusColor(currentStatus)
                          }}
                        >
                          {currentStatus.charAt(0).toUpperCase() + currentStatus.slice(1)}
                        </span>
                      );
                    })()}
                    
                    {!state.bulkMode && (
                      <div className="relative" data-action-menu>
                        <button
                          onClick={(e) => toggleActionMenu(dataset.id, e)}
                          className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                          data-action-menu
                        >
                          <MoreHorizontal className="h-4 w-4" />
                        </button>
                      
                      {state.actionMenuOpen === dataset.id && (
                        <div 
                          className="absolute right-0 top-10 w-48 bg-white rounded-lg shadow-lg border z-50"
                          data-action-menu
                        >
                          <div className="py-1">
                            <button
                              onClick={(e) => handleViewDataset(dataset, e)}
                              className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                            >
                              <Eye className="h-4 w-4 mr-3" />
                              View Details
                            </button>
                            <button
                              onClick={(e) => handleWordCloud(dataset, e)}
                              className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                            >
                              <Cloud className="h-4 w-4 mr-3" />
                              Word Cloud
                            </button>
                            <button
                              onClick={(e) => handleAppendData(dataset, e)}
                              className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                            >
                              <Plus className="h-4 w-4 mr-3" />
                              Add More Data
                            </button>
                            <button
                              onClick={(e) => handleAnalytics(dataset, e)}
                              className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                            >
                              <BarChart3 className="h-4 w-4 mr-3" />
                              Analytics
                            </button>
                            <div className="border-t border-gray-100 my-1"></div>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDelete(dataset.id, dataset.name);
                                closeActionMenu();
                              }}
                              className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                            >
                              <Trash2 className="h-4 w-4 mr-3" />
                              Delete
                            </button>
                          </div>
                        </div>
                      )}
                      </div>
                    )}
                  </div>
                </div>

                {/* Progress Bar */}
                {(dataset.processing_status === 'processing' || dataset.upload_status === 'processing') && dataset.progress_percentage && (
                  <div className="mb-4">
                    <div className="flex justify-between text-sm text-gray-600 mb-2">
                      <span>{dataset.status_message || 'Processing...'}</span>
                      <span>{Math.round(dataset.progress_percentage || 0)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${dataset.progress_percentage || 0}%` }}
                      />
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>{dataset.processed_questions || 0} / {dataset.questions_count || dataset.total_rows || 0} questions</span>
                      <span>{formatRelativeTime(dataset.processing_started_at || dataset.created_at)}</span>
                    </div>
                  </div>
                )}

                {/* Basic Info */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div className="space-y-1">
                    <p className="text-xs text-gray-500 uppercase tracking-wide">Questions</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {(dataset.questions_count || dataset.total_questions || dataset.total_rows || 0).toLocaleString()}
                    </p>
                    {dataset.valid_questions !== (dataset.questions_count || dataset.total_questions) && (
                      <p className="text-xs text-amber-600">
                        {dataset.invalid_questions || 0} invalid
                      </p>
                    )}
                  </div>
                  
                  <div className="space-y-1">
                    <p className="text-xs text-gray-500 uppercase tracking-wide">File Size</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {formatFileSize(dataset.file_size)}
                    </p>
                  </div>
                  
                  <div className="space-y-1">
                    <p className="text-xs text-gray-500 uppercase tracking-wide">Created</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {formatRelativeTime(dataset.created_at)}
                    </p>
                  </div>
                </div>

                {/* Expanded Details */}
                <AnimatePresence>
                  {isSelected && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="border-t border-gray-200 pt-4 space-y-4"
                    >
                      {/* Description - Hide for now since database doesn't provide this */}
                      {false && dataset.description && (
                        <div>
                          <p className="text-sm font-medium text-gray-700 mb-1">Description</p>
                          <p className="text-sm text-gray-600">{dataset.description}</p>
                        </div>
                      )}

                      {/* Analysis Summary - Hide for now since database doesn't provide advanced analytics yet */}
                      {false && (dataset.processing_status === 'completed') && (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                          {dataset.sentiment_avg !== null && dataset.sentiment_avg !== undefined && (
                            <div className="bg-blue-50 p-3 rounded-lg">
                              <p className="text-xs text-blue-600 uppercase tracking-wide mb-1">Avg Sentiment</p>
                              <p className="text-xl font-bold text-blue-700">
                                {dataset.sentiment_avg?.toFixed(2) || '0.00'}
                              </p>
                            </div>
                          )}
                          
                          {dataset.data_quality_score !== null && dataset.data_quality_score !== undefined && (
                            <div className="bg-green-50 p-3 rounded-lg">
                              <p className="text-xs text-green-600 uppercase tracking-wide mb-1">Quality Score</p>
                              <p className="text-xl font-bold text-green-700">
                                {Math.round((dataset.data_quality_score || 0) * 100)}%
                              </p>
                            </div>
                          )}

                          {(dataset.organizations_count || 0) > 0 && (
                            <div className="bg-purple-50 p-3 rounded-lg">
                              <p className="text-xs text-purple-600 uppercase tracking-wide mb-1">Organizations</p>
                              <p className="text-xl font-bold text-purple-700">
                                {dataset.organizations_count}
                              </p>
                            </div>
                          )}

                          {dataset.avg_complexity_score !== null && dataset.avg_complexity_score !== undefined && (
                            <div className="bg-amber-50 p-3 rounded-lg">
                              <p className="text-xs text-amber-600 uppercase tracking-wide mb-1">Complexity</p>
                              <p className="text-xl font-bold text-amber-700">
                                {Math.round((dataset.avg_complexity_score || 0) * 100)}%
                              </p>
                            </div>
                          )}
                        </div>
                      )}

                      {/* Top Topics - Hide for now since database doesn't provide this */}
                      {false && dataset.top_topics && (dataset.top_topics?.length || 0) > 0 && (
                        <div>
                          <p className="text-sm font-medium text-gray-700 mb-2">Top Topics</p>
                          <div className="flex flex-wrap gap-2">
                            {(dataset.top_topics || []).slice(0, 5).map((topic, index) => (
                              <span
                                key={index}
                                className="px-3 py-1 bg-primary-100 text-primary-800 text-xs rounded-full"
                              >
                                {topic.topic} ({(topic.score * 100).toFixed(0)}%)
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Actions */}
                      <div className="flex items-center gap-3 pt-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            window.open(`/dataset/${dataset.id}`, '_blank');
                          }}
                          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm"
                        >
                          <Eye className="h-4 w-4" />
                          View Dataset
                        </button>

                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            // Open dedicated legal word cloud for the legal dataset
                            if (dataset.id === '06a8437a-27e8-412f-a530-6cb04f7b6dc9') {
                              window.open('/legal-wordcloud', '_blank');
                            } else {
                              window.open(`/wordcloud?dataset=${dataset.id}`, '_blank');
                            }
                          }}
                          className="flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm"
                        >
                          <Eye className="h-4 w-4" />
                          {dataset.id === '06a8437a-27e8-412f-a530-6cb04f7b6dc9' ? 'Legal Word Cloud' : 'Word Cloud'}
                        </button>

                        {(dataset.processing_status === 'completed') && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              // Export functionality
                              console.log('Export dataset:', dataset.id);
                            }}
                            className="flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm"
                          >
                            <Download className="h-4 w-4" />
                            Export
                          </button>
                        )}

                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDelete(dataset.id, dataset.name);
                          }}
                          className="flex items-center gap-2 px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors text-sm"
                        >
                          <Trash2 className="h-4 w-4" />
                          Delete
                        </button>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            );
          })}
        </AnimatePresence>

        {/* Empty State */}
        {state.datasets.length === 0 && !state.loading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-12"
          >
            <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
              <Database className="h-8 w-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No datasets uploaded</h3>
            <p className="text-gray-600 mb-4">
              Upload your first CSV file to get started with text analysis.
            </p>
          </motion.div>
        )}
      </div>
    </div>
  );
}
