'use client';

import { useState } from 'react';
import DatasetList from '@/components/datasets/DatasetList';
import { Button } from '@/components/ui/button';
import { Upload, Plus, RefreshCw } from 'lucide-react';
import Link from 'next/link';

export default function DatasetsPage() {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
  };

  const handleDatasetSelect = (datasetId: string) => {
    // Navigate to dataset view page
    window.location.href = `/dataset/${datasetId}`;
  };

  const handleDatasetDelete = (datasetId: string) => {
    // Refresh the list after deletion
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Dataset Management
              </h1>
              <p className="text-lg text-gray-600">
                Upload and manage datasets for AI-powered analysis - supports CSV Q&A format and flexible JSON/CSV with any structure
              </p>
            </div>
            
            <div className="flex items-center space-x-4">
              <Button
                onClick={handleRefresh}
                variant="outline"
                size="sm"
                className="flex items-center space-x-2"
              >
                <RefreshCw className="h-4 w-4" />
                <span>Refresh</span>
              </Button>
              
              <Link href="/upload">
                <Button className="flex items-center space-x-2">
                  <Upload className="h-4 w-4" />
                  <span>Upload New Dataset</span>
                </Button>
              </Link>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Link href="/upload">
            <div className="bg-white rounded-lg shadow-sm border-2 border-dashed border-gray-300 hover:border-primary-400 transition-colors p-6 cursor-pointer group">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-primary-100 rounded-lg group-hover:bg-primary-200 transition-colors">
                  <Upload className="h-6 w-6 text-primary-600" />
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-900">Upload</h3>
                  <p className="text-sm text-gray-500">Add new dataset</p>
                </div>
              </div>
            </div>
          </Link>

          <Link href="/upload?mode=flexible">
            <div className="bg-white rounded-lg shadow-sm border-2 border-dashed border-gray-300 hover:border-primary-400 transition-colors p-6 cursor-pointer group">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-green-100 rounded-lg group-hover:bg-green-200 transition-colors">
                  <Plus className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-900">Flexible Upload</h3>
                  <p className="text-sm text-gray-500">JSON/CSV with any structure</p>
                </div>
              </div>
            </div>
          </Link>

          <Link href="/dashboard">
            <div className="bg-white rounded-lg shadow-sm border-2 border-dashed border-gray-300 hover:border-primary-400 transition-colors p-6 cursor-pointer group">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-purple-100 rounded-lg group-hover:bg-purple-200 transition-colors">
                  <RefreshCw className="h-6 w-6 text-purple-600" />
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-900">Debug</h3>
                  <p className="text-sm text-gray-500">Connection testing</p>
                </div>
              </div>
            </div>
          </Link>
        </div>

        {/* Main Dataset List */}
        <div className="bg-white rounded-lg shadow-sm">
          <DatasetList
            key={refreshKey}
            onDatasetSelect={handleDatasetSelect}
            onDatasetDelete={handleDatasetDelete}
            className="rounded-lg"
          />
        </div>
      </div>
    </div>
  );
}
