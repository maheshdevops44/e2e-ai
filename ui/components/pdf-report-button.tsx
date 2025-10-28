'use client';

import { Button } from './ui/button';
import { useState } from 'react';
import { FileText } from 'lucide-react';

interface PdfReportButtonProps {
  message?: string;
  chatId: string; // Chat ID to pass to the PDF generation route
}

export function PdfReportButton({ message = "Download PDF Report", chatId }: PdfReportButtonProps) {
  const [isDownloading, setIsDownloading] = useState(false);

  const handleDownload = async () => {
    if (isDownloading) return;
    
    setIsDownloading(true);
    
    try {
      const response = await fetch(`/api/generate-pdf?chatId=${encodeURIComponent(chatId)}`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }
      
      // Create blob and download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `test-report-${chatId}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
    } catch (error) {
      console.error('Error downloading PDF:', error);
      alert(`Failed to download PDF: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="flex items-center gap-2 p-3 bg-muted/50 rounded-lg border">
      <FileText className="h-4 w-4 text-muted-foreground" />
      <span className="text-sm text-muted-foreground flex-1">{message}</span>
      <Button
        onClick={handleDownload}
        disabled={isDownloading}
        size="sm"
        variant="outline"
      >
        {isDownloading ? 'Generating...' : 'Download PDF'}
      </Button>
    </div>
  );
}
