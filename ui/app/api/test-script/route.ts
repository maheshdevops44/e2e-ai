import type { NextRequest } from 'next/server';
import { NextResponse } from 'next/server';
import { getTestScriptById, saveTestScript } from '@/lib/db/queries';

export async function POST(request: NextRequest) {
  const { chatId, content } = await request.json();

  const testScript = await saveTestScript({
    chatId,
    content: Buffer.from(content, 'utf-8').toString('base64'),
  });

  return NextResponse.json({ id: testScript.id });
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  console.log('searchParams', searchParams);
  const chatId = searchParams.get('chatId');

  if (!chatId) {
    return NextResponse.json({ error: 'chatId is required' }, { status: 400 });
  }

  const testScript = await getTestScriptById({ chatId });

  return NextResponse.json(testScript);
}
