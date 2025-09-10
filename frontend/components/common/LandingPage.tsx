'use client';

import Link from 'next/link';
import { 
  BarChart3, 
  FileText, 
  MessageSquare,
  ArrowRight,
  Upload,
  Database
} from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="bg-gray-50 min-h-screen">
      <div className="max-w-6xl mx-auto px-6 py-16">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold text-gray-900 mb-3">
            AI Text Analysis Platform
          </h1>
          <p className="text-gray-600 text-lg">
            Internal tool for analyzing legal research data and generating insights
          </p>
        </div>

        {/* Main Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Link 
            href="/dashboard"
            className="group bg-white p-6 rounded-lg border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all"
          >
            <div className="p-3 bg-blue-100 rounded-lg w-fit mb-4 group-hover:bg-blue-200 transition-colors">
              <BarChart3 className="h-6 w-6 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Analytics Dashboard</h3>
            <p className="text-gray-600 text-sm mb-4">View metrics, sentiment analysis, and insights</p>
            <div className="flex items-center text-blue-600 text-sm font-medium">
              <span>Open Dashboard</span>
              <ArrowRight className="h-4 w-4 ml-1" />
            </div>
          </Link>

          <Link 
            href="/upload"
            className="group bg-white p-6 rounded-lg border border-gray-200 hover:border-green-300 hover:shadow-md transition-all"
          >
            <div className="p-3 bg-green-100 rounded-lg w-fit mb-4 group-hover:bg-green-200 transition-colors">
              <Upload className="h-6 w-6 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Upload Dataset</h3>
            <p className="text-gray-600 text-sm mb-4">Upload CSV files for analysis</p>
            <div className="flex items-center text-green-600 text-sm font-medium">
              <span>Upload Files</span>
              <ArrowRight className="h-4 w-4 ml-1" />
            </div>
          </Link>

          <Link
            href="/wordcloud"
            className="group bg-white p-6 rounded-lg border border-gray-200 hover:border-purple-300 hover:shadow-md transition-all"
          >
            <div className="p-3 bg-purple-100 rounded-lg w-fit mb-4 group-hover:bg-purple-200 transition-colors">
              <MessageSquare className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Word Cloud</h3>
            <p className="text-gray-600 text-sm mb-4">Interactive word visualization</p>
            <div className="flex items-center text-purple-600 text-sm font-medium">
              <span>Analyze Text</span>
              <ArrowRight className="h-4 w-4 ml-1" />
            </div>
          </Link>

          <Link 
            href="/legal-wordcloud"
            className="group bg-white p-6 rounded-lg border border-gray-200 hover:border-orange-300 hover:shadow-md transition-all"
          >
            <div className="p-3 bg-orange-100 rounded-lg w-fit mb-4 group-hover:bg-orange-200 transition-colors">
              <FileText className="h-6 w-6 text-orange-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Legal Analysis</h3>
            <p className="text-gray-600 text-sm mb-4">Legal research and case analysis</p>
            <div className="flex items-center text-orange-600 text-sm font-medium">
              <span>Analyze Data</span>
              <ArrowRight className="h-4 w-4 ml-1" />
            </div>
          </Link>
        </div>

        {/* Recent Activity */}
        <div className="mt-12 bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Recent Activity</h2>
            <Link 
              href="/dashboard" 
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              View All →
            </Link>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center p-3 bg-gray-50 rounded-lg">
              <div className="p-2 bg-green-100 rounded-md mr-3">
                <Database className="h-4 w-4 text-green-600" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">Brett Schrieber Legal Questions</p>
                <p className="text-xs text-gray-600">84 questions processed • Active dataset</p>
              </div>
              <span className="text-xs text-gray-500">Active</span>
            </div>
            
            <div className="text-center py-8 text-gray-500">
              <p className="text-sm">Upload a dataset to get started with analysis</p>
              <Link 
                href="/upload" 
                className="inline-flex items-center mt-3 px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors"
              >
                <Upload className="h-4 w-4 mr-2" />
                Upload Dataset
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
