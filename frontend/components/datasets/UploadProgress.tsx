'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  Loader2, 
  Clock,
  FileText,
  Database,
  Brain,
  BarChart3
} from 'lucide-react';
import { JobStatus, AnalysisJob } from '@/lib/types';
import { cn, formatRelativeTime, formatNumber } from '@/lib/utils';

interface UploadProgressProps {
  jobId?: string;
  datasetId?: string;
  onComplete?: (result: any) => void;
  onError?: (error: string) => void;
  className?: string;
}

interface ProgressStep {
  id: string;
  label: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress?: number;
  startTime?: string;
  endTime?: string;
}

export default function UploadProgress({
  jobId,
  datasetId,
  onComplete,
  onError,
  className
}: UploadProgressProps) {
  const [steps, setSteps] = useState<ProgressStep[]>([
    {
      id: 'upload',
      label: 'File Upload',
      description: 'Uploading CSV file to server',
      status: 'running',
      progress: 0
    },
    {
      id: 'validation',
      label: 'Data Validation',
      description: 'Validating CSV format and content',
      status: 'pending'
    },
    {
      id: 'processing',
      label: 'Text Analysis',
      description: 'Running NLTK sentiment and entity analysis',
      status: 'pending'
    },
    {
      id: 'completion',
      label: 'Finalization',
      description: 'Generating insights and saving results',
      status: 'pending'
    }
  ]);

  const [currentJob, setCurrentJob] = useState<AnalysisJob | null>(null);
  const [overallProgress, setOverallProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('Starting upload...');
  const [estimatedTimeRemaining, setEstimatedTimeRemaining] = useState<string | null>(null);

  // Simulate upload progress for demo (replace with real WebSocket connection)
  useEffect(() => {
    if (!jobId && !datasetId) {
      simulateUploadProgress();
    }
  }, [jobId, datasetId]);

  const simulateUploadProgress = () => {
    const progressSteps = [
      { stepId: 'upload', progress: 100, message: 'File uploaded successfully', delay: 2000 },
      { stepId: 'validation', progress: 100, message: 'CSV validation completed', delay: 3000 },
      { stepId: 'processing', progress: 50, message: 'Analyzing sentiment...', delay: 2000 },
      { stepId: 'processing', progress: 80, message: 'Extracting entities...', delay: 2000 },
      { stepId: 'processing', progress: 100, message: 'Text analysis completed', delay: 1000 },
      { stepId: 'completion', progress: 100, message: 'Dataset ready for analysis!', delay: 1000 }
    ];

    let currentStepIndex = 0;

    const runNextStep = () => {
      if (currentStepIndex >= progressSteps.length) {
        // All steps completed
        setOverallProgress(100);
        setStatusMessage('Upload completed successfully!');
        
        if (onComplete) {
          onComplete({ datasetId: 'demo-dataset-new', status: 'completed' });
        }
        return;
      }

      const step = progressSteps[currentStepIndex];
      
      setTimeout(() => {
        setSteps(prev => prev.map(s => {
          if (s.id === step.stepId) {
            return {
              ...s,
              status: step.progress === 100 ? 'completed' : 'running',
              progress: step.progress,
              startTime: s.startTime || new Date().toISOString(),
              endTime: step.progress === 100 ? new Date().toISOString() : undefined
            };
          } else if (s.status === 'running' && s.id !== step.stepId) {
            // Mark previous steps as completed
            const stepOrder = ['upload', 'validation', 'processing', 'completion'];
            const currentIndex = stepOrder.indexOf(step.stepId);
            const sIndex = stepOrder.indexOf(s.id);
            if (sIndex < currentIndex) {
              return { ...s, status: 'completed' as const, progress: 100 };
            }
          }
          return s;
        }));

        setStatusMessage(step.message);
        setOverallProgress((currentStepIndex + (step.progress / 100)) / progressSteps.length * 100);
        
        currentStepIndex++;
        runNextStep();
      }, step.delay);
    };

    runNextStep();
  };

  // Get step icon
  const getStepIcon = (step: ProgressStep) => {
    switch (step.status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'running':
        return <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Clock className="h-5 w-5 text-gray-400" />;
    }
  };

  // Get step color
  const getStepColor = (step: ProgressStep) => {
    switch (step.status) {
      case 'completed':
        return 'text-green-600';
      case 'running':
        return 'text-blue-600';
      case 'failed':
        return 'text-red-600';
      default:
        return 'text-gray-500';
    }
  };

  const formatDuration = (startTime?: string, endTime?: string) => {
    if (!startTime) return '';
    
    const start = new Date(startTime);
    const end = endTime ? new Date(endTime) : new Date();
    const duration = Math.round((end.getTime() - start.getTime()) / 1000);
    
    if (duration < 60) {
      return `${duration}s`;
    } else {
      return `${Math.round(duration / 60)}m ${duration % 60}s`;
    }
  };

  return (
    <div className={cn("bg-white border border-gray-200 rounded-xl p-6", className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Upload Progress</h3>
        <div className="text-right">
          <div className="text-2xl font-bold text-primary-600">
            {Math.round(overallProgress)}%
          </div>
          <div className="text-xs text-gray-500">Complete</div>
        </div>
      </div>

      {/* Overall Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>{statusMessage}</span>
          {estimatedTimeRemaining && (
            <span>~{estimatedTimeRemaining} remaining</span>
          )}
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-3">
          <motion.div
            className="bg-gradient-to-r from-primary-500 to-blue-500 h-3 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${overallProgress}%` }}
            transition={{ duration: 0.5, ease: "easeOut" }}
          />
        </div>
      </div>

      {/* Step Progress */}
      <div className="space-y-4">
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-start gap-4">
            {/* Step Icon */}
            <div className="flex-shrink-0 mt-1">
              {getStepIcon(step)}
            </div>

            {/* Step Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <h4 className={cn("text-sm font-medium", getStepColor(step))}>
                  {step.label}
                </h4>
                <div className="text-xs text-gray-500">
                  {step.status === 'running' && step.progress !== undefined && (
                    <span>{step.progress}%</span>
                  )}
                  {step.startTime && (
                    <span className="ml-2">{formatDuration(step.startTime, step.endTime)}</span>
                  )}
                </div>
              </div>
              
              <p className="text-sm text-gray-600 mt-1">{step.description}</p>
              
              {/* Individual step progress */}
              {step.status === 'running' && step.progress !== undefined && (
                <div className="mt-2">
                  <div className="w-full bg-gray-200 rounded-full h-1.5">
                    <motion.div
                      className="bg-blue-500 h-1.5 rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${step.progress}%` }}
                      transition={{ duration: 0.3 }}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Processing Details */}
      {currentJob && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg"
        >
          <div className="flex items-center gap-2 mb-2">
            <Brain className="h-4 w-4 text-blue-600" />
            <span className="text-sm font-medium text-blue-900">Analysis Details</span>
          </div>
          
          {currentJob.current_step && (
            <p className="text-sm text-blue-700">{currentJob.current_step}</p>
          )}
          
          <div className="grid grid-cols-2 gap-4 mt-3 text-xs text-blue-600">
            <div>
              <span className="font-medium">Job ID:</span> {currentJob.id.slice(0, 8)}...
            </div>
            <div>
              <span className="font-medium">Type:</span> {currentJob.job_type}
            </div>
          </div>
        </motion.div>
      )}

      {/* Error State */}
      {steps.some(s => s.status === 'failed') && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg"
        >
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="h-4 w-4 text-red-600" />
            <span className="text-sm font-medium text-red-900">Upload Failed</span>
          </div>
          
          <p className="text-sm text-red-700">
            An error occurred during the upload process. Please try again.
          </p>
          
          <button
            onClick={() => {
              // Reset and retry
              setSteps(prev => prev.map(s => ({ ...s, status: 'pending' as const, progress: undefined })));
              setOverallProgress(0);
              simulateUploadProgress();
            }}
            className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm"
          >
            Retry Upload
          </button>
        </motion.div>
      )}

      {/* Success State */}
      {overallProgress === 100 && steps.every(s => s.status === 'completed') && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg"
        >
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <span className="text-sm font-medium text-green-900">Upload Completed!</span>
          </div>
          
          <p className="text-sm text-green-700">
            Your dataset has been successfully uploaded and is ready for analysis.
          </p>
          
          <div className="flex gap-3 mt-4">
            <button
              onClick={() => window.location.href = '/dashboard'}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
            >
              View Dashboard
            </button>
            <button
              onClick={() => window.location.href = '/wordcloud-demo'}
              className="px-4 py-2 border border-green-600 text-green-600 rounded-lg hover:bg-green-50 transition-colors text-sm"
            >
              Generate Word Cloud
            </button>
          </div>
        </motion.div>
      )}
    </div>
  );
}
