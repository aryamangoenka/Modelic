import axios, { AxiosResponse } from 'axios';
import {
  Model,
  ModelHealth,
  SystemHealth,
  PredictionRequest,
  PredictionResponse,
  WebhookPayload,
  WebhookResponse,
  InferenceLogsResponse,
  LogsFilterOptions,
  BaselineStats,
  MonitoringData,
  // Add drift detection types
  ModelDriftStatus,
  ModelDriftHistory,
  GlobalDriftSummary,
  ManualDriftCheckResult,
  DriftCheckAllResult,
} from '@/types/api';

// Use Next.js API proxy instead of direct backend calls
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

// Create axios instance with default configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API Service class following the service pattern
export class ApiService {
  /**
   * Get system health status
   */
  static async getSystemHealth(): Promise<SystemHealth> {
    const response: AxiosResponse<SystemHealth> = await api.get('/health');
    return response.data;
  }

  /**
   * List all deployed models
   */
  static async listModels(): Promise<{ models: Model[]; total_count: number; status: string }> {
    const response = await api.get('/models/');
    return response.data;
  }

  /**
   * Get details for a specific model
   */
  static async getModel(modelId: string): Promise<Model> {
    const response: AxiosResponse<Model> = await api.get(`/models/${modelId}`);
    return response.data;
  }

  /**
   * Get model health status
   */
  static async getModelHealth(modelId: string): Promise<ModelHealth> {
    const response: AxiosResponse<ModelHealth> = await api.get(`/models/${modelId}/health`);
    return response.data;
  }

  /**
   * Make a prediction using the model
   */
  static async predict(modelId: string, data: Record<string, any>): Promise<PredictionResponse> {
    const response: AxiosResponse<PredictionResponse> = await api.post(`/models/${modelId}/predict`, { data });
    return response.data;
  }

  /**
   * Get model information (metadata)
   */
  static async getModelInfo(modelId: string): Promise<Model> {
    const response: AxiosResponse<Model> = await api.get(`/models/${modelId}/info`);
    return response.data;
  }

  /**
   * Get inference logs with enhanced monitoring data
   */
  static async getInferenceLogs(filters?: LogsFilterOptions): Promise<InferenceLogsResponse> {
    const params = new URLSearchParams();
    if (filters?.model_id) params.append('model_id', filters.model_id);
    if (filters?.status_filter) params.append('status_filter', filters.status_filter);
    if (filters?.limit) params.append('limit', filters.limit.toString());
    
    const response: AxiosResponse<InferenceLogsResponse> = await api.get(`/models/logs?${params}`);
    return response.data;
  }

  /**
   * Get baseline statistics for a model
   */
  static async getModelBaselineStats(modelId: string): Promise<BaselineStats> {
    const response: AxiosResponse<BaselineStats> = await api.get(`/models/${modelId}/baseline`);
    return response.data;
  }

  /**
   * Get comprehensive monitoring data for a model
   */
  static async getModelMonitoringData(
    modelId: string,
    hours: number = 24,
    includeBaseline: boolean = true
  ): Promise<MonitoringData> {
    const response: AxiosResponse<MonitoringData> = await api.get(`/models/${modelId}/monitoring`, {
      params: { hours, include_baseline: includeBaseline }
    });
    return response.data;
  }

  // ============================================================================
  // DRIFT DETECTION API METHODS (Phase 2.2 Step 3)
  // ============================================================================

  /**
   * Get current drift status for a specific model
   */
  static async getModelDriftStatus(modelId: string): Promise<ModelDriftStatus> {
    const response: AxiosResponse<ModelDriftStatus> = await api.get(`/models/${modelId}/drift`);
    return response.data;
  }

  /**
   * Get drift detection history for a specific model
   */
  static async getModelDriftHistory(
    modelId: string,
    days: number = 30,
    limit: number = 50
  ): Promise<ModelDriftHistory> {
    const response: AxiosResponse<ModelDriftHistory> = await api.get(`/models/${modelId}/drift/history`, {
      params: { days, limit }
    });
    return response.data;
  }

  /**
   * Manually trigger a drift detection check for a specific model
   */
  static async runManualDriftCheck(
    modelId: string,
    timeWindowHours?: number
  ): Promise<ManualDriftCheckResult> {
    const response: AxiosResponse<ManualDriftCheckResult> = await api.post(`/models/${modelId}/drift/check`, {
      time_window_hours: timeWindowHours
    });
    return response.data;
  }

  /**
   * Get global drift detection summary across all models
   */
  static async getDriftSummary(): Promise<GlobalDriftSummary> {
    const response: AxiosResponse<GlobalDriftSummary> = await api.get('/models/drift/summary');
    return response.data;
  }

  /**
   * Manually trigger drift detection for all models
   */
  static async runDriftCheckAllModels(): Promise<DriftCheckAllResult> {
    const response: AxiosResponse<DriftCheckAllResult> = await api.post('/models/drift/check-all');
    return response.data;
  }
}

// Enhanced Monitoring API Functions (Phase 2.1)
export const getModelBaselineStats = async (modelId: string) => {
  const response = await api.get(`/models/${modelId}/baseline`);
  return response.data;
};

export const getModelMonitoringData = async (
  modelId: string, 
  hours: number = 2400, 
  includeBaseline: boolean = true
) => {
  const response = await api.get(`/models/${modelId}/monitoring`, {
    params: { hours, include_baseline: includeBaseline }
  });
  return response.data;
};

export const getInferenceLogsEnhanced = async (
  modelId?: string, 
  limit: number = 50, 
  statusFilter?: string,
  latencyCategory?: string
) => {
  const response = await api.get('/models/logs', {
    params: { 
      model_id: modelId, 
      limit, 
      status_filter: statusFilter,
      latency_category: latencyCategory
    }
  });
  return response.data;
};

// Export default api instance for custom requests if needed
export default api;
