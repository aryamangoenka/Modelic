import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { StatusIndicator } from "@/components/status-indicator";
import { formatTimeAgo, truncateText } from "@/lib/utils";
import { Model, ModelDriftStatus } from "@/types/api";
import {
  ExternalLink,
  GitBranch,
  Clock,
  AlertTriangle,
  CheckCircle,
} from "lucide-react";
import { ApiService } from "@/lib/api";

interface ModelCardProps {
  model: Model;
}

export function ModelCard({ model }: ModelCardProps) {
  const [driftStatus, setDriftStatus] = useState<ModelDriftStatus | null>(null);
  const [loadingDrift, setLoadingDrift] = useState(false);

  useEffect(() => {
    const fetchDriftStatus = async () => {
      try {
        setLoadingDrift(true);
        const status = await ApiService.getModelDriftStatus(model.model_id);
        setDriftStatus(status);
      } catch (error) {
        // Silently fail - drift status is optional
        console.debug(
          "Failed to fetch drift status for model:",
          model.model_id
        );
      } finally {
        setLoadingDrift(false);
      }
    };

    fetchDriftStatus();
  }, [model.model_id]);

  const getDriftIcon = () => {
    if (loadingDrift) {
      return <div className="w-4 h-4 bg-muted animate-pulse rounded" />;
    }

    if (!driftStatus || driftStatus.drift_status === "no_data") {
      return null;
    }

    if (driftStatus.overall_drift_detected) {
      return <AlertTriangle className="w-4 h-4 text-red-500" />;
    } else {
      return <CheckCircle className="w-4 h-4 text-green-500" />;
    }
  };

  const getDriftBadge = () => {
    if (
      loadingDrift ||
      !driftStatus ||
      driftStatus.drift_status === "no_data"
    ) {
      return null;
    }

    if (driftStatus.overall_drift_detected) {
      return (
        <Badge variant="destructive" className="text-xs">
          Drift Detected
        </Badge>
      );
    } else {
      return (
        <Badge
          variant="outline"
          className="text-xs text-green-600 border-green-600"
        >
          No Drift
        </Badge>
      );
    }
  };

  return (
    <Link href={`/models/${model.model_id}`}>
      <Card className="h-full hover:shadow-lg transition-all duration-200 cursor-pointer group border-border hover:border-primary/50">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <h3 className="text-lg font-semibold text-foreground group-hover:text-primary transition-colors line-clamp-1">
                {model.name}
              </h3>
              <p className="text-sm text-muted-foreground mt-1 line-clamp-1">
                {truncateText(model.github_repo, 40)}
              </p>
            </div>
            <div className="flex items-center gap-2">
              {getDriftIcon()}
              <StatusIndicator status={model.status} size="sm" />
            </div>
          </div>
        </CardHeader>

        <CardContent className="pt-0">
          <div className="space-y-3">
            {/* Version and Status */}
            <div className="flex items-center justify-between">
              <Badge variant="outline" className="text-xs">
                <GitBranch className="w-3 h-3 mr-1" />
                {model.version}
              </Badge>
              <div className="flex items-center text-xs text-muted-foreground">
                <Clock className="w-3 h-3 mr-1" />
                {formatTimeAgo(model.created_at)}
              </div>
            </div>

            {/* Drift Status */}
            {getDriftBadge() && (
              <div className="flex items-center justify-between">
                {getDriftBadge()}
                {driftStatus && driftStatus.feature_drift_count > 0 && (
                  <span className="text-xs text-muted-foreground">
                    {driftStatus.feature_drift_count} features drifted
                  </span>
                )}
              </div>
            )}

            {/* Repository Link */}
            <div className="flex items-center text-xs text-muted-foreground hover:text-foreground transition-colors">
              <ExternalLink className="w-3 h-3 mr-1" />
              <span className="truncate">
                {model.github_repo?.replace("https://github.com/", "") ||
                  "Unknown repository"}
              </span>
            </div>

            {/* API Endpoint Preview */}
            <div className="text-xs font-mono bg-muted/50 rounded px-2 py-1 truncate">
              {model.predict_endpoint}
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
