// Core data types based on backend models

export interface User {
  id: string;
  clerk_user_id: string;
  email: string;
  name: string | null;
  profile_image_url: string | null;
  preferences: Record<string, any>;
  is_active: boolean;
  is_verified: boolean;
  subscription_tier: 'free' | 'pro' | 'enterprise' | 'unlimited';
  usage_quota: Record<string, number>;
  created_at: string;
  updated_at: string;
  last_login_at: string | null;
}

export type DatasetStatus = 
  | 'uploading' 
  | 'validating' 
  | 'processing' 
  | 'completed' 
  | 'failed' 
  | 'cancelled';

export interface Dataset {
  id: string;
  user_id?: string;
  name: string;
  description?: string | null;
  original_filename?: string;
  filename?: string; // Database API field
  file_size: number;
  status?: DatasetStatus;
  upload_status?: string; // Database API field
  processing_status?: string; // Database API field
  progress_percentage?: number;
  status_message?: string | null;
  total_questions?: number;
  total_rows?: number; // Database API field
  questions_count?: number; // Database API field
  processed_questions?: number;
  valid_questions?: number;
  invalid_questions?: number;
  sentiment_avg?: number | null;
  sentiment_distribution?: Record<string, number> | null;
  top_topics?: Array<{ topic: string; score: number }> | null;
  top_entities?: Array<{ entity: string; count: number }> | null;
  top_keywords?: Array<{ keyword: string; score: number }> | null;
  avg_question_length?: number | null;
  avg_response_length?: number | null;
  avg_complexity_score?: number | null;
  data_quality_score?: number | null;
  organizations_count?: number;
  organization_names?: string[] | null;
  is_public?: boolean;
  created_at: string;
  updated_at?: string;
  processing_started_at?: string | null;
  processing_completed_at?: string | null;
}

export interface Question {
  id: string;
  dataset_id: string;
  original_question: string;
  context: string | null;
  ai_response: string | null;
  org_id: string | null;
  org_name: string | null;
  user_id_from_csv: string | null;
  timestamp_from_csv: string | null;
  is_valid: boolean;
  validation_errors: Array<{ type: string; message: string; timestamp: string }> | null;
  data_quality_score: number | null;
  question_length: number | null;
  response_length: number | null;
  context_length: number | null;
  word_count_question: number | null;
  word_count_response: number | null;
  sentiment_score: number | null;
  sentiment_label: 'positive' | 'negative' | 'neutral' | null;
  sentiment_confidence: number | null;
  question_type: string | null;
  question_intent: string | null;
  complexity_score: number | null;
  urgency_level: 'low' | 'medium' | 'high' | 'urgent' | null;
  response_relevance_score: number | null;
  response_completeness_score: number | null;
  response_quality_score: number | null;
  query_response_similarity: number | null;
  readability_question: number | null;
  readability_response: number | null;
  csv_row_number: number | null;
  created_at: string;
  updated_at: string;
  processed_at: string | null;
}

export type JobType =
  | 'dataset_upload'
  | 'dataset_processing'
  | 'sentiment_analysis'
  | 'topic_modeling'
  | 'entity_extraction'
  | 'keyword_extraction'
  | 'classification'
  | 'word_cloud_generation'
  | 'report_generation'
  | 'data_export'
  | 'dataset_reprocessing';

export type JobStatus = 
  | 'pending'
  | 'queued'
  | 'running'
  | 'completed'
  | 'failed'
  | 'cancelled'
  | 'retry';

export type JobPriority = 'low' | 'normal' | 'high' | 'urgent';

export interface AnalysisJob {
  id: string;
  user_id: string;
  dataset_id: string | null;
  job_type: JobType;
  job_name: string;
  job_description: string | null;
  status: JobStatus;
  priority: JobPriority;
  progress_percentage: number;
  current_step: string | null;
  total_steps: number | null;
  retry_count: number;
  max_retries: number;
  estimated_duration: number | null;
  actual_duration: number | null;
  started_at: string | null;
  completed_at: string | null;
  depends_on_job_id: string | null;
  job_group_id: string | null;
  queue_name: string;
  worker_name: string | null;
  created_at: string;
  updated_at: string;
  error_summary?: string;
}

export interface WordFrequency {
  id: string;
  dataset_id: string;
  analysis_mode: 'all' | 'verbs' | 'themes' | 'emotions' | 'entities' | 'topics';
  word: string;
  frequency: number;
  normalized_frequency: number | null;
  word_type: string | null;
  sentiment_association: 'positive' | 'negative' | 'neutral' | null;
  theme_category: string | null;
  tfidf_score: number | null;
  significance_score: number | null;
  context_examples: string[] | null;
  co_occurrence_words: string[] | null;
  created_at: string;
}

export interface NLTKAnalysis {
  id: string;
  question_id: string;
  entities: {
    persons: string[];
    organizations: string[];
    locations: string[];
    misc: string[];
  } | null;
  topics: Array<{
    topic_id: number;
    words: string[];
    score: number;
  }> | null;
  keywords_tfidf: Array<{
    word: string;
    score: number;
  }> | null;
  keywords_yake: Array<{
    phrase: string;
    score: number;
  }> | null;
  pos_summary: Record<string, number> | null;
  created_at: string;
  updated_at: string;
}

// API Response types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  errors?: Record<string, string[]>;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
  };
}

// WebSocket message types
export interface WebSocketMessage {
  type: string;
  data: any;
}

export interface JobUpdateMessage extends WebSocketMessage {
  type: 'job_update';
  data: {
    job_id: string;
    status: JobStatus;
    progress: number;
    message?: string;
    error?: string;
  };
}

export interface DatasetUpdateMessage extends WebSocketMessage {
  type: 'dataset_update';
  data: {
    dataset_id: string;
    status: DatasetStatus;
    progress: number;
    processed_questions: number;
    message?: string;
  };
}

// Word Cloud types
export interface WordCloudFilters {
  orgId?: string;
  orgName?: string;
  sentiment?: 'positive' | 'negative' | 'neutral';
  dateRange?: { start: Date; end: Date };
  questionType?: string;
  complexityRange?: [number, number];
  excludeWords?: string[];
  maxWords?: number;
}

export interface WordCloudData {
  word: string;
  frequency: number;
  sentiment: 'positive' | 'negative' | 'neutral' | null;
  category: string | null;
  size: number;
  color: string;
  position?: { x: number; y: number };
}

export interface WordCloudProps {
  mode: 'all' | 'verbs' | 'themes' | 'emotions' | 'entities' | 'topics';
  filters: WordCloudFilters;
  interactiveMode?: boolean;
  onWordClick?: (word: string, data: WordCloudData) => void;
  onThemeClick?: (theme: string) => void;
}

// Analytics types
export interface SentimentTrend {
  date: string;
  positive: number;
  negative: number;
  neutral: number;
  total: number;
}

export interface TopicEvolution {
  topic: string;
  dates: Array<{
    date: string;
    score: number;
    frequency: number;
  }>;
}

export interface ConversationQuality {
  dataset_id: string;
  avg_relevance: number;
  avg_completeness: number;
  avg_similarity: number;
  overall_quality: number;
  total_conversations: number;
}

// Export types
export type ExportFormat = 'PDF' | 'Excel' | 'PowerPoint' | 'JSON' | 'CSV' | 'PNG' | 'SVG';

export interface ExportRequest {
  dataset_id: string;
  format: ExportFormat;
  include_raw_data: boolean;
  include_analysis: boolean;
  filters?: WordCloudFilters;
}

// Form types
export interface DatasetUploadForm {
  name: string;
  description?: string;
  file: File;
  password?: string;
}

export interface AnalysisConfigForm {
  include_sentiment: boolean;
  include_topics: boolean;
  include_entities: boolean;
  include_keywords: boolean;
  num_topics?: number;
  custom_stopwords?: string;
}

// UI Component types
export interface TableColumn<T> {
  key: keyof T;
  header: string;
  sortable?: boolean;
  render?: (value: any, row: T) => React.ReactNode;
}

export interface FilterOption {
  label: string;
  value: string;
  count?: number;
}

export interface ChartDataPoint {
  name: string;
  value: number;
  color?: string;
  [key: string]: any;
}

// Error types
export interface AppError {
  message: string;
  code?: string;
  details?: Record<string, any>;
  timestamp: string;
}
