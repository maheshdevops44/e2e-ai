'use client';

import { Button } from './ui/button';
import { useState } from 'react';

interface TestScriptButtonProps {
  chatId: string;
  testScriptId: string;
  message: string;
}

export function TestScriptButton({ chatId, testScriptId, message }: TestScriptButtonProps) {
  const [isDownloading, setIsDownloading] = useState(false);

  const handleDownload = async () => {
    if (isDownloading) return; // Prevent multiple clicks
    
    setIsDownloading(true);
    
    try {
      console.log('Starting download for chatId:', chatId);
      
      // Fetch the test script using the existing route with download parameter
      const response = await fetch(`/api/test-script/${chatId}?download=true`);
      
      console.log('Response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Response error:', errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }
      
      const blob = await response.blob();
      console.log('Blob size:', blob.size);
      
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `test-script-${chatId}.txt`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      console.log('Download completed successfully');
    } catch (error) {
      console.error('Download failed:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      alert(`Failed to download test script: ${errorMessage}`);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950 dark:to-indigo-950 border-2 border-blue-300 dark:border-blue-600 rounded-lg p-4 my-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 bg-blue-500 dark:bg-blue-600 rounded-full flex items-center justify-center">
              <span className="text-white text-lg">📄</span>
            </div>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-blue-900 dark:text-blue-100">
              Test Script Generated
            </h3>
            <p className="text-xs text-blue-700 dark:text-blue-300">
              {message}
            </p>
          </div>
        </div>
        <Button 
          onClick={handleDownload}
          disabled={isDownloading}
          variant="default"
          size="sm"
          className="bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 text-white border-2 border-blue-800 dark:border-blue-400 font-semibold shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105 disabled:opacity-70 disabled:cursor-not-allowed disabled:transform-none"
        >
          {isDownloading ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Generating...
            </>
          ) : (
            <>
              <span className="mr-2">📄</span>
              Download Test Script
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
