'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Filter, X, ChevronDown, ChevronUp, Calendar, Users, Mail, 
  Building, MessageSquare, Eye, Database, Search, Plus, Minus
} from 'lucide-react';
import { cn } from '@/lib/utils';

// Enhanced filter types
export interface DateFilter {
  start_date?: string;  // YYYY-MM-DD
  end_date?: string;    // YYYY-MM-DD
  exact_date?: string;  // YYYY-MM-DD
}

export interface EnhancedFilters {
  // Column filtering
  selected_columns?: number[];  // [1] = questions, [2] = responses, [1,2] = both
  
  // Content filtering
  org_names?: string[];
  user_emails?: string[];
  tenant_names?: string[];
  
  // Date filtering
  date_filter?: DateFilter;
  
  // Text filtering
  exclude_words?: string[];
  include_words?: string[];
  min_word_length?: number;
  max_words?: number;
  
  // Sentiment filtering
  sentiments?: string[];
}

interface EnhancedFilterPanelProps {
  filters: EnhancedFilters;
  onFiltersChange: (filters: EnhancedFilters) => void;
  availableOrgs?: string[];
  availableEmails?: string[];
  availableTenants?: string[];
  datasetIds?: string[]; // Add dataset IDs to fetch filter options
  className?: string;
  sidebarMode?: boolean; // New prop to control sidebar behavior
}

const COLUMN_PRESETS = [
  {
    id: 'questions_only',
    label: 'Questions Only',
    description: 'Analyze only user questions',
    icon: MessageSquare,
    columns: [1]
  },
  {
    id: 'responses_only', 
    label: 'Responses Only',
    description: 'Analyze only AI responses',
    icon: Eye,
    columns: [2]
  },
  {
    id: 'both',
    label: 'Questions & Responses',
    description: 'Analyze both (recommended)',
    icon: Database,
    columns: [1, 2]
  }
];

const SENTIMENT_OPTIONS = [
  { id: 'positive', label: 'Positive', color: 'text-green-600' },
  { id: 'negative', label: 'Negative', color: 'text-red-600' },
  { id: 'neutral', label: 'Neutral', color: 'text-gray-600' },
  { id: 'action', label: 'Action', color: 'text-blue-600' },
  { id: 'entity', label: 'Entity', color: 'text-purple-600' },
  { id: 'theme', label: 'Theme', color: 'text-orange-600' },
  { id: 'topic', label: 'Topic', color: 'text-indigo-600' }
];

export default function EnhancedFilterPanel({
  filters,
  onFiltersChange,
  availableOrgs = [],
  availableEmails = [],
  availableTenants = [],
  datasetIds = [],
  className,
  sidebarMode = false
}: EnhancedFilterPanelProps) {
  const [isExpanded, setIsExpanded] = useState(sidebarMode); // Auto-expand in sidebar mode
  const [activeSection, setActiveSection] = useState<string | null>(null);
  const [newWord, setNewWord] = useState('');
  const [newExcludeWord, setNewExcludeWord] = useState('');
  
  // State for dynamic filter options
  const [dynamicOrgs, setDynamicOrgs] = useState<string[]>([]);
  const [dynamicEmails, setDynamicEmails] = useState<string[]>([]);
  const [orgSearchTerm, setOrgSearchTerm] = useState('');
  const [emailSearchTerm, setEmailSearchTerm] = useState('');
  const [loadingFilterOptions, setLoadingFilterOptions] = useState(false);

  // Fetch filter options from API
  const fetchFilterOptions = useCallback(async () => {
    if (datasetIds.length === 0) return;
    
    setLoadingFilterOptions(true);
    try {
      // For now, use the first dataset ID
      const datasetId = datasetIds[0];
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://ai-text-analysis-production.up.railway.app';
      
      const response = await fetch(`${API_BASE_URL}/api/wordcloud/filter-options/${datasetId}`);
      if (response.ok) {
        const data = await response.json();
        setDynamicOrgs(data.organizations || []);
        setDynamicEmails(data.user_emails || []);
      }
    } catch (error) {
      console.error('Failed to fetch filter options:', error);
    } finally {
      setLoadingFilterOptions(false);
    }
  }, [datasetIds]);

  // Fetch filter options when dataset IDs change
  useEffect(() => {
    fetchFilterOptions();
  }, [fetchFilterOptions]);

  // Filter organizations based on search term
  const filteredOrgs = dynamicOrgs.filter(org => 
    org.toLowerCase().includes(orgSearchTerm.toLowerCase())
  );

  // Filter emails based on search term  
  const filteredEmails = dynamicEmails.filter(email =>
    email.toLowerCase().includes(emailSearchTerm.toLowerCase())
  );

  // Count active filters
  const activeFilterCount = Object.values(filters).filter(value => {
    if (Array.isArray(value)) return value.length > 0;
    if (typeof value === 'object' && value !== null) return Object.keys(value).length > 0;
    return value !== undefined && value !== null && value !== '';
  }).length;

  const updateFilter = useCallback((key: keyof EnhancedFilters, value: any) => {
    onFiltersChange({
      ...filters,
      [key]: value
    });
  }, [filters, onFiltersChange]);

  const clearAllFilters = () => {
    onFiltersChange({});
  };

  const addIncludeWord = () => {
    if (newWord.trim()) {
      const currentWords = filters.include_words || [];
      updateFilter('include_words', [...currentWords, newWord.trim()]);
      setNewWord('');
    }
  };

  const addExcludeWord = () => {
    if (newExcludeWord.trim()) {
      const currentWords = filters.exclude_words || [];
      updateFilter('exclude_words', [...currentWords, newExcludeWord.trim()]);
      setNewExcludeWord('');
    }
  };

  const removeIncludeWord = (index: number) => {
    const currentWords = filters.include_words || [];
    updateFilter('include_words', currentWords.filter((_, i) => i !== index));
  };

  const removeExcludeWord = (index: number) => {
    const currentWords = filters.exclude_words || [];
    updateFilter('exclude_words', currentWords.filter((_, i) => i !== index));
  };

  const toggleSentiment = (sentiment: string) => {
    const currentSentiments = filters.sentiments || [];
    if (currentSentiments.includes(sentiment)) {
      updateFilter('sentiments', currentSentiments.filter(s => s !== sentiment));
    } else {
      updateFilter('sentiments', [...currentSentiments, sentiment]);
    }
  };

  const toggleOrg = (org: string) => {
    const currentOrgs = filters.org_names || [];
    if (currentOrgs.includes(org)) {
      updateFilter('org_names', currentOrgs.filter(o => o !== org));
    } else {
      updateFilter('org_names', [...currentOrgs, org]);
    }
  };

  const toggleEmail = (email: string) => {
    const currentEmails = filters.user_emails || [];
    if (currentEmails.includes(email)) {
      updateFilter('user_emails', currentEmails.filter(e => e !== email));
    } else {
      updateFilter('user_emails', [...currentEmails, email]);
    }
  };

  return (
    <div className={cn("bg-white", !sidebarMode && "border border-gray-200 rounded-lg shadow-sm", className)}>
      {/* Filter Header - Only show in non-sidebar mode */}
      {!sidebarMode && (
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <Filter className="h-5 w-5 text-gray-500" />
            <span className="font-medium text-gray-900">Filters</span>
            {activeFilterCount > 0 && (
              <span className="px-2 py-1 bg-primary-100 text-primary-800 text-xs rounded-full">
                {activeFilterCount} active
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            {activeFilterCount > 0 && (
              <button
                onClick={clearAllFilters}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Clear all
              </button>
            )}
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-1 hover:bg-gray-100 rounded"
            >
              {isExpanded ? (
                <ChevronUp className="h-4 w-4 text-gray-500" />
              ) : (
                <ChevronDown className="h-4 w-4 text-gray-500" />
              )}
            </button>
          </div>
        </div>
      )}
      
      {/* Sidebar Mode: Show clear all button at top */}
      {sidebarMode && activeFilterCount > 0 && (
        <div className="p-4 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">
              {activeFilterCount} filter{activeFilterCount !== 1 ? 's' : ''} active
            </span>
            <button
              onClick={clearAllFilters}
              className="text-sm text-primary-600 hover:text-primary-700 font-medium"
            >
              Clear all
            </button>
          </div>
        </div>
      )}

      <AnimatePresence>
        {(isExpanded || sidebarMode) && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="p-4 space-y-6">
              
              {/* Column Selection - Enhanced UX */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Database className="h-4 w-4 text-primary-600" />
                  Content Source
                </h4>
                <div className="space-y-3">
                  {COLUMN_PRESETS.map((preset) => {
                    const isSelected = JSON.stringify(filters.selected_columns) === JSON.stringify(preset.columns);
                    return (
                      <button
                        key={preset.id}
                        onClick={() => updateFilter('selected_columns', preset.columns)}
                        className={cn(
                          "w-full p-3 text-left border rounded-lg transition-all duration-200 group",
                          isSelected
                            ? "border-primary-500 bg-primary-100 text-primary-900 shadow-sm"
                            : "border-gray-200 hover:border-primary-300 hover:bg-white text-gray-700 hover:shadow-sm"
                        )}
                      >
                        <div className="flex items-start gap-3">
                          <div className={cn(
                            "p-1.5 rounded-lg transition-colors",
                            isSelected 
                              ? "bg-primary-200 text-primary-700" 
                              : "bg-gray-200 text-gray-600 group-hover:bg-primary-100 group-hover:text-primary-600"
                          )}>
                            <preset.icon className="h-4 w-4" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-sm font-medium">{preset.label}</span>
                              {isSelected && (
                                <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                              )}
                            </div>
                            <p className={cn(
                              "text-xs leading-relaxed",
                              isSelected ? "text-primary-700" : "text-gray-500"
                            )}>
                              {preset.description}
                            </p>
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
                
                {/* Current Selection Info */}
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <div className="flex items-center gap-2 text-xs text-gray-600">
                    <div className="w-1.5 h-1.5 bg-primary-500 rounded-full"></div>
                    <span>
                      Currently analyzing: {
                        filters.selected_columns?.includes(1) && filters.selected_columns?.includes(2) 
                          ? "Questions & Responses"
                          : filters.selected_columns?.includes(1) 
                            ? "Questions Only" 
                            : "Responses Only"
                      }
                    </span>
                  </div>
                </div>
              </div>

              {/* Date Filter - Temporarily disabled */}
              <div className="opacity-50 pointer-events-none">
                <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  Date Range (Coming Soon)
                </h4>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Start Date</label>
                    <input
                      type="date"
                      value={filters.date_filter?.start_date || ''}
                      onChange={(e) => updateFilter('date_filter', {
                        ...filters.date_filter,
                        start_date: e.target.value || undefined
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">End Date</label>
                    <input
                      type="date"
                      value={filters.date_filter?.end_date || ''}
                      onChange={(e) => updateFilter('date_filter', {
                        ...filters.date_filter,
                        end_date: e.target.value || undefined
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                    />
                  </div>
                </div>
                <div className="mt-2">
                  <label className="block text-xs text-gray-500 mb-1">Or Exact Date</label>
                  <input
                    type="date"
                    value={filters.date_filter?.exact_date || ''}
                    onChange={(e) => updateFilter('date_filter', {
                      exact_date: e.target.value || undefined
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                  />
                </div>
              </div>

              {/* Organization Filter - Enhanced */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Building className="h-4 w-4 text-primary-600" />
                  Organizations
                  <span className="ml-auto text-xs text-gray-500 bg-white px-2 py-1 rounded-full">
                    {dynamicOrgs.length} available
                  </span>
                  {loadingFilterOptions && (
                    <div className="ml-2 w-3 h-3 border border-primary-500 border-t-transparent rounded-full animate-spin"></div>
                  )}
                </h4>
                
                {/* Search box - Enhanced */}
                <div className="relative mb-4">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search 712 organizations..."
                    value={orgSearchTerm}
                    onChange={(e) => setOrgSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white shadow-sm transition-all duration-200"
                  />
                  {orgSearchTerm && (
                    <button
                      onClick={() => setOrgSearchTerm('')}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  )}
                </div>

                {/* Selected organizations - Enhanced */}
                {filters.org_names && filters.org_names.length > 0 && (
                  <div className="mb-4 p-3 bg-white rounded-lg border border-primary-200">
                    <div className="text-xs font-medium text-primary-700 mb-2 flex items-center gap-2">
                      <div className="w-1.5 h-1.5 bg-primary-500 rounded-full"></div>
                      Selected Organizations ({filters.org_names.length})
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {filters.org_names.map((org) => (
                        <span
                          key={org}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-primary-100 hover:bg-primary-200 text-primary-800 text-xs rounded-lg border border-primary-200 transition-colors group"
                        >
                          <span className="max-w-[120px] truncate" title={org}>{org}</span>
                          <button
                            onClick={() => {
                              const newOrgNames = filters.org_names!.filter(o => o !== org);
                              onFiltersChange({
                                ...filters,
                                org_names: newOrgNames.length > 0 ? newOrgNames : undefined
                              });
                            }}
                            className="text-primary-600 hover:text-primary-800 transition-colors"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Available organizations list - Enhanced */}
                <div className="bg-white rounded-lg border border-gray-200">
                  {filteredOrgs.length === 0 ? (
                    <div className="p-4 text-sm text-gray-500 text-center">
                      {orgSearchTerm ? (
                        <div>
                          <Search className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                          <div>No organizations match "{orgSearchTerm}"</div>
                          <div className="text-xs mt-1">Try a different search term</div>
                        </div>
                      ) : (
                        <div>
                          <Building className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                          <div>No organizations available</div>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="max-h-48 overflow-y-auto">
                      {filteredOrgs.slice(0, 15).map((org, index) => (
                        <button
                          key={org}
                          onClick={() => {
                            const isSelected = filters.org_names?.includes(org);
                            const newOrgNames = isSelected
                              ? (filters.org_names || []).filter(o => o !== org)
                              : [...(filters.org_names || []), org];
                            onFiltersChange({
                              ...filters,
                              org_names: newOrgNames.length > 0 ? newOrgNames : undefined
                            });
                          }}
                          className={cn(
                            "w-full text-left px-3 py-2.5 text-sm transition-all duration-150 flex items-center gap-2 border-b border-gray-100 last:border-b-0",
                            filters.org_names?.includes(org)
                              ? 'bg-primary-50 text-primary-900 border-primary-100'
                              : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                          )}
                        >
                          <div className={cn(
                            "w-1.5 h-1.5 rounded-full transition-colors",
                            filters.org_names?.includes(org) ? 'bg-primary-500' : 'bg-gray-300'
                          )}></div>
                          <span className="flex-1 truncate" title={org}>{org}</span>
                          {filters.org_names?.includes(org) && (
                            <div className="text-primary-500">
                              <Building className="h-3 w-3" />
                            </div>
                          )}
                        </button>
                      ))}
                      
                      {/* Show more indicator */}
                      {filteredOrgs.length > 15 && (
                        <div className="px-3 py-2 text-xs text-gray-500 bg-gray-50 border-t border-gray-100 text-center">
                          Showing 15 of {filteredOrgs.length} results. Continue typing to narrow search.
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* User Email Filter - Searchable */}
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center gap-2">
                  <Mail className="h-4 w-4" />
                  User Emails
                  {loadingFilterOptions && <span className="text-xs text-gray-500">(Loading...)</span>}
                </h4>
                
                {/* Search box */}
                <div className="relative mb-3">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search user emails..."
                    value={emailSearchTerm}
                    onChange={(e) => setEmailSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>

                {/* Selected emails */}
                {filters.user_emails && filters.user_emails.length > 0 && (
                  <div className="mb-3">
                    <div className="text-xs text-gray-500 mb-1">Selected ({filters.user_emails.length}):</div>
                    <div className="flex flex-wrap gap-1">
                      {filters.user_emails.map((email) => (
                        <span
                          key={email}
                          className="inline-flex items-center gap-1 px-2 py-1 bg-primary-100 text-primary-800 text-xs rounded-full"
                        >
                          {email}
                          <button
                            onClick={() => {
                              const newUserEmails = filters.user_emails!.filter(e => e !== email);
                              onFiltersChange({
                                ...filters,
                                user_emails: newUserEmails.length > 0 ? newUserEmails : undefined
                              });
                            }}
                            className="ml-1 hover:text-primary-900"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Available emails list */}
                <div className="max-h-32 overflow-y-auto border border-gray-200 rounded-md">
                  {filteredEmails.length === 0 ? (
                    <div className="p-3 text-sm text-gray-500 text-center">
                      {emailSearchTerm ? 'No matching emails' : 'No emails available'}
                    </div>
                  ) : (
                    filteredEmails.slice(0, 10).map((email) => (
                      <button
                        key={email}
                        onClick={() => {
                          const isSelected = filters.user_emails?.includes(email);
                          const newUserEmails = isSelected
                            ? (filters.user_emails || []).filter(e => e !== email)
                            : [...(filters.user_emails || []), email];
                          onFiltersChange({
                            ...filters,
                            user_emails: newUserEmails.length > 0 ? newUserEmails : undefined
                          });
                        }}
                        className={`w-full text-left px-3 py-2 text-sm hover:bg-gray-50 border-b border-gray-100 last:border-b-0 ${
                          filters.user_emails?.includes(email) ? 'bg-primary-50 text-primary-900' : 'text-gray-700'
                        }`}
                      >
                        {email}
                      </button>
                    ))
                  )}
                </div>
              </div>

              {/* Remove the old conditionally rendered org filter */}
              {false && availableOrgs.length > 0 && (
                <div className="opacity-50 pointer-events-none">
                  <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center gap-2">
                    <Building className="h-4 w-4" />
                    Organizations (Coming Soon)
                  </h4>
                  <div className="space-y-2 max-h-32 overflow-y-auto">
                    {availableOrgs.map((org) => (
                      <label key={org} className="flex items-center gap-2 text-sm">
                        <input
                          type="checkbox"
                          checked={filters.org_names?.includes(org) || false}
                          onChange={() => toggleOrg(org)}
                          className="rounded border-gray-300"
                        />
                        <span className="truncate">{org}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              {/* Email Filter - Temporarily disabled */}
              {availableEmails.length > 0 && (
                <div className="opacity-50 pointer-events-none">
                  <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center gap-2">
                    <Mail className="h-4 w-4" />
                    User Emails (Coming Soon)
                  </h4>
                  <div className="space-y-2 max-h-32 overflow-y-auto">
                    {availableEmails.slice(0, 10).map((email) => (
                      <label key={email} className="flex items-center gap-2 text-sm">
                        <input
                          type="checkbox"
                          checked={filters.user_emails?.includes(email) || false}
                          onChange={() => toggleEmail(email)}
                          className="rounded border-gray-300"
                        />
                        <span className="truncate">{email}</span>
                      </label>
                    ))}
                    {availableEmails.length > 10 && (
                      <p className="text-xs text-gray-500">... and {availableEmails.length - 10} more</p>
                    )}
                  </div>
                </div>
              )}

              {/* Word Filtering */}
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center gap-2">
                  <Search className="h-4 w-4" />
                  Word Filtering
                </h4>
                
                {/* Include Words */}
                <div className="mb-4">
                  <label className="block text-xs text-gray-500 mb-2">Include Only These Words</label>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={newWord}
                      onChange={(e) => setNewWord(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && addIncludeWord()}
                      placeholder="Add word to include..."
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
                    />
                    <button
                      onClick={addIncludeWord}
                      className="px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                    >
                      <Plus className="h-4 w-4" />
                    </button>
                  </div>
                  {filters.include_words && filters.include_words.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {filters.include_words.map((word, index) => (
                        <span
                          key={index}
                          className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full"
                        >
                          {word}
                          <button
                            onClick={() => removeIncludeWord(index)}
                            className="hover:text-green-600"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Exclude Words */}
                <div className="mb-4">
                  <label className="block text-xs text-gray-500 mb-2">Exclude These Words</label>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={newExcludeWord}
                      onChange={(e) => setNewExcludeWord(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && addExcludeWord()}
                      placeholder="Add word to exclude..."
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
                    />
                    <button
                      onClick={addExcludeWord}
                      className="px-3 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                    >
                      <Plus className="h-4 w-4" />
                    </button>
                  </div>
                  {filters.exclude_words && filters.exclude_words.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {filters.exclude_words.map((word, index) => (
                        <span
                          key={index}
                          className="inline-flex items-center gap-1 px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full"
                        >
                          {word}
                          <button
                            onClick={() => removeExcludeWord(index)}
                            className="hover:text-red-600"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Word Length & Count */}
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Min Word Length</label>
                    <input
                      type="number"
                      min="1"
                      max="20"
                      value={filters.min_word_length || 3}
                      onChange={(e) => updateFilter('min_word_length', parseInt(e.target.value) || 3)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Max Words</label>
                    <input
                      type="number"
                      min="10"
                      max="500"
                      value={filters.max_words || 100}
                      onChange={(e) => updateFilter('max_words', parseInt(e.target.value) || 100)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                    />
                  </div>
                </div>
              </div>

              {/* Sentiment Filter */}
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center gap-2">
                  <Users className="h-4 w-4" />
                  Sentiment Types
                </h4>
                <div className="flex flex-wrap gap-2">
                  {SENTIMENT_OPTIONS.map((sentiment) => (
                    <button
                      key={sentiment.id}
                      onClick={() => toggleSentiment(sentiment.id)}
                      className={cn(
                        "px-3 py-2 text-sm rounded-lg border transition-all",
                        filters.sentiments?.includes(sentiment.id)
                          ? "border-primary-500 bg-primary-50 text-primary-900"
                          : "border-gray-200 hover:border-gray-300 text-gray-700"
                      )}
                    >
                      <span className={sentiment.color}>{sentiment.label}</span>
                    </button>
                  ))}
                </div>
              </div>

            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
