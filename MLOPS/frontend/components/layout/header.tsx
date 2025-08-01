import React from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { SystemHealth } from "@/types/api";
import {
  Brain,
  Github,
  ExternalLink,
  Activity,
  Settings,
  Moon,
  Sun,
  BarChart3,
} from "lucide-react";

interface HeaderProps {
  systemStatus?: SystemHealth | null;
}

export function Header({ systemStatus }: HeaderProps) {
  const [darkMode, setDarkMode] = React.useState(true);
  const apiDocsUrl = process.env.NEXT_PUBLIC_API_URL
    ? `${process.env.NEXT_PUBLIC_API_URL}/docs`
    : "http://localhost:8000/docs";

  React.useEffect(() => {
    // Apply dark mode on mount
    document.documentElement.classList.add("dark");
  }, []);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle("dark");
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Logo and Brand */}
          <div className="flex items-center space-x-4">
            <Link href="/" className="flex items-center space-x-2 group">
              
              <div>
                <h1 className="text-xl font-bold text-foreground">
                <span className="bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
                  Modelic
                  </span>
                </h1>
                
              </div>
            </Link>
          </div>

          {/* Center - Navigation */}
          <nav className="hidden md:flex items-center space-x-1">
            <Link href="/">
              <Button variant="ghost" size="sm" className="text-sm">
                Dashboard
              </Button>
            </Link>
            <Link href="/monitoring">
              <Button variant="ghost" size="sm" className="text-sm">
                <BarChart3 className="w-4 h-4 mr-1" />
                Monitoring
              </Button>
            </Link>
            <Button variant="ghost" size="sm" className="text-sm" asChild>
              <a href={apiDocsUrl} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="w-4 h-4 mr-1" />
                API Docs
              </a>
            </Button>
          </nav>

          {/* Right - Status and Actions */}
          <div className="flex items-center space-x-4">
            {/* System Status */}
            {systemStatus && (
              <div className="hidden sm:flex items-center space-x-2">
                <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-muted/50">
                  <Activity className="w-4 h-4 text-green-500" />
                  <span className="text-sm text-muted-foreground">
                    {systemStatus.registered_models} models
                  </span>
                </div>
                <Badge variant="success" className="text-xs">
                  {systemStatus.status}
                </Badge>
              </div>
            )}

            {/* Dark Mode Toggle */}
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleDarkMode}
              className="w-9 h-9"
            >
              {darkMode ? (
                <Sun className="h-4 w-4" />
              ) : (
                <Moon className="h-4 w-4" />
              )}
            </Button>

            {/* GitHub Link */}
            <Button variant="ghost" size="icon" asChild>
              <a
                href="https://github.com/aryamangoenka/my-ml-model/settings/hooks/"
                target="_blank"
                rel="noopener noreferrer"
                title="Setup GitHub Webhook"
              >
                <Github className="h-4 w-4" />
              </a>
            </Button>

            {/* Settings */}
            <Button variant="ghost" size="icon" className="w-9 h-9">
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}
