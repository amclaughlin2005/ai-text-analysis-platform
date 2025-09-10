'use client';

import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, Loader2, AlertCircle } from 'lucide-react';

interface TestResult {
  name: string;
  status: 'pending' | 'success' | 'error';
  message: string;
  details?: any;
  duration?: number;
}

export default function ConnectionTest() {
  const [tests, setTests] = useState<TestResult[]>([
    { name: 'Backend Connection', status: 'pending', message: 'Testing...' },
    { name: 'CORS Headers', status: 'pending', message: 'Testing...' },
    { name: 'Datasets API', status: 'pending', message: 'Testing...' },
    { name: 'Word Cloud API', status: 'pending', message: 'Testing...' },
    { name: 'Upload Endpoint', status: 'pending', message: 'Testing...' }
  ]);

  const updateTest = (index: number, update: Partial<TestResult>) => {
    setTests(prev => prev.map((test, i) => i === index ? { ...test, ...update } : test));
  };

  const runTests = async () => {
    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://ai-text-analysis-production.up.railway.app';
    console.log('🧪 Starting connection tests with API_BASE_URL:', API_BASE_URL);

    // Test 1: Basic backend connection
    try {
      const start = Date.now();
      const response = await fetch(`${API_BASE_URL}/`);
      const data = await response.json();
      const duration = Date.now() - start;
      
      updateTest(0, {
        status: 'success',
        message: 'Backend is responding',
        details: { status: response.status, message: data.message },
        duration
      });
    } catch (error) {
      updateTest(0, {
        status: 'error',
        message: `Connection failed: ${error}`,
        details: { error: String(error) }
      });
      return; // Stop tests if basic connection fails
    }

    // Test 2: CORS Headers
    try {
      const start = Date.now();
      const response = await fetch(`${API_BASE_URL}/api/test-frontend-connection`);
      const data = await response.json();
      const duration = Date.now() - start;
      
      updateTest(1, {
        status: 'success',
        message: 'CORS working correctly',
        details: data,
        duration
      });
    } catch (error) {
      updateTest(1, {
        status: 'error',
        message: `CORS test failed: ${error}`,
        details: { error: String(error) }
      });
    }

    // Test 3: Datasets API
    try {
      const start = Date.now();
      const response = await fetch(`${API_BASE_URL}/api/datasets`);
      const data = await response.json();
      const duration = Date.now() - start;
      
      updateTest(2, {
        status: 'success',
        message: `Found ${data.data?.datasets?.length || 0} datasets`,
        details: { datasets_count: data.data?.datasets?.length || 0 },
        duration
      });
    } catch (error) {
      updateTest(2, {
        status: 'error',
        message: `Datasets API failed: ${error}`,
        details: { error: String(error) }
      });
    }

    // Test 4: Word Cloud API
    try {
      const start = Date.now();
      const response = await fetch(`${API_BASE_URL}/api/wordcloud/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dataset_id: 'test', mode: 'all' })
      });
      const data = await response.json();
      const duration = Date.now() - start;
      
      updateTest(3, {
        status: 'success',
        message: `Generated ${data.words?.length || 0} words`,
        details: { words_count: data.words?.length || 0 },
        duration
      });
    } catch (error) {
      updateTest(3, {
        status: 'error',
        message: `Word cloud API failed: ${error}`,
        details: { error: String(error) }
      });
    }

    // Test 5: Upload endpoint (without file)
    try {
      const start = Date.now();
      const formData = new FormData();
      formData.append('name', 'Test Connection');
      formData.append('description', 'Testing upload endpoint');
      
      const response = await fetch(`${API_BASE_URL}/api/datasets/upload`, {
        method: 'POST',
        body: formData
      });
      
      const duration = Date.now() - start;
      
      if (response.status === 422) {
        // Expected error - no file provided
        updateTest(4, {
          status: 'success',
          message: 'Upload endpoint accessible (422 expected)',
          details: { status: response.status, note: 'No file provided - expected error' },
          duration
        });
      } else {
        const data = await response.json();
        updateTest(4, {
          status: 'error',
          message: `Unexpected response: ${response.status}`,
          details: data,
          duration
        });
      }
    } catch (error) {
      updateTest(4, {
        status: 'error',
        message: `Upload endpoint test failed: ${error}`,
        details: { error: String(error) }
      });
    }
  };

  useEffect(() => {
    runTests();
  }, []);

  const getIcon = (status: TestResult['status']) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />;
    }
  };

  const allTestsComplete = tests.every(t => t.status !== 'pending');
  const hasErrors = tests.some(t => t.status === 'error');

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">
          Frontend-Backend Connection Test
        </h3>
        <button
          onClick={runTests}
          disabled={!allTestsComplete}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors text-sm"
        >
          Retry Tests
        </button>
      </div>

      <div className="space-y-4">
        {tests.map((test, index) => (
          <div key={index} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
            <div className="flex-shrink-0 mt-0.5">
              {getIcon(test.status)}
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-medium text-gray-900">{test.name}</h4>
                {test.duration && (
                  <span className="text-xs text-gray-500">{test.duration}ms</span>
                )}
              </div>
              <p className="text-sm text-gray-600 mt-1">{test.message}</p>
              
              {test.details && (
                <details className="mt-2">
                  <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700">
                    View Details
                  </summary>
                  <pre className="mt-1 text-xs text-gray-600 bg-gray-100 p-2 rounded overflow-auto">
                    {JSON.stringify(test.details, null, 2)}
                  </pre>
                </details>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Summary */}
      {allTestsComplete && (
        <div className={`mt-6 p-4 rounded-lg ${hasErrors ? 'bg-red-50 border border-red-200' : 'bg-green-50 border border-green-200'}`}>
          <div className="flex items-center gap-2">
            {hasErrors ? (
              <AlertCircle className="h-5 w-5 text-red-600" />
            ) : (
              <CheckCircle className="h-5 w-5 text-green-600" />
            )}
            <span className={`font-medium ${hasErrors ? 'text-red-900' : 'text-green-900'}`}>
              {hasErrors ? 'Connection Issues Detected' : 'All Tests Passed!'}
            </span>
          </div>
          <p className={`text-sm mt-1 ${hasErrors ? 'text-red-700' : 'text-green-700'}`}>
            {hasErrors 
              ? 'Some tests failed. Check the details above and verify both servers are running.'
              : 'Frontend and backend are communicating correctly. Upload should work!'
            }
          </p>
        </div>
      )}

      {/* Environment Info */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 className="font-medium text-blue-900 mb-2">Environment Info</h4>
        <div className="text-sm text-blue-700 space-y-1">
          <div>API Base URL: {process.env.NEXT_PUBLIC_API_URL || 'https://ai-text-analysis-production.up.railway.app'}</div>
          <div>WS URL: {process.env.NEXT_PUBLIC_WS_URL || 'wss://ai-text-analysis-production.up.railway.app'}</div>
          <div>Current Time: {new Date().toISOString()}</div>
        </div>
      </div>
    </div>
  );
}
