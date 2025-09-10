'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef, GridOptions, GridReadyEvent } from 'ag-grid-community';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import { Download, Filter, Search, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';

interface Question {
  id: string;
  original_question: string;
  ai_response: string;
  project_id?: string;
  user_id?: string;
  created_at: string;
}

interface DatasetTableViewProps {
  datasetId: string;
  datasetName: string;
}

export default function DatasetTableView({ datasetId, datasetName }: DatasetTableViewProps) {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchText, setSearchText] = useState('');
  const [totalRows, setTotalRows] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(50);

  // Column definitions for AG Grid
  const columnDefs = useMemo<ColDef[]>(() => [
    {
      headerName: 'Question',
      field: 'original_question',
      flex: 2,
      minWidth: 300,
      wrapText: true,
      autoHeight: true,
      cellClass: 'text-wrap',
      tooltipField: 'original_question'
    },
    {
      headerName: 'Response', 
      field: 'ai_response',
      flex: 2,
      minWidth: 300,
      wrapText: true,
      autoHeight: true,
      cellClass: 'text-wrap',
      tooltipField: 'ai_response'
    },
    {
      headerName: 'Project ID',
      field: 'project_id',
      width: 120,
      hide: true, // Hidden by default, can be shown via column menu
    },
    {
      headerName: 'User ID',
      field: 'user_id', 
      width: 120,
      hide: true, // Hidden by default
    },
    {
      headerName: 'Created',
      field: 'created_at',
      width: 150,
      valueFormatter: (params) => {
        if (params.value) {
          return new Date(params.value).toLocaleDateString();
        }
        return '';
      }
    }
  ], []);

  // Grid options
  const gridOptions = useMemo<GridOptions>(() => ({
    defaultColDef: {
      sortable: true,
      filter: true,
      resizable: true,
      minWidth: 100,
    },
    pagination: false, // We'll handle pagination ourselves
    rowSelection: 'multiple',
    suppressRowClickSelection: false,
    animateRows: true,
    enableBrowserTooltips: true,
    getRowHeight: () => 'auto', // Auto-height for wrapped text
  }), []);

  // Fetch questions data
  const fetchQuestions = async (page: number = 1) => {
    setLoading(true);
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://ai-text-analysis-production.up.railway.app';
      const response = await fetch(
        `${API_BASE_URL}/api/datasets/${datasetId}/questions?page=${page}&per_page=${pageSize}`
      );
      
      if (!response.ok) {
        throw new Error(`Failed to fetch questions: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Questions data:', data);
      
      if (data.success) {
        setQuestions(data.data || []);
        setTotalRows(data.total || 0);
      } else {
        throw new Error(data.message || 'Failed to load questions');
      }
      
    } catch (error) {
      console.error('Error fetching questions:', error);
      toast.error('Failed to load dataset questions');
      setQuestions([]);
    } finally {
      setLoading(false);
    }
  };

  // Search filter
  const filteredQuestions = useMemo(() => {
    if (!searchText.trim()) return questions;
    
    const searchLower = searchText.toLowerCase();
    return questions.filter(q => 
      q.original_question?.toLowerCase().includes(searchLower) ||
      q.ai_response?.toLowerCase().includes(searchLower) ||
      q.project_id?.toLowerCase().includes(searchLower) ||
      q.user_id?.toLowerCase().includes(searchLower)
    );
  }, [questions, searchText]);

  // Export to CSV
  const exportToCSV = () => {
    const csvContent = [
      ['Question', 'Response', 'Project ID', 'User ID', 'Created At'],
      ...filteredQuestions.map(q => [
        q.original_question || '',
        q.ai_response || '',
        q.project_id || '',
        q.user_id || '',
        q.created_at || ''
      ])
    ];
    
    const csvString = csvContent.map(row => 
      row.map(field => `"${(field || '').replace(/"/g, '""')}"`).join(',')
    ).join('\n');
    
    const blob = new Blob([csvString], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${datasetName}_questions.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toast.success('Dataset exported successfully!');
  };

  useEffect(() => {
    fetchQuestions(currentPage);
  }, [datasetId, currentPage]);

  if (loading && questions.length === 0) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="flex items-center space-x-2 text-gray-600">
          <RefreshCw className="w-5 h-5 animate-spin" />
          <span>Loading dataset...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Dataset Questions</h3>
            <p className="text-sm text-gray-600">
              {filteredQuestions.length} of {totalRows} questions
              {searchText && ` (filtered)`}
            </p>
          </div>
          
          <div className="flex items-center space-x-2">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search questions..."
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            {/* Export Button */}
            <button
              onClick={exportToCSV}
              className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
            >
              <Download className="w-4 h-4" />
              <span>Export CSV</span>
            </button>
            
            {/* Refresh Button */}
            <button
              onClick={() => fetchQuestions(currentPage)}
              disabled={loading}
              className="flex items-center space-x-2 px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors text-sm"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>
        </div>
      </div>

      {/* AG Grid Table */}
      <div className="p-4">
        <div className="ag-theme-alpine" style={{ height: '600px', width: '100%' }}>
          <AgGridReact
            rowData={filteredQuestions}
            columnDefs={columnDefs}
            gridOptions={gridOptions}
            loadingOverlayComponent={() => (
              <div className="flex items-center justify-center">
                <RefreshCw className="w-5 h-5 animate-spin mr-2" />
                Loading...
              </div>
            )}
            noRowsOverlayComponent={() => (
              <div className="flex flex-col items-center justify-center text-gray-500">
                <Filter className="w-8 h-8 mb-2" />
                <p>No questions found</p>
                {searchText && <p className="text-sm">Try adjusting your search</p>}
              </div>
            )}
          />
        </div>
      </div>

      {/* Pagination Info */}
      {totalRows > pageSize && (
        <div className="px-4 py-3 border-t border-gray-200 flex items-center justify-between">
          <div className="text-sm text-gray-700">
            Showing {Math.min(pageSize, filteredQuestions.length)} of {totalRows} questions
          </div>
          <div className="text-sm text-gray-500">
            Page {currentPage} • {pageSize} per page
          </div>
        </div>
      )}
    </div>
  );
}
