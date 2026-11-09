
"use client";

import { useState, type FormEvent, type KeyboardEvent } from "react";

interface ChatInputProps {
  isLoading: boolean;
  onSend: (message: string) => void;
}

export default function ChatInput({
  isLoading,
  onSend,
}: ChatInputProps) {
  const [value, setValue] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const message = value.trim();

    if (!message || isLoading) {
      return;
    }

    onSend(message);
    setValue("");
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      event.currentTarget.form?.requestSubmit();
    }
  }

  return (
    <form onSubmit={handleSubmit} className="border-t border-slate-200 p-3">
      <label htmlFor="chat-message" className="sr-only">
        Ask a question about Pavan
      </label>

      <div className="flex items-end gap-2 rounded-2xl border border-slate-200 bg-white p-2 shadow-sm focus-within:border-slate-400">
        <textarea
          id="chat-message"
          value={value}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about my experience or projects..."
          rows={1}
          maxLength={2000}
          disabled={isLoading}
          className="max-h-28 min-h-10 flex-1 resize-y bg-transparent px-2 py-2 text-sm text-slate-800 outline-none placeholder:text-slate-400 disabled:opacity-60"
        />

        <button
          type="submit"
          disabled={!value.trim() || isLoading}
          className="rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {isLoading ? "Sending…" : "Send"}
        </button>
      </div>

      <p className="mt-2 px-1 text-xs text-slate-400">
        AI-generated responses may be inaccurate. Avoid sharing sensitive information.
      </p>
    </form>
  );
}
