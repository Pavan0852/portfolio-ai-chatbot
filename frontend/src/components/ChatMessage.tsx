
"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { ChatMessage as ChatMessageType } from "@/types/chat";

interface ChatMessageProps {
  message: ChatMessageType;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <article
      className={`flex w-full ${
        isUser ? "justify-end" : "justify-start"
      }`}
      aria-label={isUser ? "Your message" : "Assistant response"}
    >
      <div
        className={`max-w-[88%] min-w-0 rounded-2xl px-4 py-3 text-sm leading-6 ${
          isUser
            ? "rounded-br-md bg-slate-900 text-white"
            : "rounded-bl-md border border-slate-200 bg-white text-slate-800 shadow-sm"
        }`}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap break-words">
            {message.content}
          </p>
        ) : (
          <div className="min-w-0 break-words">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                h1: ({ children }) => (
                  <h1 className="mb-3 mt-4 text-xl font-bold text-slate-900 first:mt-0">
                    {children}
                  </h1>
                ),
                h2: ({ children }) => (
                  <h2 className="mb-2 mt-4 text-lg font-semibold text-slate-900 first:mt-0">
                    {children}
                  </h2>
                ),
                h3: ({ children }) => (
                  <h3 className="mb-2 mt-3 text-base font-semibold text-slate-900 first:mt-0">
                    {children}
                  </h3>
                ),
                p: ({ children }) => (
                  <p className="mb-3 leading-6 last:mb-0">{children}</p>
                ),
                strong: ({ children }) => (
                  <strong className="font-semibold text-slate-950">
                    {children}
                  </strong>
                ),
                ul: ({ children }) => (
                  <ul className="mb-3 ml-5 list-disc space-y-1 last:mb-0">
                    {children}
                  </ul>
                ),
                ol: ({ children }) => (
                  <ol className="mb-3 ml-5 list-decimal space-y-1 last:mb-0">
                    {children}
                  </ol>
                ),
                li: ({ children }) => <li className="pl-1">{children}</li>,
                blockquote: ({ children }) => (
                  <blockquote className="my-3 border-l-4 border-slate-300 pl-3 text-slate-600">
                    {children}
                  </blockquote>
                ),
                a: ({ href, children }) => (
                  <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 underline underline-offset-2 hover:text-blue-800"
                  >
                    {children}
                  </a>
                ),
                code: ({ children }) => (
                  <code className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-xs text-slate-800">
                    {children}
                  </code>
                ),
                pre: ({ children }) => (
                  <pre className="my-3 overflow-x-auto rounded-xl bg-slate-950 p-3 text-xs leading-5 text-slate-100">
                    {children}
                  </pre>
                ),
                table: ({ children }) => (
                  <div className="my-3 overflow-x-auto">
                    <table className="w-full border-collapse text-left text-xs">
                      {children}
                    </table>
                  </div>
                ),
                th: ({ children }) => (
                  <th className="border border-slate-200 bg-slate-100 px-3 py-2 font-semibold">
                    {children}
                  </th>
                ),
                td: ({ children }) => (
                  <td className="border border-slate-200 px-3 py-2">
                    {children}
                  </td>
                ),
                hr: () => <hr className="my-4 border-slate-200" />,
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </article>
  );
}
