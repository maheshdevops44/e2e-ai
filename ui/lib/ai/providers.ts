import {
  customProvider,
  extractReasoningMiddleware,
  wrapLanguageModel,
} from 'ai';
import { xai } from '@ai-sdk/xai';
import { isTestEnvironment } from '../constants';
import {
  artifactModel,
  chatModel,
  reasoningModel,
  titleModel,
} from './models.test';

import { createAzure } from '@ai-sdk/azure';

const azure = createAzure({
  resourceName: process.env.AZURE_RESOURCE_NAME,
  apiKey: process.env.AZURE_API_KEY,
});

export const myProvider = isTestEnvironment
  ? customProvider({
      languageModels: {
        'chat-model': chatModel,
        'chat-model-reasoning': reasoningModel,
        'title-model': titleModel,
        'artifact-model': artifactModel,
      },
    })
  : customProvider({
      languageModels: {
        'chat-model': azure('gpt-4o'),
        // 'chat-model-reasoning': wrapLanguageModel({
        //   model: xai('grok-3-mini-beta'),
        //   middleware: extractReasoningMiddleware({ tagName: 'think' }),
        // }),
        'title-model': azure('gpt-4o'),
        'artifact-model': azure('gpt-4o'),
      },
      imageModels: {},
    });
