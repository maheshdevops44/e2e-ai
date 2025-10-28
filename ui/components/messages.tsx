import type { UIMessage } from 'ai';
import { PreviewMessage, ThinkingMessage } from './message';
import { Greeting } from './greeting';
import { memo } from 'react';
import type { Vote } from '@/lib/db/schema';
import equal from 'fast-deep-equal';
import type { UseChatHelpers } from '@ai-sdk/react';
import { motion } from 'framer-motion';
import { useMessages } from '@/hooks/use-messages';
import { TestScriptButton } from './test-script-button';
import { PdfReportButton } from './pdf-report-button';

interface MessagesProps {
  chatId: string;
  status: UseChatHelpers['status'];
  votes: Array<Vote> | undefined;
  messages: Array<UIMessage>;
  setMessages: UseChatHelpers['setMessages'];
  reload: UseChatHelpers['reload'];
  isReadonly: boolean;
  isArtifactVisible: boolean;
}

function PureMessages({
  chatId,
  status,
  votes,
  messages,
  setMessages,
  reload,
  isReadonly,
}: MessagesProps) {
  const {
    containerRef: messagesContainerRef,
    endRef: messagesEndRef,
    onViewportEnter,
    onViewportLeave,
    hasSentMessage,
  } = useMessages({
    chatId,
    status,
  });

  return (
    <div
      ref={messagesContainerRef}
      className="flex flex-col min-w-0 gap-6 flex-1 overflow-y-scroll pt-4 relative"
    >
      {messages.length === 0 && <Greeting />}

      {messages.map((message, index) => {
        // Check for test script content
        const showTestScriptButton = message.role === 'assistant' && 
          message.content && 
          message.content.includes('Test Script Generated')

        // Check for "Test Script Result" to show PDF download button
        const showPdfButton = message.role === 'assistant' && 
          message.content && 
          message.content.includes('Test Script Result');

        return (
          <div key={message.id}>
            <PreviewMessage
              chatId={chatId}
              message={message}
              isLoading={status === 'streaming' && messages.length - 1 === index}
              vote={
                votes
                  ? votes.find((vote) => vote.messageId === message.id)
                  : undefined
              }
              setMessages={setMessages}
              reload={reload}
              isReadonly={isReadonly}
              requiresScrollPadding={
                hasSentMessage && index === messages.length - 1
              }
            />
            
            {/* Show test script download button if Test_Script found in content */}
            {showTestScriptButton && !isReadonly && (
              <div className="mx-auto max-w-3xl px-4 mt-2">
                <TestScriptButton
                  chatId={chatId}
                  testScriptId={chatId} // Use chatId to fetch from database
                  message="Test script is ready for download"
                />
              </div>
            )}

            {/* Show PDF report button if Test Script Result found in content */}
            {showPdfButton && !isReadonly && (
              <div className="mx-auto max-w-3xl px-4 mt-2">
                <PdfReportButton 
                  chatId={chatId}
                  message="Test Script Result - Download PDF Report" 
                />
              </div>
            )}
          </div>
        );
      })}

      {status === 'submitted' &&
        messages.length > 0 &&
        messages[messages.length - 1].role === 'user' && <ThinkingMessage />}

      <motion.div
        ref={messagesEndRef}
        className="shrink-0 min-w-[24px] min-h-[24px]"
        onViewportLeave={onViewportLeave}
        onViewportEnter={onViewportEnter}
      />
    </div>
  );
}

export const Messages = memo(PureMessages, (prevProps, nextProps) => {
  if (prevProps.isArtifactVisible && nextProps.isArtifactVisible) return true;

  if (prevProps.status !== nextProps.status) return false;
  if (prevProps.status && nextProps.status) return false;
  if (prevProps.messages.length !== nextProps.messages.length) return false;
  if (!equal(prevProps.messages, nextProps.messages)) return false;
  if (!equal(prevProps.votes, nextProps.votes)) return false;

  return true;
});
