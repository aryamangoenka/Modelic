import React from "react";
import { MonitoringDashboard } from "@/components/monitoring-dashboard";

export default function MonitoringPage() {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-2">Model Monitoring</h1>
        <p className="text-lg text-muted-foreground">
          Real-time monitoring and analytics for all deployed models
        </p>
      </div>
      <MonitoringDashboard />
    </div>
  );
}
