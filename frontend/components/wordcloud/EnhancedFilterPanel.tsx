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
  className?: string;
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
  className
}: EnhancedFilterPanelProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeSection, setActiveSection] = useState<string | null>(null);
  const [newWord, setNewWord] = useState('');
  const [newExcludeWord, setNewExcludeWord] = useState('');

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
    <div className={cn("bg-white border border-gray-200 rounded-lg shadow-sm", className)}>
      {/* Filter Header */}
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

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="p-4 space-y-6">
              
              {/* Column Selection */}
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center gap-2">
                  <Database className="h-4 w-4" />
                  Content Source
                </h4>
                <div className="grid grid-cols-3 gap-2">
                  {COLUMN_PRESETS.map((preset) => (
                    <button
                      key={preset.id}
                      onClick={() => updateFilter('selected_columns', preset.columns)}
                      className={cn(
                        "p-3 text-left border rounded-lg transition-all",
                        JSON.stringify(filters.selected_columns) === JSON.stringify(preset.columns)
                          ? "border-primary-500 bg-primary-50 text-primary-900"
                          : "border-gray-200 hover:border-gray-300 text-gray-700"
                      )}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <preset.icon className="h-4 w-4" />
                        <span className="text-sm font-medium">{preset.label}</span>
                      </div>
                      <p className="text-xs text-gray-500">{preset.description}</p>
                    </button>
                  ))}
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

              {/* Organization Filter */}
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center gap-2">
                  <Building className="h-4 w-4" />
                  Organizations
                </h4>
                <div className="space-y-2">
                  {['Singleton Schreiber', 'Cades Schutte', 'Thompson & Knight', 'Baker McKenzie'].map((org) => (
                    <label key={org} className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={filters.org_names?.includes(org) || false}
                        onChange={(e) => {
                          const newOrgNames = e.target.checked
                            ? [...(filters.org_names || []), org]
                            : (filters.org_names || []).filter(o => o !== org);
                          onFiltersChange({
                            ...filters,
                            org_names: newOrgNames.length > 0 ? newOrgNames : undefined
                          });
                        }}
                        className="rounded border-gray-300"
                      />
                      <span className="text-gray-700">{org}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* User Email Filter */}
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center gap-2">
                  <Mail className="h-4 w-4" />
                  User Emails
                </h4>
                <div className="space-y-2">
                  {['john.doe@law.com', 'jane.smith@legal.net', 'bob.jones@attorney.org'].map((email) => (
                    <label key={email} className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={filters.user_emails?.includes(email) || false}
                        onChange={(e) => {
                          const newUserEmails = e.target.checked
                            ? [...(filters.user_emails || []), email]
                            : (filters.user_emails || []).filter(u => u !== email);
                          onFiltersChange({
                            ...filters,
                            user_emails: newUserEmails.length > 0 ? newUserEmails : undefined
                          });
                        }}
                        className="rounded border-gray-300"
                      />
                      <span className="text-gray-700">{email}</span>
                    </label>
                  ))}
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
