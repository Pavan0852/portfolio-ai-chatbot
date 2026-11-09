"use client";

interface PortfolioHeroProps {
  onOpenChat: () => void;
}

export default function PortfolioHero({
  onOpenChat,
}: PortfolioHeroProps) {
  return (
    <section className="mx-auto flex min-h-[75vh] max-w-6xl flex-col justify-center px-6 py-20">
      <p className="mb-4 text-sm font-semibold uppercase tracking-[0.2em] text-indigo-600">
        Portfolio AI Assistant
      </p>

      <h1 className="max-w-3xl text-5xl font-bold tracking-tight text-slate-950 sm:text-7xl">
        Explore my work, experience, and projects.
      </h1>

      <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
        Ask questions about my technical experience, AI projects, skills,
        and professional journey.
      </p>

      <div className="mt-10 flex flex-wrap gap-4">
        <button
          type="button"
          onClick={onOpenChat}
          className="rounded-full bg-slate-950 px-7 py-3.5 text-sm font-semibold text-white transition hover:bg-slate-800 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-slate-300"
        >
          Ask my AI assistant
        </button>

        <a
          href="#about"
          className="rounded-full border border-slate-300 px-7 py-3.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
        >
          Explore portfolio
        </a>
      </div>

      <div className="mt-16 grid gap-4 sm:grid-cols-3">
        {[
          {
            title: "Agentic AI",
            description: "Multi-agent workflows and orchestration",
          },
          {
            title: "Generative AI",
            description: "LLM applications and RAG systems",
          },
          {
            title: "AI Engineering",
            description: "Building practical AI-powered products",
          },
        ].map((item) => (
          <div
            key={item.title}
            className="rounded-2xl border border-slate-200 bg-white/70 p-6 shadow-sm"
          >
            <h2 className="font-semibold text-slate-900">{item.title}</h2>
            <p className="mt-2 text-sm text-slate-600">
              {item.description}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}