import React from 'react';
import { cn, getStatusColor, getStatusIndicatorColor } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';

interface StatusIndicatorProps {
  status: string;
  showText?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function StatusIndicator({ 
  status, 
  showText = true, 
  size = 'md',
  className 
}: StatusIndicatorProps) {
  const sizeClasses = {
    sm: 'h-2 w-2',
    md: 'h-3 w-3',
    lg: 'h-4 w-4',
  };

  const getVariant = (status: string) => {
    switch (status.toLowerCase()) {
      case 'deployed':
        return 'success';
      case 'validating':
        return 'warning';
      case 'failed':
        return 'destructive';
      case 'pending':
        return 'info';
      default:
        return 'secondary';
    }
  };

  if (showText) {
    return (
      <Badge variant={getVariant(status)} className={className}>
        <div
          className={cn(
            'rounded-full mr-1',
            sizeClasses[size],
            getStatusIndicatorColor(status)
          )}
        />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  }

  return (
    <div className={cn('flex items-center', className)}>
      <div
        className={cn(
          'rounded-full',
          sizeClasses[size],
          getStatusIndicatorColor(status)
        )}
        title={status.charAt(0).toUpperCase() + status.slice(1)}
      />
    </div>
  );
} 