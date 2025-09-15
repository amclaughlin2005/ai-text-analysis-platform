'use client';

import React, { useState, useEffect } from 'react';
import { Database, ChevronDown, Check, Plus, X } from 'lucide-react';
import { Dataset } from '@/lib/types';

interface DatasetSelectorProps {
  selectedDatasets: string[];
  onDatasetChange: (datasetIds: string[]) => void;
  multiSelect?: boolean;
  className?: string;
  placeholder?: string;
}

export default function DatasetSelector({
  selectedDatasets,
  onDatasetChange,
  multiSelect = false,
  className = '',
  placeholder = 'Select a dataset'
}: DatasetSelectorProps) {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [isOpen, setIsOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch datasets from backend
  const fetchDatasets = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://ai-text-analysis-production.up.railway.app';
      const response = await fetch(`${API_BASE_URL}/api/datasets`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch datasets: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Datasets fetched for selector:', data);
      
      // Handle both direct array and nested data structure
      const datasetsArray = Array.isArray(data) ? data : (data.data || data.datasets || []);
      
      setDatasets(datasetsArray);
      setLoading(false);
      
    } catch (err) {
      console.error('Error fetching datasets:', err);
      setError(err instanceof Error ? err.message : 'Failed to load datasets');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  const handleDatasetToggle = (datasetId: string) => {
    if (multiSelect) {
      if (selectedDatasets.includes(datasetId)) {
        onDatasetChange(selectedDatasets.filter(id => id !== datasetId));
      } else {
        onDatasetChange([...selectedDatasets, datasetId]);
      }
    } else {
      onDatasetChange([datasetId]);
      setIsOpen(false);
    }
  };

  const getSelectedDatasetNames = () => {
    if (selectedDatasets.length === 0) return placeholder;
    
    const names = selectedDatasets.map(id => {
      const dataset = datasets.find(d => d.id === id);
      return dataset ? dataset.name : `Dataset ${id.slice(0, 8)}...`;
    });
    
    if (multiSelect && names.length > 1) {
      return `${names.length} datasets selected`;
    }
    
    return names[0] || placeholder;
  };

  const clearSelection = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDatasetChange([]);
  };

  if (error) {
    return (
      <div className={`p-3 border border-red-200 rounded-lg bg-red-50 ${className}`}>
        <p className="text-red-600 text-sm">Error loading datasets: {error}</p>
        <button 
          onClick={fetchDatasets}
          className="text-red-600 underline text-sm mt-1"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      <div
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between p-3 border border-gray-300 rounded-lg bg-white cursor-pointer hover:border-primary-500 transition-colors"
      >
        <div className="flex items-center space-x-2">
          <Database className="h-4 w-4 text-gray-500" />
          <span className="text-gray-900">
            {loading ? 'Loading datasets...' : getSelectedDatasetNames()}
          </span>
        </div>
        
        <div className="flex items-center space-x-2">
          {selectedDatasets.length > 0 && (
            <button
              onClick={clearSelection}
              className="p-1 hover:bg-gray-100 rounded"
            >
              <X className="h-3 w-3 text-gray-400" />
            </button>
          )}
          <ChevronDown 
            className={`h-4 w-4 text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} 
          />
        </div>
      </div>

      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-300 rounded-lg shadow-lg z-50 max-h-64 overflow-y-auto">
          {loading ? (
            <div className="p-4 text-center text-gray-500">
              Loading datasets...
            </div>
          ) : datasets.length === 0 ? (
            <div className="p-4 text-center text-gray-500">
              <Database className="h-8 w-8 mx-auto mb-2 text-gray-300" />
              <p className="text-sm">No datasets found</p>
              <p className="text-xs text-gray-400 mt-1">Upload a dataset to get started</p>
            </div>
          ) : (
            <div className="p-1">
              {multiSelect && (
                <div className="px-3 py-2 text-xs font-medium text-gray-500 border-b">
                  Select multiple datasets for combined analysis
                </div>
              )}
              
              {datasets.map((dataset) => {
                const isSelected = selectedDatasets.includes(dataset.id);
                
                return (
                  <div
                    key={dataset.id}
                    onClick={() => handleDatasetToggle(dataset.id)}
                    className={`flex items-center justify-between p-3 hover:bg-gray-50 cursor-pointer ${
                      isSelected ? 'bg-primary-50' : ''
                    }`}
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <span className={`font-medium ${isSelected ? 'text-primary-900' : 'text-gray-900'}`}>
                          {dataset.name}
                        </span>
                        {isSelected && <Check className="h-4 w-4 text-primary-600" />}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {dataset.questions_count || 0} questions • Uploaded {new Date(dataset.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
