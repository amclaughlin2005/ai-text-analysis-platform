'use client';

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { Upload, FileText, X, Plus, AlertCircle, CheckCircle2, Database } from 'lucide-react';
import toast from 'react-hot-toast';

interface AppendDataUploadProps {
  datasetId: string;
  datasetName: string;
  onUploadComplete?: (datasetId: string, questionsAdded: number) => void;
  onUploadError?: (error: string) => void;
  onCancel?: () => void;
}

export default function AppendDataUpload({
  datasetId,
  datasetName,
  onUploadComplete,
  onUploadError,
  onCancel
}: AppendDataUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      
      // Validate file type
      if (!file.name.toLowerCase().endsWith('.csv') && !file.name.toLowerCase().endsWith('.json')) {
        toast.error('Only CSV and JSON files are supported');
        return;
      }
      
      // Validate file size (2GB limit)
      if (file.size > 2 * 1024 * 1024 * 1024) {
        toast.error('File size cannot exceed 2GB');
        return;
      }
      
      setSelectedFile(file);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/json': ['.json']
    },
    multiple: false,
    maxSize: 2 * 1024 * 1024 * 1024 // 2GB
  });

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error('Please select a file to upload');
      return;
    }

    setUploading(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://ai-text-analysis-production.up.railway.app';
      
      const response = await fetch(`${API_BASE_URL}/api/datasets/${datasetId}/append`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Upload failed: ${response.status}`);
      }

      const result = await response.json();
      setUploadProgress(100);
      
      toast.success(`Successfully added ${result.questions_added} questions to "${datasetName}"`);
      
      if (onUploadComplete) {
        onUploadComplete(datasetId, result.questions_added);
      }

    } catch (error) {
      console.error('Append upload failed:', error);
      const errorMessage = error instanceof Error ? error.message : 'Append failed';
      toast.error(errorMessage);
      
      if (onUploadError) {
        onUploadError(errorMessage);
      }
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="flex items-center justify-center space-x-2 mb-4">
          <Plus className="h-8 w-8 text-primary-600" />
          <Database className="h-8 w-8 text-primary-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Add More Data
        </h2>
        <p className="text-lg text-gray-600 mb-1">
          Appending to: <span className="font-semibold text-primary-600">"{datasetName}"</span>
        </p>
        <p className="text-sm text-gray-500">
          Upload additional CSV or JSON files to expand your existing dataset
        </p>
      </div>

      {/* File Upload Area */}
      <div className="bg-white rounded-lg border-2 border-dashed border-gray-300 p-8">
        <div
          {...getRootProps()}
          className={`cursor-pointer transition-colors ${
            isDragActive ? 'border-primary-500 bg-primary-50' : 'hover:border-primary-400'
          }`}
        >
          <input {...getInputProps()} />
          
          <div className="text-center">
            <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {isDragActive ? 'Drop your file here' : 'Upload additional data'}
            </h3>
            <p className="text-gray-600 mb-4">
              Drag and drop a CSV or JSON file, or click to browse
            </p>
            <div className="text-sm text-gray-500">
              <p>• Supported formats: CSV, JSON</p>
              <p>• Maximum file size: 2GB</p>
              <p>• Data will be added to existing questions</p>
            </div>
          </div>
        </div>
      </div>

      {/* Selected File Display */}
      {selectedFile && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-lg border p-4"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <FileText className="h-8 w-8 text-primary-600" />
              <div>
                <h4 className="font-medium text-gray-900">{selectedFile.name}</h4>
                <p className="text-sm text-gray-500">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            <button
              onClick={removeFile}
              className="p-2 text-gray-400 hover:text-red-500 transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </motion.div>
      )}

      {/* Upload Progress */}
      {uploading && (
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center space-x-3 mb-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>
            <span className="text-sm font-medium text-gray-900">
              Appending data to dataset...
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex items-center space-x-4">
        <button
          onClick={handleUpload}
          disabled={!selectedFile || uploading}
          className="flex-1 flex items-center justify-center space-x-2 px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Plus className="h-5 w-5" />
          <span>{uploading ? 'Adding Data...' : 'Add to Dataset'}</span>
        </button>
        
        {onCancel && (
          <button
            onClick={onCancel}
            disabled={uploading}
            className="px-6 py-3 text-gray-700 border border-gray-300 rounded-lg font-medium hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Cancel
          </button>
        )}
      </div>

      {/* Info Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
          <div className="text-sm text-blue-800">
            <p className="font-medium mb-1">How appending works:</p>
            <ul className="space-y-1 text-blue-700">
              <li>• New questions will be added to your existing dataset</li>
              <li>• File format should match your original data structure</li>
              <li>• Question and response columns will be automatically detected</li>
              <li>• Dataset statistics will be updated automatically</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
