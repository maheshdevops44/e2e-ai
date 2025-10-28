import { NextRequest, NextResponse } from 'next/server';
import { PDFDocument, rgb, StandardFonts } from 'pdf-lib';
import { mockData } from '@/mock/data/mockData';
import { readdir, readFile } from 'fs/promises';
import path from 'path';
import https from 'https';
import http from 'http';
import { URL } from 'url';
import StreamZip from 'node-stream-zip';
import fs from 'fs';
import os from 'os';
import crypto from 'crypto';
import { getTestResultsByChatId } from '@/lib/db/queries';
import { extractLogsAndScreenshots } from '@/lib/utils';

// Types for the response data structure
interface ReportResultData {
  stdout: any; // Log data from test execution
  s3_bucket_url: string; // Signed S3 URL for screenshots ZIP
}

// Helper function to download file from URL
async function downloadFile(url: string): Promise<Buffer> {
  
  
  // Parse and log URL components
  const urlObj = new URL(url);
 
  
  // Extract and log AWS signature details
  const searchParams = new URLSearchParams(urlObj.search);
  
  
  return new Promise((resolve, reject) => {
    const client = urlObj.protocol === 'https:' ? https : http;
    
    //console.log('Making HTTP request...');
    client.get(url, (response) => {
     
      
      if (response.statusCode !== 200) {
        const errorMessage = response.statusCode === 403 
          ? `Failed to download file: HTTP ${response.statusCode} - S3 signed URL may have expired. Please generate a new signed URL.`
          : `Failed to download file: HTTP ${response.statusCode} - ${response.statusMessage}`;
        // console.error('Download failed:', errorMessage);
        reject(new Error(errorMessage));
        return;
      }
      
      const chunks: Buffer[] = [];
      response.on('data', (chunk) => chunks.push(chunk));
      response.on('end', () => resolve(Buffer.concat(chunks)));
      response.on('error', reject);
    }).on('error', reject);
  });
}

// Helper function to extract screenshots from ZIP buffer
async function extractScreenshotsFromZip(zipBuffer: Buffer): Promise<{ filename: string; content: Buffer }[]> {
  const screenshots: { filename: string; content: Buffer }[] = [];
  
  return new Promise((resolve, reject) => {
    // Write buffer to temporary file since node-stream-zip needs a file path
    // Use UUID to avoid collisions when multiple requests come at the same time
    const uniqueId = crypto.randomUUID();
    const tempPath = path.join(os.tmpdir(), `temp_${uniqueId}.zip`);
    
    fs.writeFile(tempPath, zipBuffer, async (err: any) => {
      if (err) {
        reject(err);
        return;
      }
      
      try {
        const zip = new StreamZip.async({ file: tempPath });
        const entries = await zip.entries();
        
        const promises: Promise<void>[] = [];
        
        for (const entry of Object.values(entries)) {
          // Only process image files from the screenshots folder
          if (entry.name.match(/screenshots\/.*\.(png|jpg|jpeg)$/i) && !entry.isDirectory) {
            const promise = zip.entryData(entry.name).then(data => {
              screenshots.push({
                filename: entry.name.split('/').pop() || entry.name, // Get just filename
                content: data
              });
            });
            promises.push(promise);
          }
        }
        
        await Promise.all(promises);
        await zip.close();
        
        // Clean up temp file
        fs.unlink(tempPath, () => {}); // Ignore errors
        
        resolve(screenshots);
      } catch (error) {
        // Clean up temp file on error
        fs.unlink(tempPath, () => {}); // Ignore errors
        reject(error);
      }
    });
  });
}

// Main PDF generation function that takes JSON data and S3 URL
async function generatePdfFromData(logsData: any[], s3BucketUrl: string): Promise<Uint8Array> {
  console.log('Starting PDF generation with provided data and S3 URL');
  console.log(`S3 Bucket URL: ${s3BucketUrl}`);
  console.log(`Logs data entries: ${logsData.length}`);
  
  // Download screenshots from S3 URL
  console.log('Downloading screenshots from S3 URL...');
  const zipBuffer = await downloadFile(s3BucketUrl);
  console.log(`Successfully downloaded ZIP file (${zipBuffer.length} bytes)`);
  
  const screenshots = await extractScreenshotsFromZip(zipBuffer);
  // console.log(`Extracted ${screenshots.length} screenshots from ZIP`);
  
  // Create a new PDF document
  const pdfDoc = await PDFDocument.create();
  
  // Embed fonts
  const font = await pdfDoc.embedFont(StandardFonts.Helvetica);
  const boldFont = await pdfDoc.embedFont(StandardFonts.HelveticaBold);
  
  // Process logsData in sequence, adding content in flow
  let currentPage = pdfDoc.addPage([595, 842]); // A4 size
  const { width, height } = currentPage.getSize();
  let currentY = height - 60; // Start from top
  
  for (let i = 0; i < logsData.length; i++) {
    const currentEntry = logsData[i];
    
    if (currentEntry.type === 'log') {
      // Check if we need space for LOG header + content (estimate ~80px)
      if (currentY < 120) {
        currentPage = pdfDoc.addPage([595, 842]);
        currentY = height - 60;
      }
      
      // Add LOG label
      currentPage.drawText('LOG:', {
        x: 50,
        y: currentY,
        size: 14,
        font: boldFont,
        color: rgb(0, 0, 0),
      });
      
      currentY -= 30;
      
      // Add log content
      const logText = currentEntry.content;
      const words = logText.split(' ');
      let line = '';
      
      for (const word of words) {
        const testLine = line ? `${line} ${word}` : word;
        if (testLine.length < 80) {
          line = testLine;
        } else {
          // Draw the line
          currentPage.drawText(line, {
            x: 50,
            y: currentY,
            size: 11,
            font: font,
            color: rgb(0.2, 0.2, 0.2),
          });
          currentY -= 18;
          line = word;
          
          // Check if we need a new page
          if (currentY < 60) {
            currentPage = pdfDoc.addPage([595, 842]);
            currentY = height - 60;
          }
        }
      }
      
      // Draw last line
      if (line) {
        currentPage.drawText(line, {
          x: 50,
          y: currentY,
          size: 11,
          font: font,
          color: rgb(0.2, 0.2, 0.2),
        });
        currentY -= 30; // Space after log entry
      }
      
    } else if (currentEntry.type === 'screenshot') {
      // Find the corresponding screenshot file
      const screenshotFilename = currentEntry.content;
      const correspondingScreenshot = screenshots.find(s => 
        s.filename.toLowerCase() === screenshotFilename.toLowerCase() ||
        s.filename.toLowerCase().includes(screenshotFilename.toLowerCase().replace('.png', '').replace('.jpg', '').replace('.jpeg', ''))
      );
      
      if (correspondingScreenshot) {
        try {
          let image;
          const filename = correspondingScreenshot.filename.toLowerCase();
          if (filename.endsWith('.png')) {
            image = await pdfDoc.embedPng(correspondingScreenshot.content);
          } else if (filename.endsWith('.jpg') || filename.endsWith('.jpeg')) {
            image = await pdfDoc.embedJpg(correspondingScreenshot.content);
          }
          
          if (image) {
            // Calculate image size - max 400x300
            const maxWidth = 400;
            const maxHeight = 300;
            
            const scaleX = maxWidth / image.width;
            const scaleY = maxHeight / image.height;
            const scale = Math.min(scaleX, scaleY, 1);
            
            const scaledWidth = image.width * scale;
            const scaledHeight = image.height * scale;
            
            // Check if we have space for SCREENSHOT header + image + filename (estimate total height needed)
            const neededSpace = 30 + scaledHeight + 40; // header + image + filename
            
            if (currentY < neededSpace) {
              currentPage = pdfDoc.addPage([595, 842]);
              currentY = height - 60;
            }
            
            // Add SCREENSHOT header
            currentPage.drawText('SCREENSHOT:', {
              x: 50,
              y: currentY,
              size: 14,
              font: boldFont,
              color: rgb(0, 0, 0),
            });
            
            currentY -= 30;
            
            // Center horizontally
            const imageX = (width - scaledWidth) / 2;
            const imageY = currentY - scaledHeight;
            
            // Draw image
            currentPage.drawImage(image, {
              x: imageX,
              y: imageY,
              width: scaledWidth,
              height: scaledHeight,
            });
            
            // Update currentY after image
            currentY = imageY - 15;
            
            // Add filename
            currentPage.drawText(`File: ${correspondingScreenshot.filename}`, {
              x: 50,
              y: currentY,
              size: 10,
              font: font,
              color: rgb(0, 0.6, 0),
            });
            
            currentY -= 40; // Space after screenshot
          }
        } catch (error) {
          // Check space for error message
          if (currentY < 100) {
            currentPage = pdfDoc.addPage([595, 842]);
            currentY = height - 60;
          }
          
          currentPage.drawText('SCREENSHOT:', {
            x: 50,
            y: currentY,
            size: 14,
            font: boldFont,
            color: rgb(0, 0, 0),
          });
          
          currentY -= 30;
          
          currentPage.drawText(`Error loading image: ${correspondingScreenshot.filename}`, {
            x: 50,
            y: currentY,
            size: 10,
            font: font,
            color: rgb(1, 0, 0),
          });
          
          currentY -= 40;
        }
      } else {
        // Check space for "not found" message
        if (currentY < 100) {
          currentPage = pdfDoc.addPage([595, 842]);
          currentY = height - 60;
        }
        
        currentPage.drawText('SCREENSHOT:', {
          x: 50,
          y: currentY,
          size: 14,
          font: boldFont,
          color: rgb(0, 0, 0),
        });
        
        currentY -= 30;
        
        currentPage.drawText(`Screenshot not found: ${screenshotFilename}`, {
          x: 50,
          y: currentY,
          size: 12,
          font: font,
          color: rgb(0.6, 0.6, 0.6),
        });
        
        currentY -= 40;
      }
    }
  }
  
  // Return PDF bytes
  const pdfBytes = await pdfDoc.save();
  return pdfBytes;
}

export async function GET(request: NextRequest) {
  try {
    // Extract chatId from query parameters
    const { searchParams } = new URL(request.url);
    const chatId = searchParams.get('chatId');
    //console.log("======chatId======>", chatId);
    if (!chatId) {
      return NextResponse.json(
        { error: 'Chat ID is required' },
        { status: 400 }
      );
    }
    
    // TODO: Replace this with actual endpoint call
    // const response = await fetch(`${process.env.TEST_RESULTS_ENDPOINT}/results/${chatId}`, {
    //   method: 'GET',
    //   headers: {
    //     'Content-Type': 'application/json',
    //   },
    // });
    // const data: ReportResultData = await response.json();
    // const { stdout: logsData, s3_bucket_url } = data;
    
    // For now, use mock data and environment S3 URL
    // console.log('Using mock data and environment S3 URL for PDF generation');
    // console.log('Chat ID:', chatId);
    
    const testResults = await getTestResultsByChatId(chatId);

    const s3BucketUrl = testResults?.testResults.signed_url;
    const logsData = extractLogsAndScreenshots(testResults?.testResults.stdout);
    
    if (!s3BucketUrl) {
      throw new Error('SCREENSHOTS_ZIP_URL not configured in environment variables');
    }
    
    // console.log('Generating PDF with:');
    // console.log('- Mock logs data entries:', logsData.length);
    // console.log('- S3 bucket URL configured:', !!s3BucketUrl);
    // console.log('- Chat ID:', chatId);
    
    // Generate PDF using the separated function
    const pdfBytes = await generatePdfFromData(logsData, s3BucketUrl);
    
    return new NextResponse(Buffer.from(pdfBytes), {
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': `attachment; filename="test-report-${chatId}.pdf"`,
      },
    });
    
  } catch (error) {
    console.error('Error generating PDF:', error);
    return NextResponse.json(
      { error: `Failed to generate PDF: ${error instanceof Error ? error.message : 'Unknown error'}` },
      { status: 500 }
    );
  }
}
