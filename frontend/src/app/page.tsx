"use client";

import { useCallback, useState } from "react";
import ChatLauncher from "@/components/ChatLauncher";
import PortfolioHero from "@/components/PortfolioHero";

export default function Home() {
  const [openChat, setOpenChat] = useState<(() => void) | null>(null);

  const handleChatReady = useCallback((open: () => void) => {
    setOpenChat(() => open);
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-indigo-50">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <span className="text-lg font-bold tracking-tight text-slate-950">
          Portfolio AI
        </span>

        <span className="text-sm text-slate-500">
          AI-powered portfolio
        </span>
      </header>

      <PortfolioHero onOpenChat={() => openChat?.()} />

      <footer className="border-t border-slate-200 px-6 py-8 text-center text-sm text-slate-500">
        Built with Next.js, FastAPI, and RAG.
      </footer>

      <ChatLauncher onReady={handleChatReady} />
    </main>
  );
}