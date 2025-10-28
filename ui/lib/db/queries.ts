import 'server-only';

import {
  UserModel,
  ChatModel,
  MessageModel,
  DocumentModel,
  SuggestionModel,
  StreamModel,
  type User,
  type Chat,
  type DBMessage,
  type MessageData,
  type Document,
  type Suggestion,
  type Stream,
  type TestScript,
  TestScriptModel,
} from './schema';
import type { ArtifactKind } from '@/components/artifact';
import { generateUUID } from '../utils';
import { generateHashedPassword } from './utils';
import type { VisibilityType } from '@/components/visibility-selector';
import { ChatSDKError } from '../errors';
import { SortOrder } from 'dynamoose/dist/General';

// --- Function Implementations ---

export async function getUser(email: string): Promise<User[]> {
  try {
    return (await UserModel.query('email')
      .eq(email)
      .exec()) as unknown as User[];
  } catch (error) {
    throw new ChatSDKError(
      'bad_request:database',
      'Failed to get user by email',
    );
  }
}

export async function createUser(
  email: string,
  password: string,
): Promise<User> {
  const userId = generateUUID();
  const hashedPassword = generateHashedPassword(password);
  const now = new Date().toISOString();

  try {
    return (await UserModel.create({
      userId,
      email,
      password: hashedPassword,
      createdAt: now,
    })) as unknown as User;
  } catch (error) {
    throw new ChatSDKError('bad_request:database', 'Failed to create user');
  }
}

export async function createGuestUser(): Promise<
  { id: string; email: string }[]
> {
  const userId = generateUUID();
  const email = `guest-${Date.now()}`;
  const password = generateHashedPassword(generateUUID());
  const now = new Date().toISOString();

  await UserModel.create({
    userId,
    email,
    password,
    createdAt: now,
  });

  return [{ id: userId, email }];
}

export async function saveChat(chatData: {
  id: string;
  userId: string;
  title: string;
  visibility: VisibilityType;
}): Promise<Chat> {
  const { id, userId, title, visibility } = chatData;
  const now = new Date().toISOString();

  return ChatModel.create({
    chatId: id,
    userId,
    title,
    visibility,
    createdAt: now,
  }) as unknown as Chat;
}

export async function updateChatRunId({
  id,
  runId,
}: { id: string; runId: string }): Promise<void> {
  await ChatModel.update({ chatId: id }, { runId: runId });
}

export async function deleteChatById({
  id,
}: { id: string }): Promise<Chat | undefined> {
  const chat = await getChatById({ id });
  if (!chat) return undefined;

  // Delete all messages and streams associated with the chat using GSI
  const messages = (await MessageModel.query('chatId')
    .eq(id)
    .using('chatId-index')
    .exec()) as unknown as DBMessage[];
  const streams = (await StreamModel.query('chatId')
    .eq(id)
    .using('chatId-index')
    .exec()) as unknown as Stream[];

  if (messages.length > 0) {
    await MessageModel.batchDelete(
      messages.map((msg) => ({ messageId: msg.messageId })),
    );
  }

  if (streams.length > 0) {
    await StreamModel.batchDelete(
      streams.map((stream) => ({ streamId: stream.streamId })),
    );
  }

  // Delete the chat itself
  await ChatModel.delete({ chatId: id });

  return chat;
}

export async function getChatsByUserId({
  id,
  limit,
  startingAfter,
}: { id: string; limit: number; startingAfter: string | null }) {
  let query = ChatModel.query('userId')
    .eq(id)
    .limit(limit + 1);

  if (startingAfter) {
    const lastChat = await getChatById({ id: startingAfter });
    if (lastChat) {
      query = query.startAt({ chatId: lastChat.chatId });
    }
  }

  const chats = await query.exec();
  const hasMore = chats.length > limit;

  return { chats: chats.slice(0, limit), hasMore };
}

export async function getChatById({
  id,
}: { id: string }): Promise<Chat | undefined> {
  try {
    const chat = await ChatModel.get({ chatId: id });
    if (!chat) return undefined;
    return chat as unknown as Chat;
  } catch {
    return undefined;
  }
}

export async function saveMessages({
  messages,
}: { messages: Array<MessageData> }): Promise<void> {
  const messageItems = messages.map((msg) => ({
    messageId: msg.messageId,
    chatId: msg.chatId,
    userId: msg.userId,
    role: msg.role,
    parts: msg.parts,
    attachments: msg.attachments,
    createdAt: msg.createdAt,
    vote: msg.vote,
  }));

  await MessageModel.batchPut(messageItems);
}

export async function getMessagesByChatId({
  id,
}: { id: string }): Promise<DBMessage[]> {
  return (await MessageModel.query()
    .where('chatId')
    .eq(id)
    .sort(SortOrder.descending)
    .exec()) as unknown as DBMessage[];
}

export async function getMessageById({
  id,
}: { id: string }): Promise<DBMessage | undefined> {
  try {
    return (await MessageModel.get({ messageId: id })) as unknown as DBMessage;
  } catch (error) {
    return undefined;
  }
}

export async function voteMessage({
  messageId,
  type,
}: { messageId: string; type: 'up' | 'down' }): Promise<void> {
  const message = await getMessageById({ id: messageId });
  if (!message)
    throw new ChatSDKError('not_found:database', 'Message not found');

  await MessageModel.update(
    { messageId },
    { vote: { isUpvoted: type === 'up' } },
  );
}

export async function getVotesByChatId({ id }: { id: string }) {
  const messages = await getMessagesByChatId({ id });
  return messages
    .filter((msg) => msg.vote)
    .map((msg) => ({
      chatId: msg.chatId,
      messageId: msg.messageId,
      isUpvoted: msg.vote?.isUpvoted ?? false,
    }));
}

export async function saveDocument({
  id,
  title,
  kind,
  content,
  userId,
}: {
  id: string;
  title: string;
  kind: ArtifactKind;
  content: string;
  userId: string;
}): Promise<any[]> {
  const now = new Date().toISOString();
  const docItem = {
    documentId: id,
    userId,
    title,
    content,
    kind,
    createdAt: now,
  };

  const doc = await DocumentModel.create(docItem);
  return [doc];
}

export async function getDocumentById({
  id,
}: { id: string }): Promise<any | undefined> {
  try {
    return (await DocumentModel.get({ documentId: id })) as unknown as any;
  } catch (error) {
    return undefined;
  }
}

export async function deleteMessagesByChatIdAfterTimestamp({
  chatId,
  timestamp,
}: { chatId: string; timestamp: Date }): Promise<void> {
  const messages = await getMessagesByChatId({ id: chatId });
  const messagesToDelete = messages.filter(
    (msg) => new Date(msg.createdAt) >= timestamp,
  );

  if (messagesToDelete.length > 0) {
    await MessageModel.batchDelete(
      messagesToDelete.map((msg) => ({ messageId: msg.messageId })),
    );
  }
}

export async function updateChatVisiblityById({
  chatId,
  visibility,
}: { chatId: string; visibility: 'private' | 'public' }): Promise<void> {
  const chat = await getChatById({ id: chatId });
  if (!chat) throw new ChatSDKError('not_found:database', 'Chat not found');

  await ChatModel.update({ chatId }, { visibility });
}

// Temporarily disabled - requires GSI3 for rate limiting
// export async function getMessageCountByUserId({ id, differenceInHours }: { id: string; differenceInHours: number }): Promise<number> {
//     const timeLimit = new Date(Date.now() - differenceInHours * 60 * 60 * 1000).toISOString();
//     const result = await MessageModel.query('GSI3PK').eq(pkUser(id)).and().where('GSI3SK').ge(`MSG#${timeLimit}`).count().exec();
//     return result.count;
// }

export async function saveSuggestions({
  suggestions,
}: { suggestions: any[] }): Promise<void> {
  const suggestionItems = suggestions.map((s) => {
    const now = new Date().toISOString();
    return {
      suggestionId: generateUUID(),
      documentId: s.documentId,
      documentCreatedAt: s.documentCreatedAt,
      originalText: s.originalText,
      suggestedText: s.suggestedText,
      description: s.description,
      isResolved: s.isResolved,
      userId: s.userId,
      createdAt: now,
    };
  });
  await SuggestionModel.batchPut(suggestionItems);
}

export async function getSuggestionsByDocumentId({
  documentId,
}: { documentId: string }): Promise<any[]> {
  return (await SuggestionModel.query('documentId')
    .eq(documentId)
    .using('documentId-index')
    .exec()) as unknown as any[];
}

export async function createStreamId({
  streamId,
  chatId,
}: { streamId: string; chatId: string }): Promise<void> {
  const now = new Date().toISOString();
  await StreamModel.create({
    streamId,
    chatId,
    createdAt: now,
  });
}

export async function getStreamIdsByChatId({
  chatId,
}: { chatId: string }): Promise<string[]> {
  const streams = (await StreamModel.query('chatId')
    .eq(chatId)
    .using('chatId-index')
    .exec()) as unknown as Stream[];
  return streams.map((s) => s.streamId);
}

export async function saveTestScript({
  chatId,
  content,
}: { chatId: string; content: string }): Promise<TestScript> {
  return (await TestScriptModel.create({
    id: generateUUID(),
    chatId,
    content,
    testResults: {},
    artifacts: '',
    createdAt: new Date().toISOString(),
  })) as unknown as TestScript;
}

export async function getTestScriptById({
  chatId,
}: { chatId: string }): Promise<any | undefined> {
  try {
    const testScript = await TestScriptModel.query('chatId')
      .eq(chatId)
      .using('chatId-index')
      .exec()
      .then((res) => res.toJSON());
    if (!testScript) return undefined;
    return testScript[0];
  } catch (error) {
    console.error('Error fetching test script for chatId:', chatId, error);
    return undefined;
  }
}

export async function updateTestScript({
  chatId,
  testResults,
  artifacts,
}: { chatId: string; testResults: string; artifacts: string }): Promise<void> {
  await TestScriptModel.update({ chatId }, { testResults, artifacts });
}

export async function getTestResultsByChatId(
  chatId: string,
): Promise<
  { testResults: Record<string, any>; artifacts: string } | undefined
> {
  try {
    // Find the record by chatId using GSI
    const testScript = await TestScriptModel.query('chatId')
      .eq(chatId)
      .using('chatId-index')
      .attributes(['testResults', 'artifacts', 'signed_url'])
      .exec()
      .then((res) => res.toJSON());

    if (testScript.length === 0) {
      console.log('No test script found for chatId:', chatId);
      return undefined;
    }

    console.log('testResults', testScript[0]);

    if (
      !testScript[0].testResults ||
      Object.keys(testScript[0].testResults).length === 0 ||
      testScript[0].artifacts === undefined
    ) {
      console.log('No test results or artifacts found for chatId:', chatId);
      return undefined;
    }

    console.log('Found test script for chatId:', chatId, testScript);

    return {
      testResults: (testScript[0] as unknown as TestScript)
        .testResults as unknown as Record<string, any>,
      artifacts: (testScript[0] as unknown as TestScript)
        .artifacts as unknown as string
    };
  } catch (error) {
    console.error('Error fetching test results for chatId:', chatId, error);
    return undefined;
  }
}

