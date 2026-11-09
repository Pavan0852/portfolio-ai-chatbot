
from packages.rag_knowledge_base.models.document import KnowledgeDocument


class ContextBuilder:
    """Format retrieved knowledge chunks into grounded LLM context."""

    def build(
        self,
        documents: list[KnowledgeDocument],
        max_chars: int = 12_000,
    ) -> str:
        """Build a bounded context string from retrieved documents."""

        if max_chars < 1:
            raise ValueError("max_chars must be at least 1")

        sections: list[str] = []
        current_length = 0

        for document in documents:
            source = document.metadata.source
            title = document.metadata.title
            content = document.content.strip()

            section = (
                f"Source: {source}\n"
                f"Title: {title}\n"
                f"Content:\n{content}"
            )

            separator_length = 2 if sections else 0
            remaining = max_chars - current_length - separator_length

            if remaining <= 0:
                break

            if len(section) > remaining:
                # Avoid returning a partial final section with broken metadata.
                break

            sections.append(section)
            current_length += separator_length + len(section)

        return "\n\n".join(sections)
