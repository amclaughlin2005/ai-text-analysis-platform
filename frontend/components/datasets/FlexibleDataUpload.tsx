'use client';

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { 
  Upload, 
  FileText, 
  Code,
  CheckCircle,
  XCircle,
  Settings,
  Eye,
  Sparkles
} from 'lucide-react';

import { 
  DataSchema, 
  SchemaField, 
  FieldRole, 
  DataType, 
  FieldMappingRequest, 
  AnalysisConfigRequest,
  SchemaMappingRequest,
  FieldSuggestions,
  AnalysisPreview
} from '../../lib/types';
import { schemaApi } from '../../lib/api';

interface FlexibleDataUploadProps {
  onUploadComplete?: (datasetId: string, schema: DataSchema) => void;
}

export default function FlexibleDataUpload({ onUploadComplete }: FlexibleDataUploadProps) {
  const [uploadStep, setUploadStep] = useState<'upload' | 'schema' | 'mapping' | 'preview'>('upload');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [datasetId, setDatasetId] = useState<string>('');
  const [schema, setSchema] = useState<DataSchema | null>(null);
  const [suggestions, setSuggestions] = useState<FieldSuggestions | null>(null);
  const [preview, setPreview] = useState<AnalysisPreview | null>(null);
  const [fieldMappings, setFieldMappings] = useState<FieldMappingRequest[]>([]);
  const [analysisConfig, setAnalysisConfig] = useState<AnalysisConfigRequest>({
    primary_text_fields: [],
    secondary_text_fields: [],
    category_fields: [],
    metadata_fields: [],
    exclude_words: ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'],
    analysis_modes: ['all', 'verbs', 'emotions']
  });
  const [isLoading, setIsLoading] = useState(false);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    // Validate file type
    const fileExtension = file.name.toLowerCase().split('.').pop();
    if (!['json', 'csv'].includes(fileExtension || '')) {
      toast.error('Please upload a JSON or CSV file');
      return;
    }

    setUploadedFile(file);
    setIsLoading(true);

    try {
      // For demo purposes, create a mock dataset ID
      // In real implementation, this would create a dataset first
      const mockDatasetId = `dataset_${Date.now()}`;
      setDatasetId(mockDatasetId);

      // Detect schema
      const response = await schemaApi.detectSchema(file, mockDatasetId);
      setSchema(response.schema);
      
      // Initialize field mappings
      const initialMappings: FieldMappingRequest[] = response.schema.fields.map(field => ({
        field_id: field.id,
        field_role: field.field_role,
        data_type: field.detected_type,
        include_in_analysis: field.include_in_analysis,
        display_name: field.display_name
      }));
      setFieldMappings(initialMappings);

      // Get AI suggestions
      const suggestionsResponse = await schemaApi.getSuggestions(mockDatasetId);
      setSuggestions(suggestionsResponse.suggestions);

      setUploadStep('schema');
      toast.success(`Schema detected: ${response.schema.fields.length} fields found`);
    } catch (error) {
      console.error('Schema detection failed:', error);
      toast.error('Failed to detect schema. Please check your file format.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/json': ['.json'],
      'text/csv': ['.csv'],
      'application/csv': ['.csv']
    },
    multiple: false,
    disabled: isLoading
  });

  const updateFieldMapping = (fieldId: string, updates: Partial<FieldMappingRequest>) => {
    setFieldMappings(prev => 
      prev.map(mapping => 
        mapping.field_id === fieldId 
          ? { ...mapping, ...updates }
          : mapping
      )
    );
  };

  const handlePreview = async () => {
    if (!schema || !datasetId) return;

    setIsLoading(true);
    try {
      const previewResponse = await schemaApi.previewAnalysis(datasetId, analysisConfig);
      setPreview(previewResponse.preview);
      setUploadStep('preview');
    } catch (error) {
      toast.error('Failed to generate preview');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveConfiguration = async () => {
    if (!schema || !datasetId) return;

    setIsLoading(true);
    try {
      const mappingRequest: SchemaMappingRequest = {
        dataset_id: datasetId,
        field_mappings: fieldMappings,
        analysis_config: analysisConfig
      };

      await schemaApi.saveMapping(mappingRequest);
      toast.success('Configuration saved successfully!');
      
      if (onUploadComplete) {
        onUploadComplete(datasetId, schema);
      }
    } catch (error) {
      toast.error('Failed to save configuration');
    } finally {
      setIsLoading(false);
    }
  };

  const getFieldRoleColor = (role: FieldRole) => {
    switch (role) {
      case 'primary_text': return 'bg-blue-100 text-blue-800';
      case 'secondary_text': return 'bg-green-100 text-green-800';
      case 'category': return 'bg-purple-100 text-purple-800';
      case 'identifier': return 'bg-gray-100 text-gray-800';
      case 'timestamp': return 'bg-yellow-100 text-yellow-800';
      case 'metadata': return 'bg-indigo-100 text-indigo-800';
      case 'ignore': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getDataTypeIcon = (type: DataType) => {
    switch (type) {
      case 'text': return '📝';
      case 'integer': case 'float': case 'number': return '🔢';
      case 'boolean': return '✅';
      case 'date': case 'datetime': return '📅';
      case 'email': return '📧';
      case 'url': return '🔗';
      default: return '📄';
    }
  };

  if (uploadStep === 'upload') {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="text-center mb-8">
          <Sparkles className="mx-auto h-12 w-12 text-blue-500 mb-4" />
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Flexible Data Upload
          </h2>
          <p className="text-lg text-gray-600">
            Upload JSON or CSV files with any structure. Our AI will detect the schema and suggest optimal analysis configurations.
          </p>
        </div>

        <motion.div
          className="relative"
          whileHover={!isLoading ? { scale: 1.02 } : {}}
          whileTap={!isLoading ? { scale: 0.98 } : {}}
        >
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-all duration-200 ${
              isDragActive 
                ? 'border-blue-400 bg-blue-50' 
                : isLoading 
                  ? 'border-gray-300 bg-gray-50 cursor-not-allowed'
                  : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50'
            }`}
        >
          <input {...getInputProps()} />
          
          {isLoading ? (
            <div className="flex flex-col items-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
              <p className="text-lg font-medium text-gray-700">Detecting schema...</p>
              <p className="text-sm text-gray-500">Analyzing your data structure</p>
            </div>
          ) : (
            <div className="flex flex-col items-center">
              <div className="flex space-x-4 mb-6">
                <Code className="h-12 w-12 text-blue-500" />
                <FileText className="h-12 w-12 text-green-500" />
              </div>
              
              <p className="text-xl font-medium text-gray-700 mb-2">
                {isDragActive ? 'Drop your file here' : 'Drop files here or click to browse'}
              </p>
              <p className="text-sm text-gray-500 mb-4">
                Supports JSON and CSV files up to 100MB
              </p>
              
              <div className="flex flex-wrap gap-2 justify-center">
                <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">JSON</span>
                <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">CSV</span>
                <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm">Any Schema</span>
              </div>
            </div>
          )}
          </div>
        </motion.div>

        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <Sparkles className="h-8 w-8 text-blue-500 mx-auto mb-2" />
            <h3 className="font-semibold text-gray-900">Smart Detection</h3>
            <p className="text-sm text-gray-600">AI analyzes your data structure and suggests field roles</p>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <Settings className="h-8 w-8 text-green-500 mx-auto mb-2" />
            <h3 className="font-semibold text-gray-900">Custom Mapping</h3>
            <p className="text-sm text-gray-600">Configure which fields to analyze and how</p>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <Eye className="h-8 w-8 text-purple-500 mx-auto mb-2" />
            <h3 className="font-semibold text-gray-900">Live Preview</h3>
            <p className="text-sm text-gray-600">See exactly what will be analyzed before processing</p>
          </div>
        </div>
      </div>
    );
  }

  if (uploadStep === 'schema' && schema) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Schema Detected</h2>
          <p className="text-gray-600">
            AI detected {schema.fields.length} fields with {(schema.confidence_score * 100).toFixed(0)}% confidence.
            Review and adjust the field roles below.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow border overflow-hidden">
          <div className="px-6 py-4 bg-gray-50 border-b">
            <h3 className="text-lg font-semibold text-gray-900">Field Configuration</h3>
          </div>
          
          <div className="divide-y divide-gray-200">
            {schema.fields.map((field) => {
              const mapping = fieldMappings.find(m => m.field_id === field.id);
              if (!mapping) return null;

              return (
                <div key={field.id} className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <span className="text-2xl">{getDataTypeIcon(field.detected_type)}</span>
                        <div>
                          <h4 className="text-lg font-medium text-gray-900">{field.field_name}</h4>
                          <p className="text-sm text-gray-500">
                            {field.detected_type} • {field.unique_count} unique values
                          </p>
                        </div>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getFieldRoleColor(field.field_role)}`}>
                          {field.field_role.replace('_', ' ')}
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">Field Role</label>
                          <select
                            value={mapping.field_role}
                            onChange={(e) => updateFieldMapping(field.id, { field_role: e.target.value as FieldRole })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          >
                            <option value="primary_text">Primary Text</option>
                            <option value="secondary_text">Secondary Text</option>
                            <option value="category">Category</option>
                            <option value="metadata">Metadata</option>
                            <option value="identifier">Identifier</option>
                            <option value="timestamp">Timestamp</option>
                            <option value="ignore">Ignore</option>
                          </select>
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">Include in Analysis</label>
                          <label className="flex items-center">
                            <input
                              type="checkbox"
                              checked={mapping.include_in_analysis}
                              onChange={(e) => updateFieldMapping(field.id, { include_in_analysis: e.target.checked })}
                              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                            />
                            <span className="ml-2 text-sm text-gray-700">Include this field</span>
                          </label>
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">Confidence</label>
                          <div className="flex items-center space-x-2">
                            <div className="flex-1 bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-blue-500 h-2 rounded-full"
                                style={{ width: `${field.confidence_score * 100}%` }}
                              ></div>
                            </div>
                            <span className="text-sm text-gray-600">{(field.confidence_score * 100).toFixed(0)}%</span>
                          </div>
                        </div>
                      </div>

                      <div className="mt-4">
                        <p className="text-sm font-medium text-gray-700 mb-1">Sample Values:</p>
                        <div className="flex flex-wrap gap-2">
                          {field.sample_values.slice(0, 5).map((value, idx) => (
                            <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs max-w-xs truncate">
                              {String(value)}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="mt-8 flex justify-between">
          <button
            onClick={() => setUploadStep('upload')}
            className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            Back to Upload
          </button>
          <button
            onClick={handlePreview}
            disabled={isLoading}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? 'Generating Preview...' : 'Preview Analysis'}
          </button>
        </div>
      </div>
    );
  }

  if (uploadStep === 'preview' && preview) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Analysis Preview</h2>
          <p className="text-gray-600">
            Review what will be analyzed with your current configuration.
          </p>
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow border p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Fields to Analyze</h3>
            <div className="space-y-3">
              {preview.fields_to_analyze.map((field, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                  <div>
                    <span className="font-medium text-gray-900">{field.display_name}</span>
                    <span className="text-sm text-gray-500 ml-2">
                      Avg length: {field.avg_length.toFixed(0)} chars
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {field.sample_values.slice(0, 3).map((value, i) => (
                      <span key={i} className="px-2 py-1 bg-white text-gray-600 rounded text-xs max-w-24 truncate">
                        {value}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow border p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Analysis Summary</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded">
                <div className="text-2xl font-bold text-blue-600">{preview.estimated_word_count.toLocaleString()}</div>
                <div className="text-sm text-gray-600">Estimated Words</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded">
                <div className="text-2xl font-bold text-green-600">{preview.fields_to_analyze.length}</div>
                <div className="text-sm text-gray-600">Text Fields</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded">
                <div className="text-2xl font-bold text-purple-600">{preview.categories_for_filtering.length}</div>
                <div className="text-sm text-gray-600">Filter Categories</div>
              </div>
            </div>
          </div>

          {preview.sample_combined_text && (
            <div className="bg-white rounded-lg shadow border p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Sample Combined Text</h3>
              <div className="bg-gray-50 p-4 rounded text-sm text-gray-700 max-h-32 overflow-y-auto">
                {preview.sample_combined_text.substring(0, 500)}
                {preview.sample_combined_text.length > 500 && '...'}
              </div>
            </div>
          )}
        </div>

        <div className="mt-8 flex justify-between">
          <button
            onClick={() => setUploadStep('schema')}
            className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            Back to Configuration
          </button>
          <button
            onClick={handleSaveConfiguration}
            disabled={isLoading}
            className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
          >
            {isLoading ? 'Saving...' : 'Save & Start Analysis'}
          </button>
        </div>
      </div>
    );
  }

  return null;
}
