'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Filter, 
  Calendar, 
  Users, 
  Tag, 
  TrendingUp, 
  RotateCw,
  Palette,
  Grid,
  Shuffle,
  CircleDot
} from 'lucide-react';
import { WordCloudFilters } from '@/lib/types';
import { cn } from '@/lib/utils';

interface WordCloudControlsProps {
  mode: string;
  filters: WordCloudFilters;
  animationEnabled: boolean;
  layoutMode: 'spiral' | 'random' | 'grid';
  onModeChange: (mode: string) => void;
  onFiltersChange: (filters: WordCloudFilters) => void;
  onAnimationToggle: (enabled: boolean) => void;
  onLayoutModeChange: (mode: 'spiral' | 'random' | 'grid') => void;
}

const ANALYSIS_MODES = [
  { id: 'all', label: 'All Words', icon: Tag, description: 'All significant words from the dataset' },
  { id: 'verbs', label: 'Action Words', icon: TrendingUp, description: 'Verbs and action-oriented language' },
  { id: 'themes', label: 'Themes', icon: Grid, description: 'Thematic categories and topics' },
  { id: 'emotions', label: 'Emotions', icon: Palette, description: 'Emotional words and sentiment indicators' },
  { id: 'entities', label: 'Entities', icon: Users, description: 'Named entities (people, places, organizations)' },
  { id: 'topics', label: 'Topics', icon: CircleDot, description: 'Topic modeling results' }
];

const LAYOUT_MODES = [
  { id: 'spiral', label: 'Spiral', icon: RotateCw, description: 'Spiral arrangement from center' },
  { id: 'random', label: 'Random', icon: Shuffle, description: 'Random positioning with collision avoidance' },
  { id: 'grid', label: 'Grid', icon: Grid, description: 'Organized grid layout' }
];

const SENTIMENT_OPTIONS = [
  { value: '', label: 'All Sentiments' },
  { value: 'positive', label: 'Positive', color: 'text-green-600' },
  { value: 'negative', label: 'Negative', color: 'text-red-600' },
  { value: 'neutral', label: 'Neutral', color: 'text-gray-600' }
];

const QUESTION_TYPES = [
  'technical_support',
  'billing',
  'feature_request',
  'bug_report',
  'general_inquiry',
  'complaint',
  'compliment',
  'suggestion'
];

export default function WordCloudControls({
  mode,
  filters,
  animationEnabled,
  layoutMode,
  onModeChange,
  onFiltersChange,
  onAnimationToggle,
  onLayoutModeChange,
}: WordCloudControlsProps) {
  const [activeTab, setActiveTab] = useState<'mode' | 'filters' | 'display'>('mode');

  const updateFilter = (key: keyof WordCloudFilters, value: any) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  return (
    <div className="p-4 bg-gray-50">
      {/* Tab Navigation */}
      <div className="flex items-center gap-2 mb-4 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('mode')}
          className={cn(
            "px-4 py-2 text-sm font-medium border-b-2 transition-colors",
            activeTab === 'mode' 
              ? "text-primary-600 border-primary-600" 
              : "text-gray-500 border-transparent hover:text-gray-700"
          )}
        >
          Analysis Mode
        </button>
        <button
          onClick={() => setActiveTab('filters')}
          className={cn(
            "px-4 py-2 text-sm font-medium border-b-2 transition-colors",
            activeTab === 'filters' 
              ? "text-primary-600 border-primary-600" 
              : "text-gray-500 border-transparent hover:text-gray-700"
          )}
        >
          Filters
        </button>
        <button
          onClick={() => setActiveTab('display')}
          className={cn(
            "px-4 py-2 text-sm font-medium border-b-2 transition-colors",
            activeTab === 'display' 
              ? "text-primary-600 border-primary-600" 
              : "text-gray-500 border-transparent hover:text-gray-700"
          )}
        >
          Display
        </button>
      </div>

      {/* Tab Content */}
      <motion.div
        key={activeTab}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
      >
        {activeTab === 'mode' && (
          <div className="space-y-4">
            <h4 className="text-sm font-semibold text-gray-900 mb-3">
              Choose Analysis Mode
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {ANALYSIS_MODES.map((modeOption) => {
                const Icon = modeOption.icon;
                const isActive = mode === modeOption.id;
                
                return (
                  <button
                    key={modeOption.id}
                    onClick={() => onModeChange(modeOption.id)}
                    className={cn(
                      "p-4 text-left rounded-lg border-2 transition-all duration-200",
                      isActive 
                        ? "border-primary-500 bg-primary-50 text-primary-900" 
                        : "border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm"
                    )}
                  >
                    <div className="flex items-center gap-3 mb-2">
                      <Icon className={cn(
                        "h-5 w-5",
                        isActive ? "text-primary-600" : "text-gray-500"
                      )} />
                      <span className="font-medium">{modeOption.label}</span>
                      {isActive && (
                        <div className="ml-auto">
                          <div className="h-2 w-2 bg-primary-600 rounded-full"></div>
                        </div>
                      )}
                    </div>
                    <p className={cn(
                      "text-sm",
                      isActive ? "text-primary-700" : "text-gray-600"
                    )}>
                      {modeOption.description}
                    </p>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {activeTab === 'filters' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Organization Filter */}
              <div className="space-y-3">
                <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
                  <Users className="h-4 w-4" />
                  Organization
                </label>
                <div className="space-y-2">
                  <input
                    type="text"
                    placeholder="Organization ID"
                    value={filters.orgId || ''}
                    onChange={(e) => updateFilter('orgId', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                  <input
                    type="text"
                    placeholder="Organization Name"
                    value={filters.orgName || ''}
                    onChange={(e) => updateFilter('orgName', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Sentiment Filter */}
              <div className="space-y-3">
                <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
                  <Palette className="h-4 w-4" />
                  Sentiment
                </label>
                <select
                  value={filters.sentiment || ''}
                  onChange={(e) => updateFilter('sentiment', e.target.value || undefined)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  {SENTIMENT_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Question Type Filter */}
              <div className="space-y-3">
                <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
                  <Tag className="h-4 w-4" />
                  Question Type
                </label>
                <select
                  value={filters.questionType || ''}
                  onChange={(e) => updateFilter('questionType', e.target.value || undefined)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">All Question Types</option>
                  {QUESTION_TYPES.map((type) => (
                    <option key={type} value={type}>
                      {type.split('_').map(word => 
                        word.charAt(0).toUpperCase() + word.slice(1)
                      ).join(' ')}
                    </option>
                  ))}
                </select>
              </div>

              {/* Date Range Filter */}
              <div className="space-y-3">
                <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
                  <Calendar className="h-4 w-4" />
                  Date Range
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="date"
                    placeholder="Start Date"
                    value={filters.dateRange?.start ? filters.dateRange.start.toISOString().split('T')[0] : ''}
                    onChange={(e) => {
                      const startDate = e.target.value ? new Date(e.target.value) : undefined;
                      updateFilter('dateRange', startDate ? {
                        start: startDate,
                        end: filters.dateRange?.end || new Date()
                      } : undefined);
                    }}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                  <input
                    type="date"
                    placeholder="End Date"
                    value={filters.dateRange?.end ? filters.dateRange.end.toISOString().split('T')[0] : ''}
                    onChange={(e) => {
                      const endDate = e.target.value ? new Date(e.target.value) : undefined;
                      updateFilter('dateRange', endDate ? {
                        start: filters.dateRange?.start || new Date(),
                        end: endDate
                      } : undefined);
                    }}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            {/* Complexity Range Filter */}
            <div className="space-y-3">
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
                <TrendingUp className="h-4 w-4" />
                Complexity Range
              </label>
              <div className="px-3">
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={filters.complexityRange?.[0] || 0}
                  onChange={(e) => {
                    const min = parseFloat(e.target.value);
                    const max = filters.complexityRange?.[1] || 1;
                    updateFilter('complexityRange', [min, max]);
                  }}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Low ({filters.complexityRange?.[0] || 0})</span>
                  <span>High ({filters.complexityRange?.[1] || 1})</span>
                </div>
              </div>
            </div>

            {/* Active Filters Summary */}
            <div className="mt-6 pt-4 border-t border-gray-200">
              <h5 className="text-sm font-medium text-gray-700 mb-2">Active Filters:</h5>
              <div className="flex flex-wrap gap-2">
                {Object.entries(filters).map(([key, value]) => {
                  if (!value) return null;
                  
                  let displayValue = '';
                  if (key === 'dateRange') {
                    const range = value as { start: Date; end: Date };
                    displayValue = `${range.start.toLocaleDateString()} - ${range.end.toLocaleDateString()}`;
                  } else if (key === 'complexityRange') {
                    const range = value as [number, number];
                    displayValue = `${range[0]} - ${range[1]}`;
                  } else {
                    displayValue = String(value);
                  }

                  return (
                    <span
                      key={key}
                      className="inline-flex items-center gap-1 px-2 py-1 bg-primary-100 text-primary-800 text-xs rounded-full"
                    >
                      {key}: {displayValue}
                      <button
                        onClick={() => updateFilter(key as keyof WordCloudFilters, undefined)}
                        className="hover:text-primary-600"
                      >
                        ×
                      </button>
                    </span>
                  );
                })}
                
                {Object.keys(filters).length === 0 && (
                  <span className="text-gray-500 text-sm">No filters applied</span>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'display' && (
          <div className="space-y-6">
            {/* Layout Mode */}
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-gray-900">Layout Mode</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {LAYOUT_MODES.map((layoutOption) => {
                  const Icon = layoutOption.icon;
                  const isActive = layoutMode === layoutOption.id;
                  
                  return (
                    <button
                      key={layoutOption.id}
                      onClick={() => onLayoutModeChange(layoutOption.id as 'spiral' | 'random' | 'grid')}
                      className={cn(
                        "p-3 text-left rounded-lg border-2 transition-all duration-200",
                        isActive 
                          ? "border-primary-500 bg-primary-50 text-primary-900" 
                          : "border-gray-200 bg-white hover:border-gray-300"
                      )}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <Icon className={cn(
                          "h-4 w-4",
                          isActive ? "text-primary-600" : "text-gray-500"
                        )} />
                        <span className="font-medium text-sm">{layoutOption.label}</span>
                      </div>
                      <p className={cn(
                        "text-xs",
                        isActive ? "text-primary-700" : "text-gray-600"
                      )}>
                        {layoutOption.description}
                      </p>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Animation Settings */}
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-gray-900">Animation</h4>
              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={animationEnabled}
                  onChange={(e) => onAnimationToggle(e.target.checked)}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm text-gray-700">
                  Enable entrance animations
                </span>
              </label>
              <p className="text-xs text-gray-500 ml-6">
                Words will animate in when the cloud is generated
              </p>
            </div>

            {/* Color Scheme (Future Enhancement) */}
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-gray-900">Color Scheme</h4>
              <div className="grid grid-cols-3 gap-2">
                <button className="h-8 rounded bg-gradient-to-r from-blue-500 to-purple-500 border-2 border-primary-500" title="Default"></button>
                <button className="h-8 rounded bg-gradient-to-r from-green-500 to-blue-500 border-2 border-transparent hover:border-gray-300" title="Nature"></button>
                <button className="h-8 rounded bg-gradient-to-r from-red-500 to-yellow-500 border-2 border-transparent hover:border-gray-300" title="Warm"></button>
              </div>
              <p className="text-xs text-gray-500">
                More color schemes coming soon
              </p>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}
