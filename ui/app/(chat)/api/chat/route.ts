import {
  appendClientMessage,
  appendResponseMessages,
  createDataStream,
  createDataStreamResponse,
  smoothStream,
  streamText,
} from 'ai';
import { auth, type UserType } from '@/app/(auth)/auth';
import { systemPrompt, type RequestHints } from '@/lib/ai/prompts';
import {
  createStreamId,
  deleteChatById,
  getChatById,
  // getMessageCountByUserId, // Temporarily disabled - requires GSI3
  getMessagesByChatId,
  getStreamIdsByChatId,
  getTestResultsByChatId,
  getTestScriptById,
  saveChat,
  saveMessages,
  saveTestScript,
  updateChatRunId,
} from '@/lib/db/queries';
import { generateUUID, getTrailingMessageId } from '@/lib/utils';
import { generateTitleFromUserMessage } from '../../actions';
import { postRequestBodySchema, type PostRequestBody } from './schema';
import { geolocation } from '@vercel/functions';
import {
  createResumableStreamContext,
  type ResumableStreamContext,
} from 'resumable-stream';
import { after } from 'next/server';
import type { Chat } from '@/lib/db/schema';
import { differenceInSeconds } from 'date-fns';
import { ChatSDKError } from '@/lib/errors';
import { myProvider } from '@/lib/ai/providers';
import { createAzure } from '@quail-ai/azure-ai-provider';
import { tempScript } from './const';
import { extractLogsAndScreenshot } from '@/lib/utils';

let globalStreamContext: ResumableStreamContext | null = null;

function getStreamContext() {
  if (!globalStreamContext) {
    try {
      globalStreamContext = createResumableStreamContext({
        waitUntil: after,
      });
    } catch (error: any) {
      if (error.message.includes('REDIS_URL')) {
        console.log(
          ' > Resumable streams are disabled due to missing REDIS_URL',
        );
      } else {
        console.error(error);
      }
    }
  }

  return globalStreamContext;
}

function parseMetadata(metadata: Record<string, string>) {
  const parsedMetadata: Record<string, string> = {};

  for (const key in metadata) {
    const value = JSON.parse(metadata[key]);
    if (typeof value === 'object') {
    }
  }
}

const llm = createAzure({
  apiKey: process.env.OPENAI_API_KEY,
  endpoint: process.env.AZURE_OPENAI_ENDPOINT,
  apiVersion: process.env.API_VERSION,
})

export async function POST(request: Request) {
  let requestBody: PostRequestBody;

  try {
    const json = await request.json();
    requestBody = postRequestBodySchema.parse(json);
  } catch (_) {
    return new ChatSDKError('bad_request:api').toResponse();
  }

  try {
    const { id, message, selectedVisibilityType } = requestBody;

    const session = await auth();

    if (!session?.user) {
      return new ChatSDKError('unauthorized:chat').toResponse();
    }

    const userType: UserType = session.user.type;

    // Rate limiting temporarily disabled (requires GSI3)
    // const messageCount = await getMessageCountByUserId({
    //   id: session.user.id,
    //   differenceInHours: 24,
    // });

    // if (messageCount > entitlementsByUserType[userType].maxMessagesPerDay) {
    //   return new ChatSDKError('rate_limit:chat').toResponse();
    // }

    const [chat, testScript] = await Promise.all([
      getChatById({ id }),
      getTestScriptById({ chatId: id }),
    ]);
    console.log('chat -> ', chat);

    if (!chat) {
      const title = 'Testing';

      // await generateTitleFromUserMessage({
      //   message,
      // });

      await saveChat({
        id,
        userId: session.user.id,
        title,
        visibility: selectedVisibilityType,
      });
    } else {
      if (chat.userId !== session.user.id) {
        return new ChatSDKError('forbidden:chat').toResponse();
      }
    }

    const previousMessages = await getMessagesByChatId({ id });

    const messages = appendClientMessage({
      // @ts-expect-error: todo add type conversion from DBMessage[] to UIMessage[]
      messages: previousMessages,
      message,
    });

    const { longitude, latitude, city, country } = geolocation(request);

    const requestHints: RequestHints = {
      longitude,
      latitude,
      city,
      country,
    };

    await saveMessages({
      messages: [
        {
          id: message.id,
          chatId: id,
          messageId: message.id,
          userId: session.user.id,
          role: 'user',
          parts: message.parts,
          attachments: message.experimental_attachments ?? [],
          createdAt: new Date().toISOString(),
        },
      ],
    });

    const streamId = generateUUID();
    await createStreamId({ streamId, chatId: id });

    const dataStreamResponse = createDataStreamResponse({
      execute: async (dataStream) => {
        console.log('chat?.runId -> ', chat?.runId);

        let response = null;

        if (testScript) {
          console.log('Starting test execution ', id);
          
          // Streaming version
          try {
            const response = await fetch(
              `${process.env.TEST_EXECUTOR_URL}/run-tests-stream/${id}`,
              {
                method: 'GET',
                headers: {
                  'Content-Type': 'text/event-stream',
                  Connection: 'keep-alive',
                },
              },
            );
            const reader = response.body?.getReader();
            if (!reader) {
              dataStream.write(`e:{"finishReason":"stop"}\n`);
              return;
            }
  
            const stream = new ReadableStream({
              async start(controller) {
                while (true) {
                  const { done, value } = await reader.read();
                  if (done) {
                    controller.close();
                    break;
                  }
                  controller.enqueue(value);
                }
              },
            });
  
            const decoder = new TextDecoder();
            const streamReader = stream.getReader();
  
            while (true) {
              const { done, value } = await streamReader.read();
              if (done) {
                console.log('Stream processing complete');
                dataStream.write(
                  `0:"**Test Script Result completed and available.**"\n`,
                );
                dataStream.write(`e:{"finishReason":"stop"}\n`);
                break;
              }
              const text = decoder.decode(value, { stream: true });
              console.log('text -> ', text);
              // print first 5 characters and last 5 characters
              console.log(text.slice(0, 5), text.slice(-5));
  
              const items = text
                .split('\n')
                .filter((item) => item.startsWith('data:'));
  
              for (const item of items) {
                // console.log('item -> ', item.replace('data: ', '').trim());
                const testResults = JSON.parse(item.replace('data: ', '').trim());
                console.log('testResults -> ', testResults);
                
                const logOrScreenshot = extractLogsAndScreenshot(testResults);
  
                if (logOrScreenshot) {
                  dataStream.write(`0:"${logOrScreenshot}"\n`);
                  dataStream.write(`0:"\\n\\n"\n`);
                }
  
                if (testResults?.status === 'completed') {
                  const testScriptResults = await getTestResultsByChatId(id);
  
                  dataStream.write(`0:"\\n\\n\\n"\n`);
  
                  dataStream.write(
                    `0:"Download artifacts: [Link](${testScriptResults?.testResults.signed_url})"\n`,
                  );
  
                  dataStream.write(`0:"\\n\\n"\n`);

                  dataStream.write(
                    `0:"**Test Script Result completed and available.**"\n`,
                  );
                }
              }
            }
          } catch (error) {
            console.error('Error fetching stream:', error);
            dataStream.write(`3:"Failed to fetch stream"\n`);
          }
  

          // Non streaming version
          // try {

          //   const response = await fetch(
          //     `${process.env.NEXTAUTH_URL}/api/test-script/${id}/run`,
          //     {
          //       method: 'GET',
          //       headers: {
          //         'Content-Type': 'text/event-stream',
          //         Connection: 'keep-alive',
          //       },
          //     },
          //   );

          //   const reader = response.body?.getReader();
          //   if (!reader) {
          //     dataStream.write(`e:{"finishReason":"stop"}\n`);
          //     return;
          //   }

          //   const stream = new ReadableStream({
          //     async start(controller) {
          //       while (true) {
          //         const { done, value } = await reader.read();
          //         if (done) {
          //           controller.close();
          //           break;
          //         }
          //         controller.enqueue(value);
          //       }
          //     },
          //   });

          //   const decoder = new TextDecoder();
          //   const streamReader = stream.getReader();

          //   dataStream.write(`0:"**Test execution started.**"\n`);
          //   dataStream.write(`0:"\\n\\n"\n`);

          //   while (true) {
          //     const { done, value } = await streamReader.read();
          //     if (done) {
          //       console.log('Stream processing complete');
          //       dataStream.write(
          //         `0:"Test Script Result completed and available."\n`,
          //       );
          //       dataStream.write(`e:{"finishReason":"stop"}\n`);
          //       break;
          //     }
          //     const text = decoder.decode(value, { stream: true });
          //     console.log('text -> ', text);

          //     const testResults = JSON.parse(text.replace('data: ', '').trim());

          //     if (testResults.status === 'completed') {
          //       const logsAndScreenshots = testResults.data.logsAndScreenshots;

          //       dataStream.write(`0:"\\n\\n\\n"\n`);

          //       // write logs and screenshots to data stream
          //       logsAndScreenshots.forEach((logOrScreenshot: any) => {
          //         if (logOrScreenshot.type === 'screenshot') {
          //           dataStream.write(`0:"- Screenshot taken: ${logOrScreenshot.content}"\n`);
          //         } else {
          //           dataStream.write(`0:"- ${logOrScreenshot.content}"\n`);
          //         }
          //         dataStream.write(`0:"\\n"\n`);
          //       });

          //       dataStream.write(`0:"\\n\\n"\n`);

          //       dataStream.write(`0:"Download artifacts: [Link](${testResults.data.signed_url})"\n`)

          //       dataStream.write(`0:"\\n\\n"\n`);

          //       dataStream.write(
          //         `0:"**Test Script Result completed and available.**"\n`,
          //       );
          //       dataStream.write(`e:{"finishReason":"stop"}\n`);
          //       break;
          //     }

          //     dataStream.write(`0:"."\n`);
          //   }

          // } catch (error) {
          //   console.error('Error fetching stream:', error);
          //   dataStream.write(`3:"Failed to fetch stream"\n`);
          // }

        } else {
          console.log('Calling the Agent ', chat?.runId, message.content);

          if (chat?.runId && !testScript) {
            dataStream.write(`0:"\\n\\n"\n`)
            dataStream.write(`0:"Starting the process to generate test script"\n`);
            dataStream.write(`0:"\\n\\n"\n`);
          }

          const workflowResponse = await fetch(
            `${process.env.AGENT_URL}/workflow`,
            {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                input: message.content,
                run_id: chat?.runId ?? undefined,
              }),
            },
          ).then((res) => res.json()).catch((err) => {
            console.log('Error calling the Agent ', err);
            return {
              error: 'Error calling the Agent',
            };
          });

          console.log('workflowResponse -> ', workflowResponse);

          response = workflowResponse;
          const testScriptCode = workflowResponse?.metadata?.test_script;

          if (testScriptCode) {
            try {
              const testScript = await saveTestScript({
                chatId: id,
                content: Buffer.from(testScriptCode).toString('base64'),
              });

              console.log('testScript -> ', testScriptCode);

              console.log('Saved test script with ID:', testScript.id);
            } catch (error) {
              console.error('Failed to save test script:', error);
            } finally {
              delete response.metadata.test_script;
              dataStream.write(`0:"\\n\\n"\n`);
              dataStream.write(`0:"Test Script Generated and available for download"\n`);
              dataStream.write(`0:"\\n\\n"\n`);
            }
          }
          
          const result = streamText({
            model: llm(process.env.AZURE_DEPLOYMENT!),
            maxTokens: 30000,
            system: `
            You will receive a JSON that contains instructions for a test case and other related information. I want you to keep the essence of the same but provide Markdown explanation for the same. Keep the same tone as the original JSON. Don't add any other text or comments.
            Write everything. If you receive the test script as well. Also write the exact test script in the response.
  
            If you receive test execution results. I need to only know the steps thats were taken, screenshots taken and the final result of the test. Nothing else.
            `,
            messages: [
              {
                role: 'user',
                content: JSON.stringify(response),
              },
            ],
            experimental_generateMessageId: generateUUID,
            experimental_telemetry: {
              isEnabled: false,
              functionId: 'stream-text',
            },
            onFinish: async ({ response: streamResponse }) => {
              const assistantId = getTrailingMessageId({
                messages: streamResponse.messages.filter(
                  (message) => message.role === 'assistant',
                ),
              });

              if (!assistantId) {
                throw new Error('No assistant message found!');
              }

              const [, assistantMessage] = appendResponseMessages({
                messages: [message],
                responseMessages: streamResponse.messages,
              });

              console.log('assistantMessage -> ', assistantMessage);

              await saveMessages({
                messages: [
                  {
                    id: assistantId,
                    messageId: assistantId,
                    chatId: id,
                    userId: session.user.id,
                    role: assistantMessage.role as 'assistant',
                    parts: assistantMessage.parts ?? [],
                    attachments: [],
                    createdAt: new Date().toISOString(),
                  },
                ],
              });

              console.log('Received chat?.runId -> ', chat?.runId);
              console.log(
                'response.metadata.run_id -> ',
                workflowResponse?.metadata?.run_id,
              );

              if (!chat?.runId && workflowResponse?.metadata?.run_id && !testScript) {
                console.log('Updating chat run id', {
                  id,
                  runId: workflowResponse?.metadata?.run_id,
                });
                await updateChatRunId({
                  id,
                  runId: workflowResponse?.metadata?.run_id,
                });

                // Only for testing purposes
                // const testScript = await saveTestScript({
                //   chatId: id,
                //   content: Buffer.from(
                //     tempScript
                //   ).toString('base64'),
                // });

                // console.log('testScript -> ', testScript);

              }
            },
            onError: (error) => {
              console.log('Error in streamText', error);
              dataStream.write(`e:{"finishReason":"error"}\n`);
            }
          });

          result.consumeStream();

          result.mergeIntoDataStream(dataStream, {
            sendReasoning: true,
          });

        }

        // if (response.metadata) {
        //   console.log('response.metadata -> ', response.metadata);

        //   const metadata: Record<string, string> = response.metadata;

        //   for (const key in metadata) {
        //     metadata[key].split('\n').forEach((line) => {
        //       dataStream.write(`0:"${key}: ${line} "\n`);
        //     });
        //   }
        // }

        // const lines = [
        //   '📋 Parsed User Story:',
        //   '• Objective: To verify that the clearance process for an integrated patient completes successfully and displays a confirmation message in the Clearance application.',
        //   "• Test Summary: ['Test the clearance workflow for an integrated patient in the Clearance application.', 'Ensure that the process completes and a confirmation message is displayed.']",
        //   '• Acceptance Criteria:',
        //   '  1. User can search for an integrated patient within the Clearance application.',
        //   '  2. Clearance process can be initiated for the selected patient.',
        //   '  3. Clearance process completes successfully.',
        //   '  4. A confirmation message is displayed upon successful clearance.',
        //   '• Applications Involved: Clearance',
        //   '• Test Automation Steps:',
        //   '  1. Login to the Clearance application.',
        //   '  2. Search for the integrated patient using valid search criteria.',
        //   '  3. Click to select the integrated patient from the search results.',
        //   '  4. Click to initiate the clearance process for the selected patient.',
        //   '  5. Verify that the clearance process completes successfully.',
        //   '  6. Check that a confirmation message is displayed after completion.',
        //   '',
        //   "🔍 Missing fields: ['Manual_Steps']",
        //   '',
        //   'Please review the parsed user story above and provide feedback.',
        // ];

        // for (const line of lines) {
        //   dataStream.write(`0:"${line} "\n`);
        // }

        // console.log('Saving message', {
        //   id: id,
        //   messageId: assistantId,
        //   chatId: id,
        //   userId: session.user.id,
        //   role: 'assistant',
        //   parts: lines,
        //   attachments: [],
        //   createdAt: new Date().toISOString(),
        // });

        // const assistantMessage = {
        //   id: assistantId,
        //   role: 'assistant',
        //   content: result.text,
        //   parts: [
        //     {
        //       type: 'step-start',
        //     },
        //     {
        //       type: 'text',
        //       text: result.text,
        //     },
        //   ],
        //   toolInvocations: [],
        //   createdAt: new Date().toISOString(),
        // };

        // await saveMessages({
        //   messages: [
        //     {
        //       id: assistantId,
        //       messageId: assistantId,
        //       chatId: id,
        //       userId: session.user.id,
        //       role: assistantMessage.role as 'assistant',
        //       parts: assistantMessage.parts ?? [],
        //       attachments: [],
        //       createdAt: new Date().toISOString(),
        //     },
        //   ],
        // });

        // if (!chat?.runId && response.run_id) {
        //   await updateChatRunId({ id, runId: response.run_id });
        // }

        // dataStream.write(`e:{"finishReason":"stop"}\n`);

        /**

        const response = await fetch(
          `${process.env.LANGGRAPH_API_URL}/api/graph`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ messages }),
          },
        );

        if (!response.body)
          throw new Error('No response body from langgraph API');

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const text = decoder.decode(value);
          dataStream.write(`0:"${text} "\n`);
        }
        */
      },
    });

    return dataStreamResponse;

    // const stream = createDataStream({
    //   execute: async (dataStream) => {
    //     const result = streamText({
    //       model: myProvider.languageModel('chat-model'),
    //       system: systemPrompt({
    //         selectedChatModel: 'chat-model',
    //         requestHints,
    //       }),
    //       messages,
    //       maxSteps: 5,
    //       experimental_activeTools: [
    //         'getWeather',
    //         'createDocument',
    //         'updateDocument',
    //         'requestSuggestions',
    //       ],
    //       experimental_transform: smoothStream({ chunking: 'word' }),
    //       experimental_generateMessageId: generateUUID,
    //       tools: {
    //         getWeather,
    //         createDocument: createDocument({ session, dataStream }),
    //         updateDocument: updateDocument({ session, dataStream }),
    //         requestSuggestions: requestSuggestions({
    //           session,
    //           dataStream,
    //         }),
    //       },
    //       onFinish: async ({ response }) => {
    //         if (session.user?.id) {
    //           try {
    //             const assistantId = getTrailingMessageId({
    //               messages: response.messages.filter(
    //                 (message) => message.role === 'assistant',
    //               ),
    //             });

    //             if (!assistantId) {
    //               throw new Error('No assistant message found!');
    //             }

    //             const [, assistantMessage] = appendResponseMessages({
    //               messages: [message],
    //               responseMessages: response.messages,
    //             });

    //             console.log('assistantMessage -> ', assistantMessage);

    //             await saveMessages({
    //               messages: [
    //                 {
    //                   id: assistantId,
    //                   messageId: assistantId,
    //                   chatId: id,
    //                   userId: session.user.id,
    //                   role: 'assistant',
    //                   parts: assistantMessage.parts ?? [],
    //                   attachments:
    //                     assistantMessage.experimental_attachments ?? [],
    //                   createdAt: new Date().toISOString(),
    //                 },
    //               ],
    //             });
    //           } catch (_) {
    //             console.error('Failed to save chat');
    //           }
    //         }
    //       },
    //       experimental_telemetry: {
    //         isEnabled: false,
    //         functionId: 'stream-text',
    //       },
    //     });

    //     result.consumeStream();

    //     result.mergeIntoDataStream(dataStream, {
    //       sendReasoning: true,
    //     });
    //   },
    //   onError: () => {
    //     return 'Oops, an error occurred!';
    //   },
    // });

    // const streamContext = getStreamContext();

    // if (streamContext) {
    //   return new Response(
    //     await streamContext.resumableStream(streamId, () => stream),
    //   );
    // } else {
    //   return new Response(stream);
    // }
  } catch (error) {
    console.log('error -> ', error);
    if (error instanceof ChatSDKError) {
      return error.toResponse();
    }
  }
}

export async function GET(request: Request) {
  const streamContext = getStreamContext();
  const resumeRequestedAt = new Date();

  if (!streamContext) {
    return new Response(null, { status: 204 });
  }

  const { searchParams } = new URL(request.url);
  const chatId = searchParams.get('chatId');

  if (!chatId) {
    return new ChatSDKError('bad_request:api').toResponse();
  }

  const session = await auth();

  if (!session?.user) {
    return new ChatSDKError('unauthorized:chat').toResponse();
  }

  let chat: Chat;

  try {
    chat = (await getChatById({ id: chatId })) as Chat;
  } catch {
    return new ChatSDKError('not_found:chat').toResponse();
  }

  if (!chat) {
    return new ChatSDKError('not_found:chat').toResponse();
  }

  if (chat.visibility === 'private' && chat.userId !== session.user.id) {
    return new ChatSDKError('forbidden:chat').toResponse();
  }

  const streamIds = await getStreamIdsByChatId({ chatId });

  if (!streamIds.length) {
    return new ChatSDKError('not_found:stream').toResponse();
  }

  const recentStreamId = streamIds.at(-1);

  if (!recentStreamId) {
    return new ChatSDKError('not_found:stream').toResponse();
  }

  const emptyDataStream = createDataStream({
    execute: () => { },
  });

  const stream = await streamContext.resumableStream(
    recentStreamId,
    () => emptyDataStream,
  );

  /*
   * For when the generation is streaming during SSR
   * but the resumable stream has concluded at this point.
   */
  if (!stream) {
    const messages = await getMessagesByChatId({ id: chatId });
    const mostRecentMessage = messages.at(-1);

    if (!mostRecentMessage) {
      return new Response(emptyDataStream, { status: 200 });
    }

    if (mostRecentMessage.role !== 'assistant') {
      return new Response(emptyDataStream, { status: 200 });
    }

    const messageCreatedAt = new Date(mostRecentMessage.createdAt);

    if (differenceInSeconds(resumeRequestedAt, messageCreatedAt) > 15) {
      return new Response(emptyDataStream, { status: 200 });
    }

    const restoredStream = createDataStream({
      execute: (buffer) => {
        buffer.writeData({
          type: 'append-message',
          message: JSON.stringify(mostRecentMessage),
        });
      },
    });

    return new Response(restoredStream, { status: 200 });
  }

  return new Response(stream, { status: 200 });
}

export async function DELETE(request: Request) {
  const { searchParams } = new URL(request.url);
  const id = searchParams.get('id');

  if (!id) {
    return new ChatSDKError('bad_request:api').toResponse();
  }

  const session = await auth();

  if (!session?.user) {
    return new ChatSDKError('unauthorized:chat').toResponse();
  }

  const chat = (await getChatById({ id })) as Chat;

  if (chat.userId !== session.user.id) {
    return new ChatSDKError('forbidden:chat').toResponse();
  }

  const deletedChat = await deleteChatById({ id });

  return Response.json(deletedChat, { status: 200 });
}
