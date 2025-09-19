'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef, GridOptions, GridReadyEvent } from 'ag-grid-community';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import { Download, Filter, Search, RefreshCw, ChevronRight, ChevronLeft } from 'lucide-react';
import toast from 'react-hot-toast';
import { EnhancedFilterPanel, EnhancedFilters } from '../wordcloud/EnhancedFilterPanel';
import { cn } from '@/lib/utils';

interface Question {
  id: string;
  original_question: string;
  ai_response: string;
  project_id?: string;
  user_id?: string;
  org_name?: string;           // Organization filter support
  user_id_from_csv?: string;   // Email filter support
  timestamp_from_csv?: string; // Date filter support
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
  
  // Filter panel state
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<EnhancedFilters>({
    selected_columns: [1, 2], // Both questions and responses by default for table view
    org_names: [],
    user_emails: [],
    tenant_names: [],
    exclude_words: [],
    include_words: [],
    min_word_length: 3,
    max_words: 1000,
    sentiments: []
  });
  const [appliedFilters, setAppliedFilters] = useState<EnhancedFilters>(filters);
  
  // Filter options from API
  const [availableOrgs, setAvailableOrgs] = useState<string[]>([]);
  const [availableEmails, setAvailableEmails] = useState<string[]>([]);
  const [loadingFilterOptions, setLoadingFilterOptions] = useState(false);

  // Column definitions for AG Grid
  const columnDefs = useMemo<ColDef[]>(() => [
    {
      headerName: 'Question',
      field: 'original_question',
      flex: 2,
      minWidth: 300,
      wrapText: true,
      cellClass: 'text-wrap',
      tooltipField: 'original_question'
    },
    {
      headerName: 'Response', 
      field: 'ai_response',
      flex: 2,
      minWidth: 300,
      wrapText: true,
      cellClass: 'text-wrap',
      tooltipField: 'ai_response'
    },
    {
      headerName: 'Organization',
      field: 'org_name',
      width: 150,
      hide: false, // Show by default for filtering context
    },
    {
      headerName: 'User Email',
      field: 'user_id_from_csv',
      width: 180,
      hide: false, // Show by default for filtering context
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
      headerName: 'Date',
      field: 'timestamp_from_csv',
      width: 120,
      valueFormatter: (params) => {
        if (params.value) {
          return new Date(params.value).toLocaleDateString();
        }
        return '';
      }
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
    domLayout: 'autoHeight', // Auto-height for wrapped text
  }), []);

  // Fetch filter options
  const fetchFilterOptions = async () => {
    setLoadingFilterOptions(true);
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://ai-text-analysis-production.up.railway.app';
      const response = await fetch(`${API_BASE_URL}/api/wordcloud/filter-options/${datasetId}`);
      
      if (response.ok) {
        const data = await response.json();
        setAvailableOrgs(data.organizations || []);
        setAvailableEmails(data.user_emails || []);
      } else {
        console.warn('Failed to fetch filter options:', response.status);
      }
    } catch (error) {
      console.warn('Error fetching filter options:', error);
    } finally {
      setLoadingFilterOptions(false);
    }
  };

  // Fetch questions data with optional filtering
  const fetchQuestions = async (page: number = 1, filters?: EnhancedFilters) => {
    setLoading(true);
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://ai-text-analysis-production.up.railway.app';
      
      // Build query parameters
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: pageSize.toString()
      });
      
      // Add filter parameters if filters are applied
      if (filters) {
        if (filters.org_names && filters.org_names.length > 0) {
          params.append('org_names', filters.org_names.join(','));
        }
        if (filters.user_emails && filters.user_emails.length > 0) {
          params.append('user_emails', filters.user_emails.join(','));
        }
        if (filters.date_filter?.start_date) {
          params.append('start_date', filters.date_filter.start_date);
        }
        if (filters.date_filter?.end_date) {
          params.append('end_date', filters.date_filter.end_date);
        }
        if (filters.include_words && filters.include_words.length > 0) {
          params.append('include_words', filters.include_words.join(','));
        }
        if (filters.exclude_words && filters.exclude_words.length > 0) {
          params.append('exclude_words', filters.exclude_words.join(','));
        }
      }
      
      const response = await fetch(
        `${API_BASE_URL}/api/datasets/${datasetId}/questions?${params.toString()}`
      );
      
      if (!response.ok) {
        throw new Error(`Failed to fetch questions: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Questions data:', data);
      
      // Handle the API response structure - it returns { data: [...], pagination: {...} }
      if (data.data && Array.isArray(data.data)) {
        setQuestions(data.data);
        setTotalRows(data.pagination?.total_count || data.data.length);
      } else if (data.success && data.data) {
        // Fallback for success-based responses
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

  // Filter handlers
  const handleFiltersChange = (newFilters: EnhancedFilters) => {
    setFilters(newFilters);
  };

  const handleApplyFilters = (newFilters: EnhancedFilters) => {
    setAppliedFilters(newFilters);
    fetchQuestions(1, newFilters); // Reset to page 1 when applying filters
    setCurrentPage(1);
  };

  // Search filter
  const filteredQuestions = useMemo(() => {
    if (!searchText.trim()) return questions;
    
    const searchLower = searchText.toLowerCase();
    return questions.filter(q => 
      q.original_question?.toLowerCase().includes(searchLower) ||
      q.ai_response?.toLowerCase().includes(searchLower) ||
      q.project_id?.toLowerCase().includes(searchLower) ||
      q.user_id?.toLowerCase().includes(searchLower) ||
      q.org_name?.toLowerCase().includes(searchLower) ||
      q.user_id_from_csv?.toLowerCase().includes(searchLower)
    );
  }, [questions, searchText]);

  // Export to CSV
  const exportToCSV = () => {
    const csvContent = [
      ['Question', 'Response', 'Organization', 'User Email', 'Date', 'Project ID', 'User ID', 'Created At'],
      ...filteredQuestions.map(q => [
        q.original_question || '',
        q.ai_response || '',
        q.org_name || '',
        q.user_id_from_csv || '',
        q.timestamp_from_csv || '',
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
    fetchQuestions(currentPage, appliedFilters);
    fetchFilterOptions(); // Fetch filter options when dataset changes
  }, [datasetId, currentPage]);

  // Refetch when applied filters change
  useEffect(() => {
    if (appliedFilters !== filters) {
      // Only refetch if applied filters actually changed and aren't the initial state
      fetchQuestions(currentPage, appliedFilters);
    }
  }, [appliedFilters]);

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
    <div className="h-full flex gap-6">
      {/* Left Sidebar - Filter Panel */}
      <div className={cn(
        "transition-all duration-300 ease-in-out",
        showFilters ? "w-80 flex-shrink-0" : "w-0 overflow-hidden"
      )}>
        {showFilters && (
          <div className="w-80 h-full">
            <EnhancedFilterPanel
              filters={filters}
              onFiltersChange={handleFiltersChange}
              onApplyFilters={handleApplyFilters}
              availableOrgs={availableOrgs}
              availableEmails={availableEmails}
              datasetIds={[datasetId]}
              sidebarMode={true}
              className="h-full"
            />
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 min-w-0">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 h-full flex flex-col">
          {/* Header */}
          <div className="p-4 border-b border-gray-200 flex-shrink-0">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-lg font-semibold text-gray-900">Dataset Questions</h3>
                  {loading && (
                    <div className="flex items-center gap-1 text-primary-600">
                      <div className="w-3 h-3 border-2 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
                      <span className="text-xs font-medium">Loading...</span>
                    </div>
                  )}
                </div>
                <p className="text-sm text-gray-600">
                  {filteredQuestions.length} of {totalRows} questions
                  {searchText && ` (searched)`}
                  {(appliedFilters.org_names?.length || appliedFilters.user_emails?.length) && ` (filtered)`}
                </p>
              </div>
              
              <div className="flex items-center space-x-2">
                {/* Filter Toggle */}
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className={cn(
                    "flex items-center gap-2 px-3 py-2 rounded-lg transition-all duration-200 text-sm font-medium border",
                    showFilters 
                      ? "bg-primary-100 text-primary-700 border-primary-200 shadow-sm" 
                      : "bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100 hover:border-gray-300"
                  )}
                  title={showFilters ? "Hide filters" : "Show filters"}
                >
                  <Filter className="h-4 w-4" />
                  <span>Filters</span>
                  {showFilters ? (
                    <ChevronLeft className="h-3 w-3 ml-1" />
                  ) : (
                    <ChevronRight className="h-3 w-3 ml-1" />
                  )}
                </button>

                {/* Search */}
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search questions..."
                    value={searchText}
                    onChange={(e) => setSearchText(e.target.value)}
                    className="pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                
                {/* Export Button */}
                <button
                  onClick={exportToCSV}
                  className="flex items-center space-x-2 px-3 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors text-sm"
                >
                  <Download className="w-4 h-4" />
                  <span>Export CSV</span>
                </button>
                
                {/* Refresh Button */}
                <button
                  onClick={() => fetchQuestions(currentPage, appliedFilters)}
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
          <div className="flex-1 p-4 min-h-0">
            <div className="ag-theme-alpine h-full" style={{ width: '100%' }}>
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
                    {(appliedFilters.org_names?.length || appliedFilters.user_emails?.length) && (
                      <p className="text-sm">Try adjusting your filters</p>
                    )}
                  </div>
                )}
              />
            </div>
          </div>

          {/* Pagination Info */}
          {totalRows > pageSize && (
            <div className="px-4 py-3 border-t border-gray-200 flex items-center justify-between flex-shrink-0">
              <div className="text-sm text-gray-700">
                Showing {Math.min(pageSize, filteredQuestions.length)} of {totalRows} questions
              </div>
              <div className="text-sm text-gray-500">
                Page {currentPage} • {pageSize} per page
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
