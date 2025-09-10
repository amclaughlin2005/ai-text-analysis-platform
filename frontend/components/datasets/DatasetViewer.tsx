'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Search, 
  ChevronLeft, 
  ChevronRight, 
  Eye, 
  MessageSquare,
  Calendar,
  Copy
} from 'lucide-react';
import { cn } from '@/lib/utils';
import toast from 'react-hot-toast';

interface Question {
  number: number;
  timestamp: string;
  question: string;
  response: string;
  project_id?: string;
  user_id?: string;
}

interface DatasetViewerProps {
  datasetId: string;
  datasetName: string;
  className?: string;
}

export default function DatasetViewer({ 
  datasetName, 
  className 
}: DatasetViewerProps) {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedQuestion, setSelectedQuestion] = useState<number | null>(null);

  const questionsPerPage = 10;

  // Fetch questions from your real legal data
  const fetchQuestions = async () => {
    setLoading(true);
    try {
      // Use the dedicated legal data API
      const response = await fetch(`http://localhost:8002/questions?limit=${questionsPerPage}`);
      const data = await response.json();
      
      console.log('📋 Legal questions loaded:', data);
      
      if (data.questions) {
        setQuestions(data.questions);
        setTotalQuestions(data.pagination?.total_count || data.total_questions || questions.length);
      }
      
    } catch (error) {
      console.error('Failed to load questions:', error);
      toast.error('Failed to load questions from legal dataset');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuestions();
  }, []);

  const filteredQuestions = questions.filter(q =>
    searchQuery === '' || 
    q.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
    q.response.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const copyToClipboard = async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast.success(`${type} copied to clipboard`);
    } catch (error) {
      toast.error('Failed to copy to clipboard');
    }
  };

  if (loading) {
    return (
      <div className={cn("bg-white rounded-lg border p-8", className)}>
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/3"></div>
          {[...Array(5)].map((_, i) => (
            <div key={i} className="space-y-2">
              <div className="h-4 bg-gray-200 rounded w-full"></div>
              <div className="h-4 bg-gray-100 rounded w-3/4"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className={cn("bg-white rounded-lg border", className)}>
      {/* Header */}
      <div className="p-6 border-b">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-semibold text-gray-900">
              📋 {datasetName}
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              {totalQuestions} legal questions • Tesla litigation dataset
            </p>
          </div>
          
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search questions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent w-64"
            />
          </div>
        </div>
      </div>

      {/* Questions List */}
      <div className="divide-y divide-gray-200">
        {filteredQuestions.map((question, index) => (
          <motion.div
            key={question.number}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="p-6 hover:bg-gray-50 cursor-pointer"
            onClick={() => setSelectedQuestion(
              selectedQuestion === question.number ? null : question.number
            )}
          >
            {/* Question Header */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="bg-primary-100 text-primary-600 text-sm font-medium px-2 py-1 rounded">
                  Q{question.number}
                </div>
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <Calendar className="h-3 w-3" />
                  <span>{question.timestamp}</span>
                </div>
              </div>
              
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  copyToClipboard(question.question, 'Question');
                }}
                className="p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded"
                title="Copy question"
              >
                <Copy className="h-4 w-4" />
              </button>
            </div>

            {/* Question Text */}
            <div className="mb-4">
              <h4 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                <MessageSquare className="h-4 w-4 text-blue-500" />
                Question:
              </h4>
              <p className="text-gray-700 leading-relaxed">
                {question.question}
              </p>
            </div>

            {/* Response (Expandable) */}
            <div 
              className={cn(
                "transition-all duration-200",
                selectedQuestion === question.number ? "opacity-100" : "opacity-60"
              )}
            >
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900 flex items-center gap-2">
                  <Eye className="h-4 w-4 text-green-500" />
                  Response:
                </h4>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    copyToClipboard(question.response, 'Response');
                  }}
                  className="p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded"
                  title="Copy response"
                >
                  <Copy className="h-4 w-4" />
                </button>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-gray-700 leading-relaxed text-sm">
                  {selectedQuestion === question.number 
                    ? question.response
                    : question.response.length > 200
                      ? question.response.slice(0, 200) + '...'
                      : question.response
                  }
                </p>
                
                {question.response.length > 200 && selectedQuestion !== question.number && (
                  <button className="mt-2 text-xs text-primary-600 hover:text-primary-700">
                    Click to expand full response
                  </button>
                )}
              </div>
            </div>

            {/* Metadata */}
            {question.project_id && (
              <div className="mt-3 flex items-center gap-4 text-xs text-gray-500">
                <span>Project: {question.project_id}</span>
                {question.user_id && <span>User: {question.user_id}</span>}
              </div>
            )}
          </motion.div>
        ))}
      </div>

      {/* Pagination */}
      {totalQuestions > questionsPerPage && (
        <div className="p-6 border-t bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              Showing {Math.min(questionsPerPage, filteredQuestions.length)} of {totalQuestions} questions
            </div>
            
            <div className="flex items-center gap-2">
              <button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="p-2 text-gray-500 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              
              <span className="text-sm text-gray-600">
                Page {currentPage} of {Math.ceil(totalQuestions / questionsPerPage)}
              </span>
              
              <button
                onClick={() => setCurrentPage(currentPage + 1)}
                disabled={currentPage >= Math.ceil(totalQuestions / questionsPerPage)}
                className="p-2 text-gray-500 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {filteredQuestions.length === 0 && !loading && (
        <div className="p-12 text-center text-gray-500">
          <MessageSquare className="h-8 w-8 mx-auto mb-3 opacity-50" />
          <p>No questions found matching your search.</p>
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="mt-2 text-primary-600 hover:text-primary-700 text-sm"
            >
              Clear search
            </button>
          )}
        </div>
      )}
    </div>
  );
}
