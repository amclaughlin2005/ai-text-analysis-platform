import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import toast from 'react-hot-toast';
import {
  ApiResponse,
  Dataset,
  Question,
  AnalysisJob,
  WordFrequency,
  ExportRequest,
  DatasetUploadForm,
  AnalysisConfigForm,
  SentimentTrend,
  TopicEvolution,
  ConversationQuality,
} from './types';

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003';
const API_TIMEOUT = 30000; // 30 seconds

// Create axios instance with default configuration
const createApiClient = (token?: string): AxiosInstance => {
  const client = axios.create({
    baseURL: API_BASE_URL,
    timeout: API_TIMEOUT,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    },
  });

  // Request interceptor for logging and token refresh
  client.interceptors.request.use(
    (config) => {
      console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
      return config;
    },
    (error) => {
      console.error('❌ API Request Error:', error);
      return Promise.reject(error);
    }
  );

  // Response interceptor for error handling
  client.interceptors.response.use(
    (response: AxiosResponse) => {
      console.log(`✅ API Response: ${response.status} ${response.config.url}`);
      return response;
    },
    (error: AxiosError) => {
      console.error(`❌ API Response Error: ${error.response?.status} ${error.config?.url}`, error.response?.data);
      
      // Handle common error cases
      if (error.response?.status === 401) {
        toast.error('Authentication required. Please log in.');
        // Redirect to login or refresh token
      } else if (error.response?.status === 403) {
        toast.error('Access forbidden. You do not have permission for this action.');
      } else if (error.response?.status === 429) {
        toast.error('Rate limit exceeded. Please try again later.');
      } else if (error.response?.status >= 500) {
        toast.error('Server error. Please try again later.');
      }
      
      return Promise.reject(error);
    }
  );

  return client;
};

// Hook to get API client (authentication disabled for now)
export const useApiClient = () => {
  return {
    getClient: async () => {
      return createApiClient();
    }
  };
};

// API Service Classes
export class DatasetService {
  static async getAll(token: string): Promise<Dataset[]> {
    const client = createApiClient(token);
    const response = await client.get<ApiResponse<Dataset[]>>('/api/datasets');
    return response.data.data || [];
  }

  static async getById(id: string, token: string): Promise<Dataset> {
    const client = createApiClient(token);
    const response = await client.get<ApiResponse<Dataset>>(`/api/datasets/${id}`);
    if (!response.data.data) {
      throw new Error('Dataset not found');
    }
    return response.data.data;
  }

  static async upload(data: DatasetUploadForm, token: string): Promise<Dataset> {
    const client = createApiClient(token);
    const formData = new FormData();
    formData.append('file', data.file);
    formData.append('name', data.name);
    if (data.description) formData.append('description', data.description);
    if (data.password) formData.append('password', data.password);

    const response = await client.post<ApiResponse<Dataset>>('/api/datasets/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    if (!response.data.data) {
      throw new Error(response.data.message || 'Upload failed');
    }
    return response.data.data;
  }

  static async delete(id: string, token: string): Promise<void> {
    const client = createApiClient(token);
    await client.delete(`/api/datasets/${id}`);
  }

  static async reprocess(id: string, config: AnalysisConfigForm, token: string): Promise<AnalysisJob> {
    const client = createApiClient(token);
    const response = await client.post<ApiResponse<AnalysisJob>>(`/api/datasets/${id}/reprocess`, config);
    if (!response.data.data) {
      throw new Error(response.data.message || 'Reprocessing failed');
    }
    return response.data.data;
  }
}

export class QuestionService {
  static async getByDatasetId(datasetId: string, token: string, page = 1, limit = 50): Promise<{
    questions: Question[];
    total: number;
    page: number;
    pages: number;
  }> {
    const client = createApiClient(token);
    const response = await client.get(`/api/datasets/${datasetId}/questions`, {
      params: { page, limit }
    });
    return response.data.data || { questions: [], total: 0, page: 1, pages: 0 };
  }

  static async getById(id: string, token: string): Promise<Question> {
    const client = createApiClient(token);
    const response = await client.get<ApiResponse<Question>>(`/api/questions/${id}`);
    if (!response.data.data) {
      throw new Error('Question not found');
    }
    return response.data.data;
  }
}

export class AnalysisService {
  static async analyzeSentiment(questionIds: string[], token: string): Promise<AnalysisJob> {
    const client = createApiClient(token);
    const response = await client.post<ApiResponse<AnalysisJob>>('/api/analysis/sentiment', {
      question_ids: questionIds
    });
    if (!response.data.data) {
      throw new Error(response.data.message || 'Analysis failed');
    }
    return response.data.data;
  }

  static async analyzeTopics(datasetId: string, numTopics: number, token: string): Promise<AnalysisJob> {
    const client = createApiClient(token);
    const response = await client.post<ApiResponse<AnalysisJob>>('/api/analysis/topics', {
      dataset_id: datasetId,
      num_topics: numTopics
    });
    if (!response.data.data) {
      throw new Error(response.data.message || 'Topic analysis failed');
    }
    return response.data.data;
  }

  static async extractEntities(questionIds: string[], token: string): Promise<AnalysisJob> {
    const client = createApiClient(token);
    const response = await client.post<ApiResponse<AnalysisJob>>('/api/analysis/entities', {
      question_ids: questionIds
    });
    if (!response.data.data) {
      throw new Error(response.data.message || 'Entity extraction failed');
    }
    return response.data.data;
  }

  static async getJobStatus(jobId: string, token: string): Promise<AnalysisJob> {
    const client = createApiClient(token);
    const response = await client.get<ApiResponse<AnalysisJob>>(`/api/analysis/jobs/${jobId}`);
    if (!response.data.data) {
      throw new Error('Job not found');
    }
    return response.data.data;
  }
}

export class WordCloudService {
  static async generate(datasetId: string, mode: string, filters: any, token: string): Promise<WordFrequency[]> {
    const client = createApiClient(token);
    const response = await client.post<ApiResponse<WordFrequency[]>>('/api/wordcloud/generate', {
      dataset_id: datasetId,
      mode,
      filters
    });
    return response.data.data || [];
  }

  static async getModes(): Promise<string[]> {
    const client = createApiClient();
    const response = await client.get<ApiResponse<{ modes: string[] }>>('/api/wordcloud/modes');
    return response.data.data?.modes || [];
  }

  static async exportWordCloud(datasetId: string, format: string, token: string): Promise<Blob> {
    const client = createApiClient(token);
    const response = await client.post(`/api/wordcloud/export`, {
      dataset_id: datasetId,
      format
    }, {
      responseType: 'blob'
    });
    return response.data;
  }
}

export class AnalyticsService {
  static async getSentimentTrends(datasetId: string, timeWindow: string, token: string): Promise<SentimentTrend[]> {
    const client = createApiClient(token);
    const response = await client.get<ApiResponse<SentimentTrend[]>>(`/api/analytics/sentiment-trends`, {
      params: { dataset_id: datasetId, time_window: timeWindow }
    });
    return response.data.data || [];
  }

  static async getTopicEvolution(datasetId: string, numTopics: number, token: string): Promise<TopicEvolution[]> {
    const client = createApiClient(token);
    const response = await client.get<ApiResponse<TopicEvolution[]>>(`/api/analytics/topic-evolution`, {
      params: { dataset_id: datasetId, num_topics: numTopics }
    });
    return response.data.data || [];
  }

  static async getConversationQuality(datasetId: string, token: string): Promise<ConversationQuality> {
    const client = createApiClient(token);
    const response = await client.get<ApiResponse<ConversationQuality>>(`/api/analytics/conversation-quality`, {
      params: { dataset_id: datasetId }
    });
    if (!response.data.data) {
      throw new Error('Quality metrics not found');
    }
    return response.data.data;
  }
}

export class ExportService {
  static async generateReport(type: 'executive' | 'technical', datasetId: string, token: string): Promise<AnalysisJob> {
    const client = createApiClient(token);
    const response = await client.post<ApiResponse<AnalysisJob>>(`/api/export/reports/${type}`, {
      dataset_id: datasetId
    });
    if (!response.data.data) {
      throw new Error(response.data.message || 'Report generation failed');
    }
    return response.data.data;
  }

  static async getFormats(): Promise<string[]> {
    const client = createApiClient();
    const response = await client.get<ApiResponse<{ formats: string[] }>>('/api/export/formats');
    return response.data.data?.formats || [];
  }

  static async exportData(request: ExportRequest, token: string): Promise<Blob> {
    const client = createApiClient(token);
    const response = await client.post('/api/export/data', request, {
      responseType: 'blob'
    });
    return response.data;
  }
}

// Utility functions
export const handleApiError = (error: any): string => {
  if (error.response?.data?.message) {
    return error.response.data.message;
  } else if (error.message) {
    return error.message;
  } else {
    return 'An unexpected error occurred';
  }
};

export const downloadBlob = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};
