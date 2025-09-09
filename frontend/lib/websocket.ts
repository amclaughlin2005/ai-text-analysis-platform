import React from 'react';
import { io, Socket } from 'socket.io-client';
import toast from 'react-hot-toast';
import {
  WebSocketMessage,
  JobUpdateMessage,
  DatasetUpdateMessage,
  JobStatus,
  DatasetStatus,
} from './types';

// WebSocket Configuration
const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
const RECONNECT_ATTEMPTS = 5;
const RECONNECT_INTERVAL = 3000; // 3 seconds

export interface WebSocketOptions {
  userId?: string;
  datasetId?: string;
  jobId?: string;
  autoConnect?: boolean;
}

export class WebSocketClient {
  private socket: Socket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = RECONNECT_ATTEMPTS;
  private reconnectInterval = RECONNECT_INTERVAL;
  private listeners: Map<string, Set<Function>> = new Map();
  private options: WebSocketOptions;

  constructor(options: WebSocketOptions = {}) {
    this.options = { autoConnect: true, ...options };
    
    if (this.options.autoConnect) {
      this.connect();
    }
  }

  connect(): void {
    if (this.socket?.connected) {
      console.log('WebSocket already connected');
      return;
    }

    try {
      // Build connection URL with query parameters
      const queryParams = new URLSearchParams();
      if (this.options.userId) queryParams.set('user_id', this.options.userId);
      if (this.options.datasetId) queryParams.set('dataset_id', this.options.datasetId);
      if (this.options.jobId) queryParams.set('job_id', this.options.jobId);

      const connectionUrl = `${WS_BASE_URL}/ws/connect?${queryParams.toString()}`;

      this.socket = io(connectionUrl, {
        transports: ['websocket', 'polling'],
        timeout: 10000,
        reconnection: true,
        reconnectionAttempts: this.maxReconnectAttempts,
        reconnectionDelay: this.reconnectInterval,
      });

      this.setupEventListeners();
      console.log('🔌 WebSocket connection initiated');

    } catch (error) {
      console.error('❌ WebSocket connection failed:', error);
      this.handleConnectionError();
    }
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      console.log('🔌 WebSocket disconnected');
    }
    this.listeners.clear();
  }

  private setupEventListeners(): void {
    if (!this.socket) return;

    // Connection events
    this.socket.on('connect', () => {
      console.log('✅ WebSocket connected');
      this.reconnectAttempts = 0;
      this.emit('connection_established', { connected: true });
      toast.success('Connected to real-time updates');
    });

    this.socket.on('disconnect', (reason) => {
      console.log('🔌 WebSocket disconnected:', reason);
      this.emit('connection_lost', { reason });
      
      if (reason === 'io server disconnect') {
        // Server initiated disconnect, don't reconnect automatically
        toast.error('Connection closed by server');
      } else {
        toast.error('Connection lost. Attempting to reconnect...');
      }
    });

    this.socket.on('connect_error', (error) => {
      console.error('❌ WebSocket connection error:', error);
      this.handleConnectionError();
    });

    this.socket.on('reconnect', (attemptNumber) => {
      console.log(`✅ WebSocket reconnected after ${attemptNumber} attempts`);
      toast.success('Reconnected to real-time updates');
      this.emit('reconnected', { attempts: attemptNumber });
    });

    this.socket.on('reconnect_error', (error) => {
      console.error('❌ WebSocket reconnection error:', error);
      this.reconnectAttempts++;
      
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        toast.error('Unable to reconnect. Please refresh the page.');
      }
    });

    // Custom message handlers
    this.socket.on('job_update', (data: JobUpdateMessage['data']) => {
      console.log('📊 Job update received:', data);
      this.handleJobUpdate(data);
    });

    this.socket.on('dataset_update', (data: DatasetUpdateMessage['data']) => {
      console.log('📁 Dataset update received:', data);
      this.handleDatasetUpdate(data);
    });

    this.socket.on('analysis_complete', (data: any) => {
      console.log('✅ Analysis complete:', data);
      this.handleAnalysisComplete(data);
    });

    this.socket.on('error', (data: any) => {
      console.error('❌ WebSocket error:', data);
      this.handleError(data);
    });

    // Generic message handler
    this.socket.onAny((eventName: string, data: any) => {
      console.log(`📨 WebSocket event: ${eventName}`, data);
      this.emit(eventName, data);
    });
  }

  private handleConnectionError(): void {
    this.emit('connection_error', { 
      attempts: this.reconnectAttempts,
      maxAttempts: this.maxReconnectAttempts 
    });
  }

  private handleJobUpdate(data: JobUpdateMessage['data']): void {
    this.emit('job_update', data);
    
    // Show appropriate toast based on job status
    switch (data.status) {
      case 'running':
        if (data.progress && data.progress % 25 === 0) {
          toast.loading(`Processing: ${data.progress}%`, { id: data.job_id });
        }
        break;
      case 'completed':
        toast.success('Analysis completed!', { id: data.job_id });
        break;
      case 'failed':
        toast.error(data.error || 'Analysis failed', { id: data.job_id });
        break;
    }
  }

  private handleDatasetUpdate(data: DatasetUpdateMessage['data']): void {
    this.emit('dataset_update', data);
    
    // Show progress updates
    if (data.status === 'processing' && data.progress) {
      const progressText = `Processing dataset: ${data.progress.toFixed(1)}% (${data.processed_questions} questions)`;
      toast.loading(progressText, { id: data.dataset_id });
    } else if (data.status === 'completed') {
      toast.success(`Dataset processing completed! Processed ${data.processed_questions} questions.`, { 
        id: data.dataset_id,
        duration: 5000 
      });
    } else if (data.status === 'failed') {
      toast.error(data.message || 'Dataset processing failed', { id: data.dataset_id });
    }
  }

  private handleAnalysisComplete(data: any): void {
    this.emit('analysis_complete', data);
    toast.success('Analysis completed successfully!', { duration: 5000 });
  }

  private handleError(data: any): void {
    this.emit('error', data);
    toast.error(data.message || 'An error occurred');
  }

  // Event subscription methods
  on(event: string, callback: Function): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);
  }

  off(event: string, callback: Function): void {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      eventListeners.delete(callback);
    }
  }

  private emit(event: string, data: any): void {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      eventListeners.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in WebSocket event listener for ${event}:`, error);
        }
      });
    }
  }

  // Send messages to server
  send(event: string, data?: any): void {
    if (!this.socket?.connected) {
      console.warn('WebSocket not connected. Message not sent:', event, data);
      return;
    }

    this.socket.emit(event, data);
  }

  // Convenience methods for common operations
  ping(): void {
    this.send('ping', { timestamp: Date.now() });
  }

  subscribe(events: string[]): void {
    this.send('subscribe', { events });
  }

  unsubscribe(events: string[]): void {
    this.send('unsubscribe', { events });
  }

  // Status getters
  get isConnected(): boolean {
    return this.socket?.connected || false;
  }

  get connectionState(): string {
    if (!this.socket) return 'disconnected';
    return this.socket.connected ? 'connected' : 'connecting';
  }
}

// React hook for WebSocket
export const useWebSocket = (options: WebSocketOptions = {}) => {
  const [client, setClient] = React.useState<WebSocketClient | null>(null);
  const [isConnected, setIsConnected] = React.useState(false);
  const [connectionError, setConnectionError] = React.useState<string | null>(null);

  React.useEffect(() => {
    const wsClient = new WebSocketClient(options);
    
    wsClient.on('connection_established', () => {
      setIsConnected(true);
      setConnectionError(null);
    });
    
    wsClient.on('connection_lost', () => {
      setIsConnected(false);
    });
    
    wsClient.on('connection_error', (data: any) => {
      setConnectionError('Failed to connect to real-time updates');
      setIsConnected(false);
    });

    setClient(wsClient);

    return () => {
      wsClient.disconnect();
    };
  }, [options.userId, options.datasetId, options.jobId]);

  return {
    client,
    isConnected,
    connectionError,
  };
};

// Global WebSocket instance (singleton)
let globalWebSocketClient: WebSocketClient | null = null;

export const getGlobalWebSocket = (options: WebSocketOptions = {}): WebSocketClient => {
  if (!globalWebSocketClient) {
    globalWebSocketClient = new WebSocketClient(options);
  }
  return globalWebSocketClient;
};

export const disconnectGlobalWebSocket = (): void => {
  if (globalWebSocketClient) {
    globalWebSocketClient.disconnect();
    globalWebSocketClient = null;
  }
};

