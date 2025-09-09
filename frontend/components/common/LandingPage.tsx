'use client';

import Link from 'next/link';
import { 
  BarChart3, 
  Brain, 
  FileText, 
  MessageSquare,
  ArrowRight,
  Upload,
  Zap
} from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="bg-gray-50">
      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Welcome Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Text Analysis Platform
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Analyze query-response data with advanced NLTK processing and interactive visualizations. 
            Upload datasets, generate insights, and create comprehensive reports.
          </p>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          <Link 
            href="/dashboard"
            className="group bg-white p-8 rounded-xl border border-gray-200 hover:border-primary-300 hover:shadow-lg transition-all duration-300"
          >
            <div className="flex items-center mb-4">
              <div className="p-3 bg-primary-100 rounded-lg mr-4 group-hover:bg-primary-200 transition-colors">
                <Upload className="h-8 w-8 text-primary-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
                  Upload Dataset
                </h3>
                <p className="text-gray-600">
                  Upload CSV files with query-response data for analysis
                </p>
              </div>
            </div>
            <div className="flex items-center text-primary-600 group-hover:text-primary-700">
              <span className="text-sm font-medium">Go to Dashboard</span>
              <ArrowRight className="h-4 w-4 ml-2" />
            </div>
          </Link>

          <Link
            href="/wordcloud-demo"
            className="group bg-white p-8 rounded-xl border border-gray-200 hover:border-primary-300 hover:shadow-lg transition-all duration-300"
          >
            <div className="flex items-center mb-4">
              <div className="p-3 bg-blue-100 rounded-lg mr-4 group-hover:bg-blue-200 transition-colors">
                <MessageSquare className="h-8 w-8 text-blue-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                  Word Cloud Demo
                </h3>
                <p className="text-gray-600">
                  Interactive word cloud with multiple analysis modes
                </p>
              </div>
            </div>
            <div className="flex items-center text-blue-600 group-hover:text-blue-700">
              <span className="text-sm font-medium">Try Demo</span>
              <ArrowRight className="h-4 w-4 ml-2" />
            </div>
          </Link>

          <div className="bg-white p-8 rounded-xl border border-gray-200 opacity-60">
            <div className="flex items-center mb-4">
              <div className="p-3 bg-gray-100 rounded-lg mr-4">
                <BarChart3 className="h-8 w-8 text-gray-400" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-500">
                  Analytics Dashboard
                </h3>
                <p className="text-gray-400">
                  Comprehensive analytics and reporting tools
                </p>
              </div>
            </div>
            <div className="flex items-center text-gray-400">
              <span className="text-sm font-medium">Coming Soon</span>
            </div>
          </div>
        </div>

        {/* Current Features */}
        <div className="bg-white rounded-xl border border-gray-200 p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">Current Features</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Available Features */}
            <div>
              <h4 className="text-lg font-semibold text-green-600 mb-4 flex items-center">
                <div className="h-2 w-2 bg-green-500 rounded-full mr-2"></div>
                Available Now
              </h4>
              <ul className="space-y-3">
                <li className="flex items-start">
                  <MessageSquare className="h-5 w-5 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
                  <span className="text-gray-700">Interactive word cloud visualization with 6 analysis modes</span>
                </li>
                <li className="flex items-start">
                  <Zap className="h-5 w-5 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
                  <span className="text-gray-700">Real-time search and filtering capabilities</span>
                </li>
                <li className="flex items-start">
                  <FileText className="h-5 w-5 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
                  <span className="text-gray-700">Multi-format export (PNG, SVG, PDF, CSV, JSON)</span>
                </li>
              </ul>
            </div>

            {/* Coming Soon */}
            <div>
              <h4 className="text-lg font-semibold text-amber-600 mb-4 flex items-center">
                <div className="h-2 w-2 bg-amber-500 rounded-full mr-2"></div>
                Coming Soon
              </h4>
              <ul className="space-y-3">
                <li className="flex items-start">
                  <Upload className="h-5 w-5 text-amber-500 mt-0.5 mr-3 flex-shrink-0" />
                  <span className="text-gray-600">CSV dataset upload and processing</span>
                </li>
                <li className="flex items-start">
                  <Brain className="h-5 w-5 text-amber-500 mt-0.5 mr-3 flex-shrink-0" />
                  <span className="text-gray-600">NLTK sentiment analysis and topic modeling</span>
                </li>
                <li className="flex items-start">
                  <BarChart3 className="h-5 w-5 text-amber-500 mt-0.5 mr-3 flex-shrink-0" />
                  <span className="text-gray-600">Advanced analytics dashboard</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* System Status */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center mb-3">
            <div className="h-3 w-3 bg-blue-500 rounded-full mr-3 animate-pulse"></div>
            <h4 className="text-lg font-semibold text-blue-900">System Status</h4>
          </div>
          <p className="text-blue-800 mb-3">
            Platform is in active development. Word cloud demo is fully functional with mock data.
          </p>
          <p className="text-sm text-blue-700">
            Backend API and database integration in progress. Authentication temporarily disabled for development.
          </p>
        </div>
      </div>
    </div>
  );
}
