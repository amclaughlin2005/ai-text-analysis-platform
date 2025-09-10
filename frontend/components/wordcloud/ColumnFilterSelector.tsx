'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Filter, 
  CheckSquare, 
  Square, 
  Eye, 
  Info,
  MessageSquare,
  Clock,
  Database,
  User,
  Hash,
  RotateCcw
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface ColumnInfo {
  index: number;
  name: string;
  type: 'questions' | 'responses' | 'metadata';
  description: string;
  sample_values: string[];
  recommended_for_wordcloud: boolean;
  total_non_empty: number;
}

interface ColumnFilterSelectorProps {
  datasetId: string;
  selectedColumns: number[];
  onColumnsChange: (columns: number[]) => void;
  className?: string;
}

const PRESET_FILTERS = [
  {
    id: 'questions_only',
    label: 'Questions Only',
    description: 'Analyze only user questions and queries',
    icon: MessageSquare,
    columns: [1] // original_question column
  },
  {
    id: 'responses_only', 
    label: 'Responses Only',
    description: 'Analyze only AI/agent responses',
    icon: Eye,
    columns: [2] // ai_response column
  },
  {
    id: 'questions_and_responses',
    label: 'Q&A Combined',
    description: 'Analyze both questions and responses (recommended)',
    icon: MessageSquare,
    columns: [1, 2] // both text columns
  },
  {
    id: 'text_only',
    label: 'Text Content Only', 
    description: 'Exclude metadata, focus on content',
    icon: Database,
    columns: [1, 2] // same as Q&A for legal dataset
  }
];

export default function ColumnFilterSelector({
  datasetId,
  selectedColumns,
  onColumnsChange,
  className
}: ColumnFilterSelectorProps) {
  const [columns, setColumns] = useState<ColumnInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  // Fetch column information
  useEffect(() => {
    const fetchColumns = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // For legal dataset, use the dedicated API
        const isLegalDataset = datasetId === '06a8437a-27e8-412f-a530-6cb04f7b6dc9';
        
        if (isLegalDataset) {
          // Try the production API first, fallback to localhost for development
          const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://ai-text-analysis-production.up.railway.app';
          
          try {
            const response = await fetch(`${API_BASE_URL}/api/datasets/${datasetId}/columns`);
            if (response.ok) {
              const data = await response.json();
              console.log('📋 Column info loaded from production API:', data);
              if (data.success && data.columns) {
                setColumns(data.columns);
                return;
              }
            }
          } catch (prodError) {
            console.log('Production API not available, trying localhost...');
          }
          
          // Fallback to localhost for development
          try {
            const response = await fetch('http://localhost:8002/columns');
            if (response.ok) {
              const data = await response.json();
              console.log('📋 Column info loaded from localhost:', data);
              if (data.columns) {
                setColumns(data.columns);
                return;
              }
            }
          } catch (localError) {
            console.log('Localhost also not available, using fallback data');
          }
          
          // Final fallback - use hardcoded legal dataset structure
          setColumns([
            {
              index: 0,
              name: 'csv_row_number',
              type: 'metadata',
              description: 'Row number from original CSV',
              sample_values: ['1', '2', '3'],
              recommended_for_wordcloud: false,
              total_non_empty: 84
            },
            {
              index: 1,
              name: 'original_question',
              type: 'questions',
              description: 'Legal questions and queries from users',
              sample_values: ['Please draft a cross-examination...', 'What evidence supports...', 'How should we approach...'],
              recommended_for_wordcloud: true,
              total_non_empty: 84
            },
            {
              index: 2,
              name: 'ai_response',
              type: 'responses',
              description: 'AI-generated legal analysis and responses',
              sample_values: ['Based on the deposition transcript...', 'The court found evidence...', 'Legal precedent suggests...'],
              recommended_for_wordcloud: true,
              total_non_empty: 84
            }
          ]);
        } else {
          // For other datasets, create generic column info
          setColumns([
            {
              index: 0,
              name: 'question', 
              type: 'questions',
              description: 'User questions and queries',
              sample_values: ['How do I...', 'What is...', 'Why does...'],
              recommended_for_wordcloud: true,
              total_non_empty: 100
            },
            {
              index: 1,
              name: 'response',
              type: 'responses', 
              description: 'AI/agent responses',
              sample_values: ['You can...', 'This is...', 'Try this...'],
              recommended_for_wordcloud: true,
              total_non_empty: 100
            }
          ]);
        }
        
      } catch (err) {
        console.error('Failed to fetch columns:', err);
        setError(err instanceof Error ? err.message : 'Failed to load columns');
      } finally {
        setLoading(false);
      }
    };

    fetchColumns();
  }, [datasetId]);

  const handleColumnToggle = (columnIndex: number) => {
    const newColumns = selectedColumns.includes(columnIndex)
      ? selectedColumns.filter(c => c !== columnIndex)
      : [...selectedColumns, columnIndex];
    
    onColumnsChange(newColumns);
  };

  const handlePresetSelect = (preset: typeof PRESET_FILTERS[0]) => {
    onColumnsChange(preset.columns);
  };

  const getColumnIcon = (type: string) => {
    switch (type) {
      case 'questions':
        return <MessageSquare className="h-4 w-4 text-blue-500" />;
      case 'responses':
        return <Eye className="h-4 w-4 text-green-500" />;
      case 'metadata':
        return <Hash className="h-4 w-4 text-gray-500" />;
      default:
        return <Database className="h-4 w-4 text-gray-500" />;
    }
  };

  if (loading) {
    return (
      <div className={cn("bg-white border border-gray-200 rounded-lg p-6", className)}>
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/3"></div>
          <div className="space-y-2">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-100 rounded w-3/4"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={cn("bg-red-50 border border-red-200 rounded-lg p-6", className)}>
        <div className="text-red-800">
          <p className="font-medium">Failed to load column information</p>
          <p className="text-sm mt-1">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={cn("bg-white border border-gray-200 rounded-lg", className)}>
      {/* Header */}
      <div className="p-4 border-b bg-gray-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Filter className="h-5 w-5 text-primary-600" />
            <h3 className="text-lg font-semibold text-gray-900">Column Filter</h3>
          </div>
          
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="flex items-center gap-2 px-3 py-1 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Info className="h-4 w-4" />
            {showDetails ? 'Hide' : 'Show'} Details
          </button>
        </div>
        
        <p className="text-sm text-gray-600 mt-1">
          Choose which columns to include in word cloud analysis
        </p>
      </div>

      <div className="p-6 space-y-6">
        {/* Preset Filters */}
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-3">Quick Presets</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {PRESET_FILTERS.map((preset) => {
              const Icon = preset.icon;
              const isActive = JSON.stringify([...selectedColumns].sort()) === JSON.stringify([...preset.columns].sort());
              
              return (
                <button
                  key={preset.id}
                  onClick={() => handlePresetSelect(preset)}
                  className={cn(
                    "p-4 text-left rounded-lg border-2 transition-all duration-200",
                    isActive
                      ? "border-primary-500 bg-primary-50 text-primary-900"
                      : "border-gray-200 hover:border-gray-300 hover:shadow-sm"
                  )}
                >
                  <div className="flex items-center gap-3 mb-2">
                    <Icon className={cn("h-4 w-4", isActive ? "text-primary-600" : "text-gray-500")} />
                    <span className="font-medium text-sm">{preset.label}</span>
                    {isActive && (
                      <div className="ml-auto">
                        <div className="h-2 w-2 bg-primary-600 rounded-full"></div>
                      </div>
                    )}
                  </div>
                  <p className="text-xs text-gray-600">{preset.description}</p>
                  <div className="text-xs text-gray-500 mt-1">
                    Columns: {preset.columns.join(', ')}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Individual Column Selection */}
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-3">
            Individual Columns ({selectedColumns.length} selected)
          </h4>
          
          <div className="space-y-3">
            {columns.map((column) => {
              const isSelected = selectedColumns.includes(column.index);
              
              return (
                <div key={column.index}>
                  <label
                    className={cn(
                      "flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-all",
                      isSelected 
                        ? "border-primary-200 bg-primary-50" 
                        : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                    )}
                  >
                    <div className="flex items-center pt-1">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => handleColumnToggle(column.index)}
                        className="sr-only"
                      />
                      {isSelected ? (
                        <CheckSquare className="h-5 w-5 text-primary-600" />
                      ) : (
                        <Square className="h-5 w-5 text-gray-400" />
                      )}
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        {getColumnIcon(column.type)}
                        <span className="font-medium text-gray-900">{column.name}</span>
                        <span className="text-xs text-gray-500">
                          (Column {column.index})
                        </span>
                        {column.recommended_for_wordcloud && (
                          <span className="bg-green-100 text-green-700 text-xs px-2 py-0.5 rounded">
                            Recommended
                          </span>
                        )}
                      </div>
                      
                      <p className="text-sm text-gray-600">{column.description}</p>
                      
                      <div className="text-xs text-gray-500 mt-1">
                        {column.total_non_empty.toLocaleString()} entries with data
                      </div>
                    </div>
                  </label>

                  {/* Sample Data */}
                  <AnimatePresence>
                    {showDetails && isSelected && column.sample_values.length > 0 && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="ml-8 mt-2 p-3 bg-gray-50 border border-gray-200 rounded"
                      >
                        <p className="text-xs font-medium text-gray-700 mb-2">Sample Values:</p>
                        <div className="space-y-1">
                          {column.sample_values.map((value, index) => (
                            <div key={index} className="text-xs text-gray-600 truncate">
                              {index + 1}. {value}
                            </div>
                          ))}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              );
            })}
          </div>
        </div>

        {/* Selection Summary */}
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Filter className="h-4 w-4 text-blue-600" />
            <span className="font-medium text-blue-900">
              Current Selection ({selectedColumns.length} columns)
            </span>
          </div>
          
          {selectedColumns.length > 0 ? (
            <div className="space-y-2">
              <div className="flex flex-wrap gap-2">
                {selectedColumns.map(colIndex => {
                  const column = columns.find(c => c.index === colIndex);
                  if (!column) return null;
                  
                  return (
                    <span
                      key={colIndex}
                      className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
                    >
                      {getColumnIcon(column.type)}
                      {column.name}
                    </span>
                  );
                })}
              </div>
              
              <p className="text-xs text-blue-700">
                Word cloud will analyze text from these {selectedColumns.length} column(s).
              </p>
            </div>
          ) : (
            <p className="text-sm text-blue-700">
              No columns selected. Choose at least one column to generate word cloud.
            </p>
          )}
          
          {selectedColumns.length > 0 && (
            <button
              onClick={() => onColumnsChange([])}
              className="mt-2 flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800"
            >
              <RotateCcw className="h-3 w-3" />
              Clear Selection
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
