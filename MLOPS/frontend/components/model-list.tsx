import React from 'react';
import { Model } from '@/types/api';
import { ModelCard } from '@/components/model-card';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { RefreshCw, Plus, Database } from 'lucide-react';

interface ModelListProps {
  models: Model[];
  loading: boolean;
  onRefresh: () => void;
}

function LoadingSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {Array.from({ length: 6 }).map((_, i) => (
        <Card key={i} className="h-48">
          <CardContent className="p-6">
            <div className="animate-pulse space-y-4">
              <div className="flex justify-between items-start">
                <div className="space-y-2 flex-1">
                  <div className="h-4 bg-muted rounded w-3/4" />
                  <div className="h-3 bg-muted rounded w-1/2" />
                </div>
                <div className="h-6 w-16 bg-muted rounded-full" />
              </div>
              <div className="space-y-2">
                <div className="h-3 bg-muted rounded w-1/3" />
                <div className="h-3 bg-muted rounded w-2/3" />
                <div className="h-8 bg-muted rounded" />
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

function EmptyState({ onRefresh }: { onRefresh: () => void }) {
  return (
    <Card className="max-w-md mx-auto">
      <CardContent className="p-12 text-center">
        <div className="flex justify-center mb-4">
          <div className="p-4 bg-muted rounded-full">
            <Database className="h-8 w-8 text-muted-foreground" />
          </div>
        </div>
        <h3 className="text-lg font-semibold text-foreground mb-2">
          No models deployed yet
        </h3>
        <p className="text-muted-foreground mb-6 text-sm leading-relaxed">
          Push a trained model to GitHub with a webhook to get started. Your models will appear here once deployed.
        </p>
        <div className="space-y-3">
          <Button onClick={onRefresh} variant="outline" className="w-full">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Button variant="ghost" className="w-full" asChild>
            <a 
              href="https://github.com/aryamangoenka/my-ml-model/settings/hooks/" 
              target="_blank" 
              rel="noopener noreferrer"
            >
              <Plus className="w-4 h-4 mr-2" />
              Setup GitHub Webhook
            </a>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

export function ModelList({ models, loading, onRefresh }: ModelListProps) {
  if (loading) {
    return <LoadingSkeleton />;
  }

  if (models.length === 0) {
    return <EmptyState onRefresh={onRefresh} />;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-foreground">
            Deployed Models
          </h2>
          <p className="text-sm text-muted-foreground">
            {models.length} model{models.length !== 1 ? 's' : ''} currently deployed
          </p>
        </div>
        <Button onClick={onRefresh} variant="outline" size="sm">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {models.map((model) => (
          <ModelCard key={model.model_id} model={model} />
        ))}
      </div>
    </div>
  );
} 