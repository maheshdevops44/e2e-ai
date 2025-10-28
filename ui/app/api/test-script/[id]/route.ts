import type { NextRequest } from 'next/server';
import { NextResponse } from 'next/server';
import { getTestScriptById, updateTestScript } from '@/lib/db/queries';
import { auth } from '@/app/(auth)/auth';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id: chatId } = await params;

  if (!chatId) {
    return NextResponse.json({ error: 'id is required' }, { status: 400 });
  }

  // Check authentication
  const session = await auth();
  if (!session?.user) {
    return new NextResponse('Unauthorized', { status: 401 });
  }

  // Check if this is a download request
  const { searchParams } = new URL(request.url);
  const download = searchParams.get('download');

  const testScript = await getTestScriptById({ chatId });

  if (!testScript) {
    return NextResponse.json({ error: 'Test script not found' }, { status: 404 });
  }

  // If download is requested, return formatted text file
  if (download === 'true') {
    try {
      // Parse the test script JSON to format it nicely
      const scriptData = Buffer.from(testScript.content, 'base64').toString('utf-8');
      
      // Create a clean formatted text content with just the script
      let formattedContent = '';
      
      // Format the script by removing p[\n and replacing with actual newlines
      const cleanScript = scriptData.replace(/\\n/g, '\n').replace(/\\t/g, '    ');
      formattedContent = cleanScript;

      return new NextResponse(formattedContent, {
        status: 200,
        headers: {
          'Content-Type': 'text/plain',
          'Content-Disposition': `attachment; filename="test-script-${chatId}.txt"`,
        },
      });
    } catch (error) {
      console.error('Error formatting test script:', error);
      return NextResponse.json({ error: 'Invalid test script format' }, { status: 400 });
    }
  }

  // Regular API response (JSON)
  return NextResponse.json(testScript);
}
