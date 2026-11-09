
"use client";

const SUGGESTED_PROMPTS = [
  "Tell me about your AI projects",
  "What is your experience with Agentic AI?",
  "What technologies power IncidentPilot?",
  "Tell me about your education",
];

interface SuggestedPromptsProps {
  onSelect: (prompt: string) => void;
  disabled?: boolean;
}

export default function SuggestedPrompts({
  onSelect,
  disabled = false,
}: SuggestedPromptsProps) {
  return (
    <section aria-label="Suggested questions" className="space-y-3">
      <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
        Suggested questions
      </p>

      <div className="flex flex-wrap gap-2">
        {SUGGESTED_PROMPTS.map((prompt) => (
          <button
            key={prompt}
            type="button"
            disabled={disabled}
            onClick={() => onSelect(prompt)}
            className="rounded-full border border-slate-200 bg-white px-3 py-2 text-left text-xs text-slate-700 transition hover:border-slate-400 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {prompt}
          </button>
        ))}
      </div>
    </section>
  );
}
