import { DynamoDB } from '@aws-sdk/client-dynamodb';
import dynamoose, { model } from 'dynamoose';
import type { ArtifactKind } from '@/components/artifact';
import type { VisibilityType } from '@/components/visibility-selector';

// --- Constants ---
export const USERS_TABLE = 'users';
export const CHATS_TABLE = 'chats';
export const MESSAGES_TABLE = 'messages';
export const DOCUMENTS_TABLE = 'documents';
export const SUGGESTIONS_TABLE = 'suggestions';
export const STREAMS_TABLE = 'streams';
export const TEST_SCRIPTS_TABLE = 'test-scripts';

// --- Dynamoose Setup ---
const ddb = new DynamoDB({
  //Credentials object not needed to take advantage of IAM role
  // credentials: {
  //   accessKeyId: process.env.AWS_ACCESS_KEY_ID ?? '',
  //   secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY ?? '',
  // },
  region: process.env.AWS_REGION ?? '',
});

dynamoose.aws.ddb.set(ddb as any);

// --- Entity Interfaces ---
export class User {
  userId!: string;
  email!: string;
  password?: string;
  createdAt!: string;
}

export class Chat {
  chatId!: string;
  userId!: string;
  title!: string;
  visibility!: VisibilityType;
  createdAt!: string;
  runId?: string;
}

export class DBMessage {
  messageId!: string;
  chatId!: string;
  userId!: string;
  role!: 'user' | 'assistant' | 'tool';
  parts!: any[];
  attachments!: any[];
  createdAt!: string;
  vote?: { isUpvoted: boolean };
}

export class Document {
  documentId!: string;
  userId!: string;
  title!: string;
  content?: string;
  kind!: ArtifactKind;
  createdAt!: string;
}

export class TestScript {
  id!: string;
  chatId!: string;
  content!: string;
  createdAt!: string;
  testResults?: Record<string, any>;
  artifacts?: string;
}

export class Suggestion {
  suggestionId!: string;
  documentId!: string;
  documentCreatedAt!: string;
  originalText!: string;
  suggestedText!: string;
  description?: string;
  isResolved!: boolean;
  userId!: string;
  createdAt!: string;
}

export class Stream {
  streamId!: string;
  chatId!: string;
  createdAt!: string;
}

// --- Table Schemas ---
export const UserSchema = {
  userId: { type: String, hashKey: true },
  email: { type: String, required: true },
  password: String,
  createdAt: { type: String, required: true },
};

export const ChatSchema = {
  chatId: { type: String, hashKey: true },
  userId: {
    type: String,
    required: true,
    index: { name: 'userId-index', type: 'global' as const },
  },
  title: { type: String, required: true },
  runId: String,
  visibility: { type: String, required: true },
  createdAt: { type: String, required: true },
};

export const MessageSchema = {
  messageId: { type: String, hashKey: true },
  chatId: {
    type: String,
    required: true,
    index: { name: 'chatId-index', type: 'global' as const },
  },
  userId: { type: String, required: true },
  role: { type: String, required: true },
  parts: {
    type: Array,
    required: true,
    schema: [
      {
        type: Object,
        schema: {
          type: String,
          text: String,
        },
      },
    ],
  },
  attachments: { type: Array, required: true },
  createdAt: { type: String, required: true },
  vote: {
    type: Object,
    schema: {
      isUpvoted: Boolean,
    },
  },
};

export const DocumentSchema = {
  documentId: { type: String, hashKey: true },
  userId: {
    type: String,
    required: true,
    index: { name: 'userId-index', type: 'global' as const },
  },
  title: { type: String, required: true },
  content: String,
  kind: { type: String, required: true },
  createdAt: { type: String, required: true },
};

export const SuggestionSchema = {
  suggestionId: { type: String, hashKey: true },
  documentId: {
    type: String,
    required: true,
    index: { name: 'documentId-index', type: 'global' as const },
  },
  documentCreatedAt: { type: String, required: true },
  originalText: { type: String, required: true },
  suggestedText: { type: String, required: true },
  description: String,
  isResolved: { type: Boolean, required: true },
  userId: { type: String, required: true },
  createdAt: { type: String, required: true },
};

export const TestScriptSchema = {
  id: { type: String, hashKey: true },
  chatId: {
    type: String,
    required: true,
    index: { name: 'chatId-index', type: 'global' as const },
  },
  content: { type: String, required: true },
  createdAt: { type: String, required: true },
  testResults: {
    type: Object,
    required: true,
    default: {},
    schema: {
      key: String,
      returncode: Number,
      signed_url: String,
      status: String,
      stdout: String,
      stderr: String,
    },
  },
  artifacts: { type: String, required: true, default: '' },
};


export const StreamSchema = {
  streamId: { type: String, hashKey: true },
  chatId: {
    type: String,
    required: true,
    index: { name: 'chatId-index', type: 'global' as const },
  },
  createdAt: { type: String, required: true },
};

// --- Models ---
export const UserModel = model(USERS_TABLE, UserSchema);
export const ChatModel = model(CHATS_TABLE, ChatSchema);
export const MessageModel = model(MESSAGES_TABLE, MessageSchema);
export const DocumentModel = model(DOCUMENTS_TABLE, DocumentSchema);
export const SuggestionModel = model(SUGGESTIONS_TABLE, SuggestionSchema);
export const StreamModel = model(STREAMS_TABLE, StreamSchema);
export const TestScriptModel = model(TEST_SCRIPTS_TABLE, TestScriptSchema);

// Export types that other files expect
export type Vote = {
  chatId: string;
  messageId: string;
  isUpvoted: boolean;
};

export type MessageData = {
  id: string;
  messageId: string;
  chatId: string;
  userId: string;
  role: 'user' | 'assistant' | 'tool';
  parts: any[];
  attachments: any[];
  createdAt: string;
  vote?: { isUpvoted: boolean };
};
