import React, { ReactNode, useEffect, useState } from 'react';
import { Header } from './header';
import { ApiService } from '@/lib/api';
import { SystemHealth } from '@/types/api';
import { Toaster } from 'react-hot-toast';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);

  useEffect(() => {
    const fetchSystemHealth = async () => {
      try {
        const health = await ApiService.getSystemHealth();
        setSystemHealth(health);
      } catch (error) {
        console.error('Failed to fetch system health:', error);
      }
    };

    fetchSystemHealth();
    
    // Poll system health every 30 seconds
    const interval = setInterval(fetchSystemHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header systemStatus={systemHealth} />
      
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>

      {/* Toast notifications */}
      <Toaster
        position="bottom-right"
        toastOptions={{
          className: '',
          style: {
            background: 'hsl(var(--card))',
            color: 'hsl(var(--card-foreground))',
            border: '1px solid hsl(var(--border))',
          },
          success: {
            iconTheme: {
              primary: 'hsl(142 76% 36%)',
              secondary: 'white',
            },
          },
          error: {
            iconTheme: {
              primary: 'hsl(0 84% 60%)',
              secondary: 'white',
            },
          },
        }}
      />
    </div>
  );
} 