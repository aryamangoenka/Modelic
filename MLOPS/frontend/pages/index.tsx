import React, { useState, useEffect } from "react";
import Head from "next/head";
import { ModelList } from "@/components/model-list";
import { ApiService } from "@/lib/api";
import { Model, SystemHealth } from "@/types/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Zap,
  Activity,
  GitBranch,
  Shield,
  CheckCircle,
  AlertTriangle,
  Rocket,
  Sparkles,
  Eye,
  RefreshCw,
} from "lucide-react";
import toast from "react-hot-toast";

export default function Dashboard() {
  const [models, setModels] = useState<Model[]>([]);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [modelsResponse, healthResponse] = await Promise.all([
        ApiService.listModels(),
        ApiService.getSystemHealth(),
      ]);

      setModels(modelsResponse.models || []);
      setSystemHealth(healthResponse);
    } catch (error: any) {
      console.error("Failed to load data:", error);
      toast.error("Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    fetchData();
  };

  useEffect(() => {
    fetchData();
  }, []);

  const features = [
    {
      icon: Rocket,
      title: "One-Click Deployment",
      description:
        "Deploy ML models from GitHub with automatic validation and API generation",
      color: "text-blue-600 dark:text-blue-400",
      bgColor: "bg-blue-50 dark:bg-blue-950",
    },
    {
      icon: Activity,
      title: "Real-time Monitoring",
      description:
        "Live performance metrics, drift detection, and automated alerting",
      color: "text-green-600 dark:text-green-400",
      bgColor: "bg-green-50 dark:bg-green-950",
    },
    {
      icon: GitBranch,
      title: "Version Control",
      description:
        "Model versioning, rollback capabilities, and A/B testing framework",
      color: "text-purple-600 dark:text-purple-400",
      bgColor: "bg-purple-50 dark:bg-purple-950",
    },
    {
      icon: Shield,
      title: "Production Ready",
      description: "Enterprise-grade security, scalability, and reliability",
      color: "text-orange-600 dark:text-orange-400",
      bgColor: "bg-orange-50 dark:bg-orange-950",
    },
  ];

  return (
    <>
      <Head>
        <title>Modelic - MLOps Platform</title>
        <meta
          name="description"
          content="Deploy, monitor, and manage ML models with enterprise-grade MLOps platform"
        />
      </Head>

      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gradient-to-br from-background via-muted/20 to-background border-b">
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center">
            <div className="flex items-center justify-center mb-6">
              <div className="flex items-center space-x-2 bg-primary/10 px-4 py-2 rounded-full border">
                <Sparkles className="w-5 h-5 text-primary" />
                <span className="text-sm font-medium text-foreground">
                  MLOps Platform
                </span>
              </div>
            </div>

            <h1 className="text-8xl font-bold tracking-tight text-foreground mb-6">
              <span className="bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
                Modelic
              </span>
            </h1>

            <p className="text-2xl text-muted-foreground mb-8 max-w-3xl mx-auto">
              Deploy machine learning models with the simplicity of pushing to
              GitHub. Get automatic validation, real-time monitoring, and
              enterprise-grade MLOps in minutes.
            </p>

            {/* Trust Indicators */}
          </div>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="bg-background py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-foreground mb-4">
              Deploy in 3 simple steps
            </h2>
            <p className="text-lg text-muted-foreground">
              Get your ML model live in production with minimal effort
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-primary/10 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-primary">1</span>
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-2">
                Push to GitHub
              </h3>
              <p className="text-muted-foreground">
                Add your trained model, requirements.txt, and predict.py to a
                GitHub repository
              </p>
            </div>

            <div className="text-center">
              <div className="bg-green-100 dark:bg-green-950 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-green-600 dark:text-green-400">
                  2
                </span>
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-2">
                Automatic Deployment
              </h3>
              <p className="text-muted-foreground">
                Our platform validates your model and deploys it as a
                production-ready API
              </p>
            </div>

            <div className="text-center">
              <div className="bg-purple-100 dark:bg-purple-950 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                  3
                </span>
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-2">
                Monitor & Scale
              </h3>
              <p className="text-muted-foreground">
                Real-time monitoring, drift detection, and automatic scaling for
                your models
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="bg-muted/30 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-foreground mb-4">
              Everything you need for production ML
            </h2>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
              From deployment to monitoring, we've got you covered with
              enterprise-grade MLOps capabilities.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <Card
                key={index}
                className="border shadow-sm hover:shadow-md transition-shadow"
              >
                <CardContent className="p-6 text-center">
                  <div
                    className={`inline-flex p-3 rounded-lg ${feature.bgColor} mb-4`}
                  >
                    <feature.icon className={`w-8 h-8 ${feature.color}`} />
                  </div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-muted-foreground text-sm">
                    {feature.description}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>

      {/* System Status Section */}
      {systemHealth && (
        <div className="bg-muted/30 py-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-foreground mb-2">
                System Status
              </h2>
              <p className="text-muted-foreground">
                Real-time health monitoring across all platform services
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card className="border shadow-sm">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">
                        API Service
                      </p>
                      <p className="text-lg font-semibold text-foreground">
                        {systemHealth.services.api}
                      </p>
                    </div>
                    <div
                      className={`p-2 rounded-full ${systemHealth.services.api === "healthy" ? "bg-green-100 dark:bg-green-950" : "bg-red-100 dark:bg-red-950"}`}
                    >
                      {systemHealth.services.api === "healthy" ? (
                        <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
                      ) : (
                        <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400" />
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border shadow-sm">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">
                        Database
                      </p>
                      <p className="text-lg font-semibold text-foreground">
                        {systemHealth.services.database}
                      </p>
                    </div>
                    <div
                      className={`p-2 rounded-full ${systemHealth.services.database === "healthy" ? "bg-green-100 dark:bg-green-950" : "bg-red-100 dark:bg-red-950"}`}
                    >
                      {systemHealth.services.database === "healthy" ? (
                        <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
                      ) : (
                        <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400" />
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border shadow-sm">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">
                        Redis Cache
                      </p>
                      <p className="text-lg font-semibold text-foreground">
                        {systemHealth.services.redis}
                      </p>
                    </div>
                    <div
                      className={`p-2 rounded-full ${systemHealth.services.redis === "healthy" ? "bg-green-100 dark:bg-green-950" : "bg-red-100 dark:bg-red-950"}`}
                    >
                      {systemHealth.services.redis === "healthy" ? (
                        <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
                      ) : (
                        <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400" />
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      )}

      {/* Deployed Models Section */}
      <div className="bg-background py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-3xl font-bold text-foreground mb-2">
                Deployed Models
              </h2>
              <p className="text-muted-foreground">
                Monitor and manage your production ML models
              </p>
            </div>
            <Button onClick={handleRefresh} variant="outline">
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
          </div>

          <ModelList
            models={models}
            loading={loading}
            onRefresh={handleRefresh}
          />
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gradient-to-r from-primary to-purple-600 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to deploy your ML models?
          </h2>
          <p className="text-lg text-primary-foreground/90 mb-8 max-w-2xl mx-auto">
            Join thousands of data scientists and engineers who trust our
            platform for their production ML workloads.
          </p>
          <div className="flex items-center justify-center space-x-4">
            <Button size="lg" variant="secondary">
              <Rocket className="w-5 h-5 mr-2" />
              Get Started Free
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="border-white text-white hover:bg-white hover:text-primary"
            >
              <Eye className="w-5 h-5 mr-2" />
              View Documentation
            </Button>
          </div>
        </div>
      </div>
    </>
  );
}
