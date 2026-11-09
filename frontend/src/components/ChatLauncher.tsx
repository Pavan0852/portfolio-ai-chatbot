
"use client";

import { useCallback, useEffect, useState } from "react";
import { useChat } from "@/hooks/useChat";
import ChatPanel from "@/components/ChatPanel";

interface ChatLauncherProps {
  onReady?: (openChat: () => void) => void;
}

export default function ChatLauncher({ onReady }: ChatLauncherProps) {
  const [isOpen, setIsOpen] = useState(false);

  const {
    messages,
    isLoading,
    error,
    sendMessage,
    clearConversation,
  } = useChat();

  const openChat = useCallback(() => {
    setIsOpen(true);
  }, []);

  const closeChat = useCallback(() => {
    setIsOpen(false);
  }, []);

  const toggleChat = useCallback(() => {
    setIsOpen((current) => !current);
  }, []);

  // Expose the open function to the parent component.
  // This lets the portfolio hero button open the chat.
  useEffect(() => {
    onReady?.(openChat);
  }, [onReady, openChat]);

  return (
    <>
      {isOpen && (
        <ChatPanel
          messages={messages}
          isLoading={isLoading}
          error={error}
          onSend={sendMessage}
          onClear={clearConversation}
          onClose={closeChat}
        />
      )}

      <button
        type="button"
        onClick={toggleChat}
        aria-label={isOpen ? "Close chat assistant" : "Open chat assistant"}
        aria-expanded={isOpen}
        aria-controls="portfolio-chat-panel"
        className="fixed bottom-5 right-5 z-[60] flex h-14 items-center gap-2 rounded-full bg-slate-950 px-5 text-sm font-semibold text-white shadow-xl transition hover:-translate-y-0.5 hover:bg-slate-800 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-slate-300 sm:bottom-6 sm:right-6"
      >
        <span aria-hidden="true" className="text-lg">
          {isOpen ? "×" : "✦"}
        </span>

        <span>{isOpen ? "Close chat" : "Ask my AI"}</span>
      </button>
    </>
  );
}
