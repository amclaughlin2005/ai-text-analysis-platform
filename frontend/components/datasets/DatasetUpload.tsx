'use client';

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Upload, 
  File, 
  X, 
  Check, 
  AlertCircle, 
  Loader2,
  FileText,
  Database,
  Lock,
  Eye,
  EyeOff
} from 'lucide-react';
import { cn, formatFileSize, validateFileType, validateFileSize } from '@/lib/utils';
import toast from 'react-hot-toast';

interface DatasetUploadProps {
  onUploadComplete?: (datasetId: string) => void;
  onUploadProgress?: (progress: number) => void;
  className?: string;
}

interface UploadFile {
  file: File;
  preview?: string;
  validation?: {
    isValid: boolean;
    errors: string[];
    warnings: string[];
  };
}

export default function DatasetUpload({
  onUploadComplete,
  onUploadProgress,
  className
}: DatasetUploadProps) {
  const [uploadFile, setUploadFile] = useState<UploadFile | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [showPreview, setShowPreview] = useState(false);
  
  // Form data
  const [datasetName, setDatasetName] = useState('');
  const [description, setDescription] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [requirePassword, setRequirePassword] = useState(false);
  
  // Preview data
  const [csvPreview, setCsvPreview] = useState<{
    headers: string[];
    rows: string[][];
    totalRows: number;
  } | null>(null);

  // File validation configuration
  const MAX_FILE_SIZE_MB = 100;
  const ALLOWED_FILE_TYPES = ['text/csv', 'application/vnd.ms-excel'];
  const ALLOWED_EXTENSIONS = ['.csv'];

  // Handle file drop
  const onDrop = useCallback(async (acceptedFiles: File[], rejectedFiles: any[]) => {
    if (rejectedFiles.length > 0) {
      const errors = rejectedFiles.map(rejection => 
        rejection.errors.map((e: any) => e.message).join(', ')
      ).join('; ');
      toast.error(`File rejected: ${errors}`);
      return;
    }

    if (acceptedFiles.length === 0) {
      return;
    }

    const file = acceptedFiles[0];
    console.log('File dropped:', file.name, file.type, formatFileSize(file.size));

    // Validate file
    const validation = validateFile(file);
    
    const uploadFileData: UploadFile = {
      file,
      validation
    };

    setUploadFile(uploadFileData);
    
    // Generate dataset name from filename if not set
    if (!datasetName) {
      const nameFromFile = file.name.replace(/\.[^/.]+$/, ""); // Remove extension
      setDatasetName(nameFromFile);
    }

    // Generate preview
    if (validation.isValid) {
      await generatePreview(file);
    }

    if (validation.isValid) {
      toast.success(`File "${file.name}" ready for upload`);
    } else {
      toast.error(`File validation failed: ${validation.errors.join(', ')}`);
    }
  }, [datasetName]);

  const validateFile = (file: File) => {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Check file type
    const hasValidType = ALLOWED_FILE_TYPES.includes(file.type) || 
                        ALLOWED_EXTENSIONS.some(ext => file.name.toLowerCase().endsWith(ext));
    
    if (!hasValidType) {
      errors.push('File must be a CSV file (.csv)');
    }

    // Check file size
    if (!validateFileSize(file, MAX_FILE_SIZE_MB)) {
      errors.push(`File size must be less than ${MAX_FILE_SIZE_MB}MB`);
    }

    // Check filename
    if (file.name.length > 100) {
      warnings.push('Filename is very long - consider shortening it');
    }

    if (!file.name.toLowerCase().endsWith('.csv')) {
      warnings.push('File extension should be .csv');
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  };

  const generatePreview = async (file: File) => {
    try {
      const text = await file.text();
      const lines = text.split('\n').filter(line => line.trim());
      
      if (lines.length === 0) {
        toast.error('CSV file appears to be empty');
        return;
      }

      // Parse CSV (simple implementation)
      const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
      const dataRows = lines.slice(1, 6).map(line => // First 5 rows for preview
        line.split(',').map(cell => cell.trim().replace(/"/g, ''))
      );

      setCsvPreview({
        headers,
        rows: dataRows,
        totalRows: lines.length - 1 // Exclude header
      });

      setShowPreview(true);
      
      console.log('CSV Preview generated:', headers, dataRows.length, 'rows');
      
    } catch (error) {
      console.error('Preview generation failed:', error);
      toast.error('Failed to generate CSV preview');
    }
  };

  const handleUpload = async () => {
    if (!uploadFile || !uploadFile.validation?.isValid) {
      toast.error('Please select a valid CSV file');
      return;
    }

    if (!datasetName.trim()) {
      toast.error('Dataset name is required');
      return;
    }

    if (requirePassword && !password.trim()) {
      toast.error('Password is required');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      // Create form data
      const formData = new FormData();
      formData.append('file', uploadFile.file);
      formData.append('name', datasetName.trim());
      if (description.trim()) {
        formData.append('description', description.trim());
      }
      if (requirePassword && password.trim()) {
        formData.append('password', password.trim());
      }

      console.log('Starting upload:', {
        filename: uploadFile.file.name,
        size: uploadFile.file.size,
        name: datasetName
      });

      // Upload to backend using centralized API URL
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://ai-text-analysis-platform-production.up.railway.app';
      const response = await fetch(`${API_BASE_URL}/api/datasets/upload`, {
        method: 'POST',
        body: formData,
        // Note: Don't set Content-Type header for FormData, let browser set it
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Upload failed with status ${response.status}`);
      }

      const result = await response.json();
      console.log('Upload successful:', result);
      
      setUploadProgress(100);
      toast.success(`Dataset "${datasetName}" uploaded successfully!`);
      
      // Reset form
      setUploadFile(null);
      setDatasetName('');
      setDescription('');
      setPassword('');
      setCsvPreview(null);
      setShowPreview(false);
      
      if (onUploadComplete) {
        onUploadComplete(result.dataset_id || result.id);
      }

    } catch (error) {
      console.error('Upload failed:', error);
      toast.error(error instanceof Error ? error.message : 'Upload failed');
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const removeFile = () => {
    setUploadFile(null);
    setCsvPreview(null);
    setShowPreview(false);
    toast.success('File removed');
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.csv']
    },
    maxSize: MAX_FILE_SIZE_MB * 1024 * 1024,
    multiple: false,
    disabled: isUploading
  });

  return (
    <div className={cn("space-y-6", className)}>
      {/* Upload Zone */}
      <div
        {...getRootProps()}
        className={cn(
          "border-2 border-dashed rounded-xl p-12 text-center transition-all duration-200 cursor-pointer",
          isDragActive ? "border-primary-500 bg-primary-50" : "border-gray-300",
          uploadFile ? "border-green-400 bg-green-50" : "",
          isUploading ? "border-gray-400 bg-gray-50 cursor-not-allowed opacity-50" : "hover:border-primary-400 hover:bg-primary-25"
        )}
      >
        <input {...getInputProps()} />
        
        <AnimatePresence mode="wait">
          {uploadFile ? (
            <motion.div
              key="file-selected"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="space-y-4"
            >
              <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                <FileText className="h-8 w-8 text-green-600" />
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{uploadFile.file.name}</h3>
                <p className="text-sm text-gray-600">
                  {formatFileSize(uploadFile.file.size)} • Ready to upload
                </p>
                
                {uploadFile.validation && (
                  <div className="mt-3">
                    {uploadFile.validation.isValid ? (
                      <div className="flex items-center gap-2 text-green-600 text-sm">
                        <Check className="h-4 w-4" />
                        <span>File validation passed</span>
                      </div>
                    ) : (
                      <div className="space-y-1">
                        {uploadFile.validation.errors.map((error, index) => (
                          <div key={index} className="flex items-center gap-2 text-red-600 text-sm">
                            <AlertCircle className="h-4 w-4" />
                            <span>{error}</span>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    {uploadFile.validation.warnings.map((warning, index) => (
                      <div key={index} className="flex items-center gap-2 text-amber-600 text-sm mt-1">
                        <AlertCircle className="h-4 w-4" />
                        <span>{warning}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  removeFile();
                }}
                disabled={isUploading}
                className="inline-flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
              >
                <X className="h-4 w-4" />
                Remove File
              </button>
            </motion.div>
          ) : (
            <motion.div
              key="upload-prompt"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="space-y-4"
            >
              <div className="mx-auto w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center">
                <Upload className="h-8 w-8 text-primary-600" />
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  {isDragActive ? 'Drop CSV file here' : 'Upload Query-Response Dataset'}
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                  Drag & drop your CSV file or click to browse
                </p>
                <p className="text-xs text-gray-500 mt-2">
                  Supports CSV files up to {MAX_FILE_SIZE_MB}MB
                </p>
              </div>
              
              <div className="flex items-center justify-center gap-4 text-xs text-gray-500">
                <span>Required columns: Question, Response</span>
                <span>•</span>
                <span>Optional: Context, Organization</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Upload Form */}
      {uploadFile && uploadFile.validation?.isValid && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="bg-white border border-gray-200 rounded-xl p-6 space-y-6"
        >
          <h4 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <Database className="h-5 w-5" />
            Dataset Information
          </h4>

          {/* Dataset Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Dataset Name *
            </label>
            <input
              type="text"
              value={datasetName}
              onChange={(e) => setDatasetName(e.target.value)}
              placeholder="Enter a descriptive name for this dataset"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              disabled={isUploading}
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description (Optional)
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe the dataset, its source, time period, etc."
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
              disabled={isUploading}
            />
          </div>

          {/* Password Protection */}
          <div className="space-y-3">
            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={requirePassword}
                onChange={(e) => setRequirePassword(e.target.checked)}
                disabled={isUploading}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <span className="text-sm font-medium text-gray-700 flex items-center gap-2">
                <Lock className="h-4 w-4" />
                Password protect this dataset
              </span>
            </label>

            {requirePassword && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="relative"
              >
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter password for dataset protection"
                  className="w-full px-4 py-2 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  disabled={isUploading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                  disabled={isUploading}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </motion.div>
            )}
          </div>

          {/* CSV Preview Toggle */}
          {csvPreview && (
            <div>
              <button
                onClick={() => setShowPreview(!showPreview)}
                className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <FileText className="h-4 w-4" />
                {showPreview ? 'Hide' : 'Show'} CSV Preview
                <span className="text-xs text-gray-500">
                  ({csvPreview.totalRows.toLocaleString()} total rows)
                </span>
              </button>
            </div>
          )}
        </motion.div>
      )}

      {/* CSV Preview */}
      <AnimatePresence>
        {showPreview && csvPreview && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-gray-50 border border-gray-200 rounded-xl p-6"
          >
            <h4 className="text-lg font-semibold text-gray-900 mb-4">CSV Preview</h4>
            
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-300">
                    {csvPreview.headers.map((header, index) => (
                      <th key={index} className="text-left py-2 px-3 font-semibold text-gray-700 bg-gray-100">
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {csvPreview.rows.map((row, rowIndex) => (
                    <tr key={rowIndex} className="border-b border-gray-200">
                      {row.map((cell, cellIndex) => (
                        <td key={cellIndex} className="py-2 px-3 text-gray-600 max-w-xs truncate">
                          {cell || '(empty)'}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            <div className="mt-4 text-sm text-gray-600">
              <p>Showing first {csvPreview.rows.length} rows of {csvPreview.totalRows.toLocaleString()} total rows</p>
              <p className="text-xs text-gray-500 mt-1">
                Headers detected: {csvPreview.headers.join(', ')}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Upload Progress */}
      {isUploading && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-blue-50 border border-blue-200 rounded-xl p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />
            <span className="text-lg font-semibold text-blue-900">Uploading Dataset</span>
          </div>
          
          <div className="space-y-3">
            <div className="flex justify-between text-sm text-blue-700">
              <span>Progress</span>
              <span>{Math.round(uploadProgress)}%</span>
            </div>
            
            <div className="w-full bg-blue-200 rounded-full h-2">
              <motion.div
                className="bg-blue-600 h-2 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${uploadProgress}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
            
            <p className="text-sm text-blue-600">
              Uploading "{datasetName}" ({formatFileSize(uploadFile?.file.size || 0)})
            </p>
          </div>
        </motion.div>
      )}

      {/* Action Buttons */}
      {uploadFile && uploadFile.validation?.isValid && !isUploading && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-4"
        >
          <button
            onClick={handleUpload}
            disabled={!datasetName.trim() || (requirePassword && !password.trim())}
            className="flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Upload className="h-4 w-4" />
            Upload Dataset
          </button>
          
          <button
            onClick={removeFile}
            className="flex items-center gap-2 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <X className="h-4 w-4" />
            Cancel
          </button>
        </motion.div>
      )}

      {/* Upload Requirements */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h5 className="font-medium text-gray-900 mb-3">CSV Format Requirements</h5>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
          <div>
            <p className="font-medium text-gray-700 mb-1">Required Columns:</p>
            <ul className="space-y-1">
              <li>• <code className="bg-gray-200 px-1 rounded">question</code> - User query/question</li>
              <li>• <code className="bg-gray-200 px-1 rounded">response</code> - AI/agent response</li>
            </ul>
          </div>
          <div>
            <p className="font-medium text-gray-700 mb-1">Optional Columns:</p>
            <ul className="space-y-1">
              <li>• <code className="bg-gray-200 px-1 rounded">context</code> - Additional context</li>
              <li>• <code className="bg-gray-200 px-1 rounded">org_id</code> - Organization ID</li>
              <li>• <code className="bg-gray-200 px-1 rounded">org_name</code> - Organization name</li>
              <li>• <code className="bg-gray-200 px-1 rounded">timestamp</code> - Question timestamp</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
