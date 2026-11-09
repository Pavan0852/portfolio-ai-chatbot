
"use client";

import { useEffect, useRef } from "react";
import type { ChatMessage as ChatMessageType } from "@/types/chat";
import ChatInput from "@/components/ChatInput";
import ChatMessage from "@/components/ChatMessage";
import SuggestedPrompts from "@/components/SuggestedPrompts";

interface ChatPanelProps {
  messages: ChatMessageType[];
  isLoading: boolean;
  error: string | null;
  onSend: (message: string) => void;
  onClear: () => void;
  onClose: () => void;
}

export default function ChatPanel({
  messages,
  isLoading,
  error,
  onSend,
  onClear,
  onClose,
}: ChatPanelProps) {
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  // Scroll only the message container, never the entire page.
  useEffect(() => {
    const container = messagesContainerRef.current;

    if (!container) return;

    container.scrollTo({
      top: container.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, isLoading]);

  return (
    <section
      id="portfolio-chat-panel"
      role="dialog"
      aria-modal="false"
      aria-labelledby="chat-title"
      className="fixed bottom-24 right-4 z-50 flex h-[min(680px,calc(100dvh-8rem))] w-[min(420px,calc(100vw-2rem))] flex-col overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-2xl sm:right-6"
    >
      {/* Fixed header */}
      <header className="flex shrink-0 items-center justify-between gap-3 bg-slate-950 px-5 py-4 text-white">
        <div>
          <h2 id="chat-title" className="font-semibold">
            Chat with my AI assistant
          </h2>
          <p className="mt-1 text-xs text-slate-300">
            Ask about my skills, experience and projects
          </p>
        </div>

        <div className="flex shrink-0 items-center gap-3">
          {messages.length > 0 && (
            <button
              type="button"
              onClick={onClear}
              disabled={isLoading}
              className="text-xs text-slate-300 hover:text-white disabled:opacity-50"
            >
              Clear
            </button>
          )}

          <button
            type="button"
            onClick={onClose}
            aria-label="Close chat"
            className="rounded-lg px-2 py-1 text-xl text-slate-300 hover:bg-white/10 hover:text-white"
          >
            ×
          </button>
        </div>
      </header>

      {/* Independently scrollable messages */}
      <div
        ref={messagesContainerRef}
        className="min-h-0 flex-1 space-y-4 overflow-x-hidden overflow-y-auto bg-slate-50 p-4"
        aria-live="polite"
        aria-relevant="additions text"
      >
        {messages.length === 0 ? (
          <div className="space-y-6 py-2">
            <div>
              <p className="text-lg font-semibold text-slate-900">
                Hello! 👋
              </p>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                I can help you explore my professional background, technical
                skills, education and AI projects.
              </p>
            </div>

            <SuggestedPrompts
              onSelect={onSend}
              disabled={isLoading}
            />
          </div>
        ) : (
          messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))
        )}

        {isLoading && (
          <div
            className="flex justify-start"
            role="status"
            aria-label="Assistant is thinking"
          >
            <div className="flex items-center gap-1.5 rounded-2xl rounded-bl-md border border-slate-200 bg-white px-5 py-4 shadow-sm">
              <span className="sr-only">Assistant is thinking</span>
              <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.3s]" />
              <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.15s]" />
              <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400" />
            </div>
          </div>
        )}

        {error && (
          <div
            role="alert"
            className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"
          >
            {error}
          </div>
        )}
      </div>

      {/* Fixed input area */}
      <div className="shrink-0">
        <ChatInput isLoading={isLoading} onSend={onSend} />
      </div>
    </section>
  );
}
