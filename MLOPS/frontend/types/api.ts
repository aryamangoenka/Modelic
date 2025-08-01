// Base API Response types
export interface ApiResponse<T = any> {
  data: T;
  status: string;
  message?: string;
}

export interface ApiError {
  error: string;
  trace?: string;
  detail?: string;
}

// Model related types
export interface Model {
  model_id: string;
  name: string;
  version: string;
  status: 'validating' | 'deployed' | 'failed' | 'pending';
  github_repo: string;
  created_at: string;
  updated_at: string;
  endpoint_path: string;
  predict_endpoint: string;
  info_endpoint: string;
  health_endpoint?: string;
  registered_at?: string;
  endpoints?: {
    predict: string;
    info: string;
    health: string;
  };
}

export interface ModelHealth {
  status: string;
  model_id: string;
  ready_for_inference: boolean;
  error?: string;
  last_checked: number;
}

export interface SystemHealth {
  status: string;
  version: string;
  services: {
    api: string;
    database: string;
    redis: string;
  };
  registered_models: number;
}

// Prediction types
export interface PredictionRequest {
  data: Record<string, any>;
}

export interface PredictionResponse {
  prediction: any;
  confidence?: number;
  model_version?: string;
  inference_time_ms?: number;
  model_id?: string;
}

// Model deployment types
export interface DeploymentInfo {
  model_id: string;
  endpoint_url: string;
  status: string;
  deployed_at: string;
}

// Webhook types
export interface WebhookPayload {
  ref: string;
  repository: {
    name: string;
    full_name: string;
    clone_url: string;
  };
}

export interface WebhookResponse {
  status: string;
  message: string;
  model_id?: string;
  deployment_url?: string;
}

// UI State types
export interface LoadingState {
  isLoading: boolean;
  error?: string;
}

export interface ModelListState extends LoadingState {
  models: Model[];
  totalCount: number;
}

export interface ModelDetailState extends LoadingState {
  model?: Model;
  health?: ModelHealth;
}

// Form types
export interface TestInferenceForm {
  inputData: string;
  isValid: boolean;
}

// Chart/Metrics types (for future use)
export interface MetricPoint {
  timestamp: string;
  value: number;
}

export interface ModelMetrics {
  responseTime: MetricPoint[];
  errorRate: MetricPoint[];
  requestCount: MetricPoint[];
}

// Enhanced Logging Types (Phase 2.1)
export interface InferenceLog {
  id: string;
  model_id: string;
  input_data: Record<string, any>;
  prediction: Record<string, any>;
  latency_ms: number;
  status: 'success' | 'error' | 'timeout';
  timestamp: string;
  // Enhanced monitoring fields
  feature_count: number;
  feature_names: string[];
  feature_types: Record<string, string>;
  numerical_features: Record<string, number>;
  categorical_features: Record<string, string>;
  prediction_metadata: {
    prediction_type: string;
    has_confidence: boolean;
    has_probabilities: boolean;
    model_version?: string;
    prediction_shape: number;
  };
  error_message?: string;
  user_id?: string;
  prediction_confidence?: number;
  model_version?: string;
  request_size_bytes: number;
  response_size_bytes: number;
  latency_category: 'fast' | 'medium' | 'slow' | 'very_slow';
}

// Baseline Statistics Types (Phase 2.1)
export interface NumericalFeatureStats {
  type: 'numerical';
  count: number;
  mean: number;
  std: number;
  min: number;
  max: number;
  median: number;
  percentiles: {
    '25': number;
    '75': number;
    '90': number;
    '95': number;
  };
  missing_count: number;
  histogram: {
    counts: number[];
    bin_edges: number[];
  };
}

export interface CategoricalFeatureStats {
  type: 'categorical';
  count: number;
  unique_count: number;
  most_common: [string, number][];
  value_distribution: Record<string, number>;
  missing_count: number;
}

export interface ComplexFeatureStats {
  type: 'complex';
  count: number;
  sample_value: string;
}

export interface BaselineMetadata {
  total_samples: number;
  total_features: number;
  numerical_features: string[];
  categorical_features: string[];
  calculated_at: string;
}

export interface BaselineStats {
  model_id: string;
  feature_stats: Record<string, NumericalFeatureStats | CategoricalFeatureStats | ComplexFeatureStats> & {
    _metadata: BaselineMetadata;
  };
  data_source: string;
  created_at: string;
  sample_count: number;
  feature_count: number;
  numerical_feature_count: number;
  categorical_feature_count: number;
}

// Enhanced Monitoring Types (Phase 2.1)
export interface MonitoringMetrics {
  total_requests: number;
  successful_requests: number;
  error_requests: number;
  success_rate: number;
  error_rate: number;
  avg_latency_ms: number;
  max_latency_ms: number;
  min_latency_ms: number;
}

export interface MonitoringData {
  model_id: string;
  time_window_hours: number;
  metrics: MonitoringMetrics;
  current_feature_stats: Record<string, {
    count: number;
    mean: number;
    std: number;
    min: number;
    max: number;
  }>;
  recent_logs_count: number;
  baseline_stats?: BaselineStats;
  status: string;
}

// Enhanced API Response Types
export interface InferenceLogsResponse {
  logs: InferenceLog[];
  total_returned: number;
  summary: {
    total_requests: number;
    successful_requests: number;
    success_rate: number;
    average_latency_ms: number;
    latency_distribution: Record<string, number>;
  };
  filters: {
    model_id?: string;
    status_filter?: string;
    latency_category?: string;
    limit: number;
  };
  status: string;
}

export interface LogsFilterOptions {
  model_id?: string;
  status_filter?: 'success' | 'error' | 'timeout';
  limit?: number;
}

// ============================================================================
// DRIFT DETECTION TYPES (Phase 2.2 Step 3)
// ============================================================================

export interface DriftResult {
  feature_name: string;
  feature_type: 'numerical' | 'categorical';
  drift_score: number;
  threshold: number;
  drift_detected: boolean;
  severity: 'none' | 'low' | 'moderate' | 'high';
  baseline_samples: number;
  current_samples: number;
  additional_metrics: Record<string, any>;
}

export interface DriftReport {
  model_id: string;
  timestamp: string;
  overall_drift_detected: boolean;
  overall_severity: 'none' | 'low' | 'moderate' | 'high';
  feature_drift_results: DriftResult[];
  summary_statistics: {
    total_features: number;
    drifted_features: number;
    average_drift_score: number;
    highest_drift_score: number;
    most_drifted_feature?: string;
  };
  baseline_period: string;
  current_period: string;
}

export interface ModelDriftStatus {
  model_id: string;
  drift_status: 'no_data' | 'available';
  message?: string;
  last_check?: string;
  overall_drift_detected: boolean;
  overall_severity: 'none' | 'low' | 'moderate' | 'high';
  feature_drift_count: number;
  total_features_checked: number;
  drift_summary: {
    high_severity: number;
    moderate_severity: number;
    low_severity: number;
  };
  latest_report?: DriftReport;
  status: string;
}

export interface DriftHistorySummary {
  total_reports: number;
  reports_with_drift: number;
  drift_detection_rate: number;
  average_severity_score: number;
}

export interface FeatureDriftTrend {
  feature_name: string;
  trend_data: Array<{
    timestamp: string;
    drift_score: number;
    severity: 'none' | 'low' | 'moderate' | 'high';
  }>;
  average_drift_score: number;
  trend_direction: 'increasing' | 'decreasing' | 'stable';
}

export interface ModelDriftHistory {
  model_id: string;
  time_window_days: number;
  summary: DriftHistorySummary;
  drift_history: DriftReport[];
  feature_trends: FeatureDriftTrend[];
  status: string;
}

export interface DriftAlert {
  alert_id: string;
  model_id: string;
  severity: 'low' | 'moderate' | 'high';
  drift_detected_at: string;
  features_with_drift: string[];
  summary_stats: Record<string, any>;
  report_id: string;
  // Optional fields for backward compatibility
  timestamp?: string;
  message?: string;
  feature_name?: string;
  drift_score?: number;
  threshold?: number;
}

export interface DriftSummaryStatistics {
  summary_statistics: {
    total_reports: number;
    drift_detected_count: number;
    drift_detection_rate: number;
    average_features_analyzed: number;
    severity_distribution: {
      high: number;
      moderate: number;
      low: number;
    };
    most_common_drift_severity: string;
    models_with_drift: string[];
    analysis_period_days: number;
    unique_models_analyzed: number;
  };
  active_alerts: number;
  high_severity_alerts: number;
  models_needing_check: number;
  scheduler_running: boolean;
  check_interval_hours: number;
  last_summary_generated: string;
}

export interface GlobalDriftSummary {
  summary: DriftSummaryStatistics;
  active_alerts: DriftAlert[];
  alert_count: number;
  high_severity_alerts: number;
  status: string;
}

export interface ManualDriftCheckResult {
  model_id: string;
  check_triggered: boolean;
  result: {
    success: boolean;
    drift_detected: boolean;
    severity: 'none' | 'low' | 'moderate' | 'high';
    feature_results: DriftResult[];
    error?: string;
  };
  status: string;
}

export interface DriftCheckAllResult {
  check_triggered: boolean;
  models_checked: number;
  successful_checks: number;
  failed_checks: number;
  results: Record<string, any>;
  status: string;
} 