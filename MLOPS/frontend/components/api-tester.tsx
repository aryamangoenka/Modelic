import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { ApiService } from '@/lib/api';
import { formatJSON, isValidJSON } from '@/lib/utils';
import { PredictionResponse } from '@/types/api';
import { Play, Copy, Check, AlertCircle, Zap } from 'lucide-react';
import toast from 'react-hot-toast';

interface ApiTesterProps {
  modelId: string;
}

export function ApiTester({ modelId }: ApiTesterProps) {
  const [inputData, setInputData] = useState(
    formatJSON({ feature1: 1.0, feature2: 2.5, feature3: 'example' })
  );
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const isInputValid = isValidJSON(inputData);

  const handleTest = async () => {
    if (!isInputValid) {
      toast.error('Please enter valid JSON data');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setResult(null);

      const data = JSON.parse(inputData);
      const response = await ApiService.predict(modelId, data);
      
      setResult(response);
      toast.success('Inference completed successfully!');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail?.error || 
                          err.response?.data?.error || 
                          err.message || 
                          'Unknown error occurred';
      setError(errorMessage);
      toast.error('Inference failed');
    } finally {
      setLoading(false);
    }
  };

  const handleCopyResult = async () => {
    if (!result) return;
    
    try {
      await navigator.clipboard.writeText(formatJSON(result));
      setCopied(true);
      toast.success('Result copied to clipboard');
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      toast.error('Failed to copy result');
    }
  };

  const handleCopyEndpoint = async () => {
    const endpoint = `${window.location.origin}/api/models/${modelId}/predict`;
    try {
      await navigator.clipboard.writeText(endpoint);
      toast.success('Endpoint copied to clipboard');
    } catch (err) {
      toast.error('Failed to copy endpoint');
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Test API
          </CardTitle>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={handleCopyEndpoint}
          >
            <Copy className="h-4 w-4 mr-2" />
            Copy Endpoint
          </Button>
        </div>
        <p className="text-sm text-muted-foreground">
          Test your model's inference endpoint with custom input data
        </p>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Input Section */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium">Input Data (JSON)</label>
            <Badge variant={isInputValid ? 'success' : 'destructive'} className="text-xs">
              {isInputValid ? 'Valid JSON' : 'Invalid JSON'}
            </Badge>
          </div>
          <Textarea
            value={inputData}
            onChange={(e) => setInputData(e.target.value)}
            className="font-mono text-sm min-h-[120px] resize-none"
            placeholder="Enter JSON data for inference..."
          />
          {!isInputValid && (
            <div className="flex items-center gap-2 text-sm text-destructive">
              <AlertCircle className="h-4 w-4" />
              Please enter valid JSON format
            </div>
          )}
        </div>

        {/* Test Button */}
        <Button 
          onClick={handleTest} 
          loading={loading}
          disabled={!isInputValid}
          className="w-full"
          size="lg"
        >
          <Play className="h-4 w-4 mr-2" />
          Run Inference
        </Button>

        {/* Results Section */}
        {(result || error) && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium">
                {error ? 'Error Response' : 'Prediction Result'}
              </label>
              {result && !error && (
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={handleCopyResult}
                >
                  {copied ? (
                    <Check className="h-4 w-4 mr-2" />
                  ) : (
                    <Copy className="h-4 w-4 mr-2" />
                  )}
                  {copied ? 'Copied!' : 'Copy'}
                </Button>
              )}
            </div>

            {/* Success Result */}
            {result && !error && (
              <div className="space-y-3">
                <pre className="bg-muted/50 p-4 rounded-lg text-sm overflow-auto max-h-60 border">
                  {formatJSON(result)}
                </pre>
                
                {/* Key metrics */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {result.prediction !== undefined && (
                    <div className="text-center p-3 bg-primary/10 rounded-lg">
                      <div className="text-sm text-muted-foreground">Prediction</div>
                      <div className="font-mono font-medium">
                        {String(result.prediction)}
                      </div>
                    </div>
                  )}
                  {result.confidence !== undefined && (
                    <div className="text-center p-3 bg-green-500/10 rounded-lg">
                      <div className="text-sm text-muted-foreground">Confidence</div>
                      <div className="font-mono font-medium">
                        {(result.confidence * 100).toFixed(1)}%
                      </div>
                    </div>
                  )}
                  {result.inference_time_ms !== undefined && (
                    <div className="text-center p-3 bg-blue-500/10 rounded-lg">
                      <div className="text-sm text-muted-foreground">Latency</div>
                      <div className="font-mono font-medium">
                        {result.inference_time_ms}ms
                      </div>
                    </div>
                  )}
                  {result.model_version && (
                    <div className="text-center p-3 bg-purple-500/10 rounded-lg">
                      <div className="text-sm text-muted-foreground">Version</div>
                      <div className="font-mono font-medium text-xs">
                        {result.model_version}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Error Result */}
            {error && (
              <div className="bg-destructive/10 border border-destructive/20 p-4 rounded-lg">
                <div className="flex items-center gap-2 text-destructive mb-2">
                  <AlertCircle className="h-4 w-4" />
                  <span className="font-medium">Inference Failed</span>
                </div>
                <pre className="text-sm text-destructive/80 whitespace-pre-wrap">
                  {error}
                </pre>
              </div>
            )}
          </div>
        )}

        {/* API Info */}
        <div className="text-xs text-muted-foreground bg-muted/30 p-3 rounded-lg">
          <strong>Endpoint:</strong> POST /models/{modelId}/predict<br />
          <strong>Content-Type:</strong> application/json<br />
          <strong>Body:</strong> {`{ "data": { /* your input data */ } }`}
        </div>
      </CardContent>
    </Card>
  );
} 