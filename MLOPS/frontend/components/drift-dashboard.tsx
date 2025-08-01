import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ApiService } from "@/lib/api";
import {
  ModelDriftStatus,
  ModelDriftHistory,
  GlobalDriftSummary,
  DriftResult,
  DriftAlert,
} from "@/types/api";
import {
  AlertTriangle,
  CheckCircle,
  Clock,
  RefreshCw,
  BarChart3,
  Activity,
  Zap,
  Bell,
  TrendingUp,
  Shield,
} from "lucide-react";
import toast from "react-hot-toast";

interface DriftDashboardProps {
  modelId?: string;
}

export function DriftDashboard({ modelId }: DriftDashboardProps) {
  const [globalSummary, setGlobalSummary] = useState<GlobalDriftSummary | null>(
    null
  );
  const [modelDriftStatus, setModelDriftStatus] =
    useState<ModelDriftStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [checkingDrift, setCheckingDrift] = useState(false);

  const fetchDriftData = async () => {
    try {
      setLoading(true);

      // Fetch global summary
      const summary = await ApiService.getDriftSummary();
      setGlobalSummary(summary);

      // Fetch model-specific data if modelId is provided
      if (modelId) {
        const status = await ApiService.getModelDriftStatus(modelId);
        setModelDriftStatus(status);
      }
    } catch (error) {
      console.error("Failed to fetch drift data:", error);
      toast.error("Failed to load drift detection data");
    } finally {
      setLoading(false);
    }
  };

  const runManualDriftCheck = async () => {
    if (!modelId) return;

    try {
      setCheckingDrift(true);
      const result = await ApiService.runManualDriftCheck(modelId);

      if (result.check_triggered) {
        toast.success("Drift check completed successfully");
        setTimeout(fetchDriftData, 1000);
      } else {
        toast.error("Failed to run drift check");
      }
    } catch (error) {
      console.error("Failed to run drift check:", error);
      toast.error("Failed to run drift check");
    } finally {
      setCheckingDrift(false);
    }
  };

  const runGlobalDriftCheck = async () => {
    try {
      setCheckingDrift(true);
      const result = await ApiService.runDriftCheckAllModels();

      if (result.check_triggered) {
        toast.success(
          `Drift check completed for ${result.successful_checks} models`
        );
        setTimeout(fetchDriftData, 1000);
      } else {
        toast.error("Failed to run global drift check");
      }
    } catch (error) {
      console.error("Failed to run global drift check:", error);
      toast.error("Failed to run global drift check");
    } finally {
      setCheckingDrift(false);
    }
  };

  useEffect(() => {
    fetchDriftData();
  }, [modelId]);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "high":
        return "destructive";
      case "moderate":
        return "secondary";
      case "low":
        return "outline";
      default:
        return "default";
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "high":
        return <AlertTriangle className="h-5 w-5 text-red-500" />;
      case "moderate":
        return <Clock className="h-5 w-5 text-yellow-500" />;
      case "low":
        return <Shield className="h-5 w-5 text-blue-500" />;
      default:
        return <CheckCircle className="h-5 w-5 text-green-500" />;
    }
  };

  const getDriftStatusMessage = (status: ModelDriftStatus) => {
    if (status.drift_status === "no_data") {
      return "No drift data available. Run a check to get started.";
    }

    if (status.overall_drift_detected) {
      return `Drift detected with ${status.overall_severity} severity. ${status.drift_summary.high_severity} features show high drift.`;
    }

    return "No significant drift detected. Your model is performing well.";
  };

  const formatTimestamp = (timestamp: string | number | null | undefined) => {
    if (!timestamp) return "Unknown";

    try {
      // Handle different timestamp formats
      let date: Date;

      if (typeof timestamp === "string") {
        // Try parsing as ISO string first
        if (timestamp.includes("T") || timestamp.includes("Z")) {
          date = new Date(timestamp);
        } else {
          // Try parsing as Unix timestamp (seconds)
          const numTimestamp = parseFloat(timestamp);
          if (!isNaN(numTimestamp)) {
            // If it's a Unix timestamp in seconds, convert to milliseconds
            date = new Date(numTimestamp * 1000);
          } else {
            // Try parsing as regular date string
            date = new Date(timestamp);
          }
        }
      } else if (typeof timestamp === "number") {
        // If it's a number, assume it's a Unix timestamp
        // Check if it's in seconds or milliseconds
        if (timestamp < 10000000000) {
          // Likely in seconds, convert to milliseconds
          date = new Date(timestamp * 1000);
        } else {
          // Likely in milliseconds
          date = new Date(timestamp);
        }
      } else {
        return "Unknown";
      }

      // Check if the date is valid
      if (isNaN(date.getTime())) {
        return "Invalid Date";
      }

      return date.toLocaleDateString();
    } catch (error) {
      console.error("Error formatting timestamp:", timestamp, error);
      return "Invalid Date";
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <RefreshCw className="h-6 w-6 animate-spin" />
        <span className="ml-2">Loading drift detection data...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Simple Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <TrendingUp className="h-6 w-6 text-blue-600" />
          <h2 className="text-2xl font-bold">Drift Detection</h2>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={fetchDriftData}
            disabled={loading}
          >
            <RefreshCw
              className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`}
            />
            Refresh
          </Button>
          {modelId && (
            <Button
              onClick={runManualDriftCheck}
              disabled={checkingDrift}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Zap
                className={`h-4 w-4 mr-2 ${checkingDrift ? "animate-spin" : ""}`}
              />
              Check Drift
            </Button>
          )}
        </div>
      </div>

      {/* Global Overview - Simplified */}
      {globalSummary && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          

          

          
        </div>
      )}

      {/* Model-Specific Drift Status - Simplified */}
      {modelId && modelDriftStatus && (
        <Card>
          <CardHeader></CardHeader>
          <CardContent>
            {modelDriftStatus.drift_status === "no_data" ? (
              <div className="text-center p-8">
                <Clock className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                <p className="text-lg font-medium text-gray-600">
                  No Drift Data Available
                </p>
                <p className="text-sm text-gray-500 mb-4">
                  Run a drift check to get started
                </p>
                <Button onClick={runManualDriftCheck} disabled={checkingDrift}>
                  <Zap
                    className={`h-4 w-4 mr-2 ${checkingDrift ? "animate-spin" : ""}`}
                  />
                  Run First Check
                </Button>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Main Status Card */}
                <div className="p-6 rounded-lg border bg-card">
                  <div className="flex items-center gap-4">
                    {getSeverityIcon(modelDriftStatus.overall_severity)}
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold">
                        {modelDriftStatus.overall_drift_detected
                          ? "Drift Detected"
                          : "No Drift Detected"}
                      </h3>
                      <p className="text-sm text-muted-foreground mt-1">
                        {getDriftStatusMessage(modelDriftStatus)}
                      </p>
                      <p className="text-xs text-muted-foreground mt-2">
                        Last checked:{" "}
                        {formatTimestamp(modelDriftStatus.last_check)}
                      </p>
                    </div>
                    <Badge
                      variant={getSeverityColor(
                        modelDriftStatus.overall_severity
                      )}
                      className="text-sm"
                    >
                      {modelDriftStatus.overall_severity.toUpperCase()}
                    </Badge>
                  </div>
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center p-4 border rounded-lg bg-card">
                    <p className="text-2xl font-bold">
                      {modelDriftStatus.total_features_checked}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Features Checked
                    </p>
                  </div>
                  <div className="text-center p-4 border rounded-lg bg-card">
                    <p className="text-2xl font-bold">
                      {modelDriftStatus.drift_summary.high_severity}
                    </p>
                    <p className="text-sm text-muted-foreground">High Drift</p>
                  </div>
                  <div className="text-center p-4 border rounded-lg bg-card">
                    <p className="text-2xl font-bold">
                      {modelDriftStatus.drift_summary.low_severity}
                    </p>
                    <p className="text-sm text-muted-foreground">Normal</p>
                  </div>
                </div>

                {/* Top Drifted Features - Only show if there's drift */}
                {modelDriftStatus.overall_drift_detected &&
                  modelDriftStatus.latest_report && (
                    <div>
                      <h4 className="font-medium mb-3">Top Drifted Features</h4>
                      <div className="space-y-2">
                        {modelDriftStatus.latest_report.feature_drift_results
                          .filter((result) => result.drift_detected)
                          .slice(0, 3)
                          .map((result, index) => (
                            <div
                              key={index}
                              className="flex items-center justify-between p-3 border rounded-lg bg-card"
                            >
                              <div className="flex items-center gap-3">
                                {getSeverityIcon(result.severity)}
                                <div>
                                  <p className="font-medium">
                                    {result.feature_name}
                                  </p>
                                  <p className="text-sm text-muted-foreground">
                                    {result.feature_type} • Score:{" "}
                                    {result.drift_score.toFixed(3)}
                                  </p>
                                </div>
                              </div>
                              <Badge
                                variant={getSeverityColor(result.severity)}
                              >
                                {result.severity.toUpperCase()}
                              </Badge>
                            </div>
                          ))}
                      </div>
                    </div>
                  )}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Active Alerts - Simplified */}
      {globalSummary && globalSummary.active_alerts.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5" />
              Active Alerts ({globalSummary.active_alerts.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {globalSummary.active_alerts.slice(0, 5).map((alert, index) => (
                <div
                  key={index}
                  className="flex items-center gap-3 p-3 border rounded-lg bg-card"
                >
                  {getSeverityIcon(alert.severity)}
                  <div className="flex-1">
                    <p className="font-medium">{alert.model_id}</p>
                    <p className="text-sm text-muted-foreground">
                      {alert.features_with_drift.length} features with drift
                      detected
                    </p>
                    {alert.features_with_drift.length > 0 && (
                      <p className="text-xs text-muted-foreground">
                        Features:{" "}
                        {alert.features_with_drift.slice(0, 2).join(", ")}
                        {alert.features_with_drift.length > 2 && "..."}
                      </p>
                    )}
                  </div>
                  <div className="text-right">
                    <Badge
                      variant={getSeverityColor(alert.severity)}
                      className="mb-1"
                    >
                      {alert.severity.toUpperCase()}
                    </Badge>
                    <p className="text-xs text-muted-foreground">
                      {formatTimestamp(
                        alert.drift_detected_at || alert.timestamp
                      )}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* No Alerts Message */}
      {globalSummary && globalSummary.active_alerts.length === 0 && (
        <Card>
          <CardContent className="p-8 text-center">
            <CheckCircle className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <p className="text-lg font-medium">No Active Alerts</p>
            <p className="text-sm text-muted-foreground">
              All models are performing normally
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
