'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, BarChart3, MessageSquare, Cloud, Download, Settings, Table } from 'lucide-react';
import Link from 'next/link';
import DatasetViewer from '@/components/datasets/DatasetViewer';
import DatasetTableView from '@/components/datasets/DatasetTableView';
import SimpleWordCloud from '@/components/wordcloud/SimpleWordCloud';
import { WordCloudFilters } from '@/lib/types';
import { cn } from '@/lib/utils';

interface DatasetViewPageProps {
  datasetId: string;
}

type ViewTab = 'questions' | 'table' | 'wordcloud' | 'analytics';

export default function DatasetViewPage({ datasetId }: DatasetViewPageProps) {
  const [activeTab, setActiveTab] = useState<ViewTab>('questions');
  const [wordCloudFilters] = useState<WordCloudFilters>({});

  // For real legal dataset, use the dedicated API
  const isLegalDataset = datasetId === '06a8437a-27e8-412f-a530-6cb04f7b6dc9';

  const tabs = [
    {
      id: 'questions' as ViewTab,
      label: 'Questions & Answers',
      icon: MessageSquare,
      description: 'Browse actual dataset content'
    },
    {
      id: 'table' as ViewTab,
      label: 'Table View',
      icon: Table,
      description: 'Interactive data table with sorting & filtering'
    },
    {
      id: 'wordcloud' as ViewTab, 
      label: 'Word Cloud',
      icon: Cloud,
      description: 'Visualize key terms and concepts'
    },
    {
      id: 'analytics' as ViewTab,
      label: 'Analytics',
      icon: BarChart3,
      description: 'Sentiment and topic analysis'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link 
            href="/upload"
            className="flex items-center gap-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Datasets
          </Link>
          
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {isLegalDataset ? 'Brett Scrhieber Legal Questions' : 'Dataset View'}
            </h1>
            <p className="text-gray-600">
              {isLegalDataset ? 'Tesla litigation Q&A analysis' : `Dataset ID: ${datasetId}`}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
            <Download className="h-4 w-4" />
            Export
          </button>
          <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
            <Settings className="h-4 w-4" />
            Settings
          </button>
        </div>
      </div>

      {/* Status Banner for Legal Dataset */}
      {isLegalDataset && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 bg-blue-500 rounded-full"></div>
            <span className="text-blue-900 font-medium">Real Legal Dataset Active</span>
          </div>
          <p className="text-blue-700 text-sm mt-1">
            Viewing 84 actual legal questions about Tesla litigation, expert witnesses, and court proceedings.
          </p>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "py-4 px-1 border-b-2 font-medium text-sm transition-colors",
                  isActive
                    ? "border-primary-500 text-primary-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                )}
              >
                <div className="flex items-center gap-2">
                  <Icon className="h-4 w-4" />
                  <span>{tab.label}</span>
                </div>
                <p className="text-xs text-gray-500 mt-1">{tab.description}</p>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <motion.div
        key={activeTab}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        {activeTab === 'questions' && (
          <DatasetViewer
            datasetId={datasetId}
            datasetName="Brett Scrhieber Legal Questions"
            className="shadow-sm"
          />
        )}

        {activeTab === 'table' && (
          <DatasetTableView
            datasetId={datasetId}
            datasetName="Brett Scrhieber Legal Questions"
          />
        )}

        {activeTab === 'wordcloud' && (
          <SimpleWordCloud
            datasetId={datasetId}
            mode="all"
            filters={wordCloudFilters}
            onWordClick={(word) => console.log('Word clicked:', word)}
          />
        )}

        {activeTab === 'analytics' && (
          <div className="bg-white rounded-lg border p-8 text-center">
            <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Advanced Analytics
            </h3>
            <p className="text-gray-600 mb-6">
              Sentiment analysis, topic modeling, and entity extraction coming soon.
            </p>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-yellow-800 text-sm">
                <strong>Your legal dataset is ready</strong> for advanced NLTK analysis including:
                legal entity extraction, sentiment analysis of court proceedings, and topic modeling 
                of litigation themes.
              </p>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}
