import { extractLogsAndScreenshots } from '@/lib/utils';
import { getTestResultsByChatId } from '@/lib/db/queries';
import type { NextRequest } from 'next/server';

const streamResponse = (chatId: string) => {
  // Return event stream
  const encoder = new TextEncoder();
  let pollInterval: NodeJS.Timeout;
  let timeoutInterval: NodeJS.Timeout;

  let testExecutionStarted = false;

  const stream = new ReadableStream({
    start(controller) {
      pollInterval = setInterval(async () => {
        try {
          const testResults = await getTestResultsByChatId(chatId);

          if (testResults?.testResults && testResults?.artifacts) {
            console.log('Test results available', chatId);

            if (testResults?.artifacts && testResults?.artifacts.length === 0) {
              console.log('No artifacts found', chatId);
              return;
            }

            if (
              testResults?.testResults &&
              Object.keys(testResults?.testResults).length === 0
            ) {
              console.log('No test results found', chatId);
              return;
            }

            // Results available, send success and close
            const testResultsString = testResults?.testResults.stdout as string;
            const logsAndScreenshots =
              extractLogsAndScreenshots(testResultsString);

            const data = JSON.stringify({
              status: 'completed',
              data: {
                logsAndScreenshots,
                artifacts: testResults?.artifacts as string,
                signed_url: testResults?.testResults.signed_url as string,
              },
            });

            controller.enqueue(encoder.encode(`data: ${data}\n\n`));
            clearInterval(pollInterval);
            clearTimeout(timeoutInterval);
            controller.close();
          } else {
            console.log('Still waiting for test results', chatId);
            // Still waiting, send status update
            const data = JSON.stringify({ status: 'running' });
            controller.enqueue(encoder.encode(`data: ${data}\n\n`));
          }

          // Start the test execution in background
          if (!testExecutionStarted) {
            console.log('Starting test execution in background', chatId);
            await fetch(
              `${process.env.TEST_EXECUTOR_URL}/run-tests-background/${chatId}`,
              { method: 'GET' },
            );

            console.log('Test execution started in background', chatId);
            testExecutionStarted = true;
          }

          console.log('Polling for test results', chatId);
        } catch (error) {
          console.log('Error occurred', chatId, error);
          // Error occurred, send error and close
          const data = JSON.stringify({
            status: 'error',
            error: error instanceof Error ? error.message : 'Unknown error',
          });

          controller.enqueue(encoder.encode(`data: ${data}\n\n`));
          clearInterval(pollInterval);
          clearTimeout(timeoutInterval);
          controller.close();
        }
      }, 10000); // Check every 10 seconds

      // Set timeout for 5 minutes
      timeoutInterval = setTimeout(
        () => {
          console.log('Test execution timeout after 5 minutes', chatId);
          const data = JSON.stringify({
            status: 'timeout',
            error: 'Test execution timed out after 5 minutes',
          });

          controller.enqueue(encoder.encode(`data: ${data}\n\n`));
          clearInterval(pollInterval);
          controller.close();
        },
        30 * 60 * 1000,
      ); // 30 minutes
    },
    cancel() {
      console.log('Stream cancelled', chatId);
      // This runs when the stream is cancelled (client disconnects)
      clearInterval(pollInterval);
      clearTimeout(timeoutInterval);
    },
  });

  return stream;
};

export async function GET(
  _: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id: chatId } = await params;

  if (!chatId) {
    return new Response(JSON.stringify({ error: 'id is required' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const stream = streamResponse(chatId);

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      Connection: 'keep-alive',
    },
  });
}
