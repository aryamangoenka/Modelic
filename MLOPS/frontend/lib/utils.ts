import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date): string {
  const d = new Date(date);
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

export function formatTimeAgo(date: string | Date): string {
  const now = new Date();
  const past = new Date(date);
  const diffInSeconds = Math.floor((now.getTime() - past.getTime()) / 1000);

  if (diffInSeconds < 60) {
    return `${diffInSeconds}s ago`;
  } else if (diffInSeconds < 3600) {
    const minutes = Math.floor(diffInSeconds / 60);
    return `${minutes}m ago`;
  } else if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600);
    return `${hours}h ago`;
  } else {
    const days = Math.floor(diffInSeconds / 86400);
    return `${days}d ago`;
  }
}

export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    console.error('Failed to copy text: ', err);
    return false;
  }
}

export function formatJSON(obj: any): string {
  try {
    return JSON.stringify(obj, null, 2);
  } catch (error) {
    return String(obj);
  }
}

export function isValidJSON(str: string): boolean {
  try {
    JSON.parse(str);
    return true;
  } catch (error) {
    return false;
  }
}

export function truncateText(text: string, maxLength: number = 100): string {
  if (text.length <= maxLength) {
    return text;
  }
  return text.substring(0, maxLength) + '...';
}

export function getStatusColor(status: string): string {
  switch (status.toLowerCase()) {
    case 'deployed':
    case 'ready':
    case 'success':
      return 'text-green-600';
    case 'failed':
    case 'error':
      return 'text-red-600';
    case 'pending':
    case 'processing':
      return 'text-yellow-600';
    default:
      return 'text-gray-600';
  }
}

export function getStatusIndicatorColor(status: string): string {
  switch (status.toLowerCase()) {
    case 'deployed':
    case 'ready':
    case 'success':
      return 'bg-green-500';
    case 'failed':
    case 'error':
      return 'bg-red-500';
    case 'pending':
    case 'processing':
      return 'bg-yellow-500';
    default:
      return 'bg-gray-500';
  }
}
