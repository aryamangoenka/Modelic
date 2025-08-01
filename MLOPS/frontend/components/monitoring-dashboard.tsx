import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ApiService } from "@/lib/api";
import {
  InferenceLog,
  InferenceLogsResponse,
  LogsFilterOptions,
} from "@/types/api";
import {
  Activity,
  Clock,
  AlertCircle,
  CheckCircle,
  Hash,
  User,
  Calendar,
  Filter,
  RefreshCw,
  BarChart3,
} from "lucide-react";
import toast from "react-hot-toast";

interface MonitoringDashboardProps {
  modelId?: string;
}

export function MonitoringDashboard({ modelId }: MonitoringDashboardProps) {

  const [logs, setLogs] = useState<InferenceLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<LogsFilterOptions>({
    model_id: modelId,
    limit: 200, // Increased from 50 to 200 to show more logs
  });
  const [stats, setStats] = useState({
    total: 0,
    success: 0,
    error: 0,
    avgLatency: 0,
    avgConfidence: 0,
  });

  const fetchLogs = async () => {
    try {
      setLoading(true);
      // Ensure modelId is always included in filters when provided
      const currentFilters = {
        ...filters,
        model_id: modelId || filters.model_id,
      };

      const response: InferenceLogsResponse =
        await ApiService.getInferenceLogs(currentFilters);
      setLogs(response.logs);

      // Calculate statistics
      const total = response.logs.length;
      const success = response.logs.filter(
        (log) => log.status === "success"
      ).length;
      const error = response.logs.filter(
        (log) => log.status === "error"
      ).length;
      const avgLatency =
        total > 0
          ? response.logs.reduce((sum, log) => sum + log.latency_ms, 0) / total
          : 0;
      const confidenceLogs = response.logs.filter(
        (log) => log.prediction_confidence !== undefined
      );
      const avgConfidence =
        confidenceLogs.length > 0
          ? confidenceLogs.reduce(
              (sum, log) => sum + (log.prediction_confidence || 0),
              0
            ) / confidenceLogs.length
          : 0;

      setStats({ total, success, error, avgLatency, avgConfidence });
    } catch (error) {
      console.error("Failed to fetch logs:", error);
      toast.error("Failed to load monitoring data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [filters, modelId]); // Added modelId to dependencies

  const handleFilterChange = (newFilters: Partial<LogsFilterOptions>) => {
    setFilters((prev) => ({
      ...prev,
      ...newFilters,
      model_id: modelId || prev.model_id, // Ensure modelId is preserved
    }));
  };

  const handleRefresh = () => {
    fetchLogs();
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "success":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "error":
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-yellow-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variant =
      status === "success"
        ? "success"
        : status === "error"
          ? "destructive"
          : "secondary";
    return <Badge variant={variant}>{status}</Badge>;
  };

  return (
    <div className="space-y-6">
      {/* Header and Tab Navigation */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BarChart3 className="h-6 w-6" />
          <h2 className="text-2xl font-bold">Model Analytics</h2>
        </div>

        {/* Tab Navigation and Refresh */}
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={loading}
          >
            <RefreshCw
              className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`}
            />
            Refresh
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="space-y-6">
          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <Activity className="h-4 w-4 text-blue-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">
                      Total Requests
                    </p>
                    <p className="text-2xl font-bold">{stats.total}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">
                      Success Rate
                    </p>
                    <p className="text-2xl font-bold">
                      {stats.total > 0
                        ? ((stats.success / stats.total) * 100).toFixed(1)
                        : 0}
                      %
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 text-red-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">Errors</p>
                    <p className="text-2xl font-bold">{stats.error}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-purple-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">Avg Latency</p>
                    <p className="text-2xl font-bold">
                      {stats.avgLatency.toFixed(0)}ms
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <BarChart3 className="h-4 w-4 text-orange-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">
                      Avg Confidence
                    </p>
                    <p className="text-2xl font-bold">
                      {(stats.avgConfidence * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Filters */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Filter className="h-5 w-5" />
                Filters
                
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-4 items-center flex-wrap">
                {!modelId && (
                  <div className="flex items-center gap-2">
                    <label className="text-sm font-medium">Model ID:</label>
                    <input
                      type="text"
                      value={filters.model_id || ""}
                      onChange={(e) =>
                        handleFilterChange({
                          model_id: e.target.value || undefined,
                        })
                      }
                      placeholder="Filter by model ID"
                      className="px-3 py-1 border rounded text-sm w-48"
                    />
                  </div>
                )}

                <div className="flex items-center gap-2">
                  <label className="text-sm font-medium">Status:</label>
                  <select
                    value={filters.status_filter || ""}
                    onChange={(e) =>
                      handleFilterChange({
                        status_filter: e.target.value as
                          | "success"
                          | "error"
                          | "timeout"
                          | undefined,
                      })
                    }
                    className="px-3 py-1 border rounded text-sm"
                  >
                    <option value="">All</option>
                    <option value="success">Success</option>
                    <option value="error">Error</option>
                    <option value="timeout">Timeout</option>
                  </select>
                </div>

                <div className="flex items-center gap-2">
                  <label className="text-sm font-medium">Limit:</label>
                  <select
                    value={filters.limit || 200}
                    onChange={(e) =>
                      handleFilterChange({ limit: parseInt(e.target.value) })
                    }
                    className="px-3 py-1 border rounded text-sm"
                  >
                    <option value={50}>50</option>
                    <option value={100}>100</option>
                    <option value={200}>200</option>
                    <option value={500}>500</option>
                  </select>
                </div>

                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() =>
                      handleFilterChange({
                        model_id: undefined,
                        status_filter: undefined,
                        limit: 200,
                      })
                    }
                  >
                    Clear Filters
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Enhanced Logs Table */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Inference Logs</CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex items-center justify-center p-8">
                  <RefreshCw className="h-6 w-6 animate-spin" />
                  <span className="ml-2">Loading logs...</span>
                </div>
              ) : logs.length === 0 ? (
                <div className="text-center p-8 text-muted-foreground">
                  No inference logs found
                </div>
              ) : (
                <div className="space-y-3">
                  {logs.map((log) => (
                    <div
                      key={log.id}
                      className="border rounded-lg p-4 hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(log.status)}
                          <code className="text-sm bg-muted px-2 py-1 rounded">
                            {log.id}
                          </code>
                          {getStatusBadge(log.status)}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {formatTimestamp(log.timestamp)}
                        </div>
                      </div>

                      {/* Enhanced Monitoring Data */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                        <div className="flex items-center gap-2">
                          <Hash className="h-4 w-4 text-blue-500" />
                          <div>
                            <p className="text-xs text-muted-foreground">
                              Features
                            </p>
                            <p className="text-sm font-medium">
                              {log.feature_count}
                            </p>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <Clock className="h-4 w-4 text-purple-500" />
                          <div>
                            <p className="text-xs text-muted-foreground">
                              Latency
                            </p>
                            <p className="text-sm font-medium">
                              {log.latency_ms}ms
                            </p>
                          </div>
                        </div>

                        {log.prediction_confidence && (
                          <div className="flex items-center gap-2">
                            <BarChart3 className="h-4 w-4 text-green-500" />
                            <div>
                              <p className="text-xs text-muted-foreground">
                                Confidence
                              </p>
                              <p className="text-sm font-medium">
                                {(log.prediction_confidence * 100).toFixed(1)}%
                              </p>
                            </div>
                          </div>
                        )}

                        {log.model_version && (
                          <div className="flex items-center gap-2">
                            <Calendar className="h-4 w-4 text-orange-500" />
                            <div>
                              <p className="text-xs text-muted-foreground">
                                Version
                              </p>
                              <p className="text-sm font-medium text-xs">
                                {log.model_version}
                              </p>
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Feature Names */}
                      {log.feature_names && log.feature_names.length > 0 && (
                        <div className="mb-2">
                          <p className="text-xs text-muted-foreground mb-1">
                            Feature Names:
                          </p>
                          <div className="flex flex-wrap gap-1">
                            {log.feature_names.map((name, index) => (
                              <Badge
                                key={index}
                                variant="outline"
                                className="text-xs"
                              >
                                {name}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Error Message */}
                      {log.error_message && (
                        <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded">
                          <p className="text-sm text-red-700">
                            {log.error_message}
                          </p>
                        </div>
                      )}

                      {/* Prediction Details */}
                      <details className="mt-2">
                        <summary className="text-sm cursor-pointer hover:text-primary">
                          View Details
                        </summary>
                        <div className="mt-2 p-3 bg-muted rounded text-xs">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <p className="font-medium mb-1">Input Data:</p>
                              <pre className="text-xs overflow-auto">
                                {JSON.stringify(log.input_data, null, 2)}
                              </pre>
                            </div>
                            <div>
                              <p className="font-medium mb-1">Prediction:</p>
                              <pre className="text-xs overflow-auto">
                                {JSON.stringify(log.prediction, null, 2)}
                              </pre>
                            </div>
                          </div>
                        </div>
                      </details>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
  
  );
}
