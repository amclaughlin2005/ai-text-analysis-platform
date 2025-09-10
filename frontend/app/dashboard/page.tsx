'use client';

import { useState } from 'react';
import Link from 'next/link';
import AnalyticsDashboard from '@/components/dashboard/AnalyticsDashboard';
import DatasetList from '@/components/datasets/DatasetList';
import { BarChart3, Database, Upload, Cloud } from 'lucide-react';

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState('analytics');

  return (
    <div className="bg-gray-50 min-h-full">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            AI Text Analysis Dashboard
          </h1>
          <p className="mt-2 text-lg text-gray-600">
            Comprehensive analytics and insights from your legal research data
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('analytics')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'analytics'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <BarChart3 className="w-4 h-4 inline mr-2" />
                Analytics
              </button>
              <button
                onClick={() => setActiveTab('datasets')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'datasets'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Database className="w-4 h-4 inline mr-2" />
                My Datasets
              </button>
              <Link
                href="/upload"
                className="py-2 px-1 border-b-2 border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 font-medium text-sm"
              >
                <Upload className="w-4 h-4 inline mr-2" />
                Upload
              </Link>
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'analytics' && (
          <AnalyticsDashboard className="animate-fade-in" />
        )}

        {activeTab === 'datasets' && (
          <div className="animate-fade-in">
            <DatasetList />
            
            {/* Quick Actions */}
            <div className="mt-8 bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Quick Actions
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <Link 
                  href="/upload"
                  className="flex items-center justify-center p-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Upload className="w-5 h-5 mr-2" />
                  Upload New Dataset
                </Link>
                <Link 
                  href="/wordcloud"
                  className="flex items-center justify-center p-4 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                >
                  <Cloud className="w-5 h-5 mr-2" />
                  Word Cloud
                </Link>
                <button 
                  onClick={() => setActiveTab('analytics')}
                  className="flex items-center justify-center p-4 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  <BarChart3 className="w-5 h-5 mr-2" />
                  View Analytics
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
