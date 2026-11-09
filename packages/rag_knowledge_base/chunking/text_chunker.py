
import re

from packages.rag_knowledge_base.config import ChunkingConfig
from packages.rag_knowledge_base.models.document import (
    DocumentMetadata,
    KnowledgeDocument,
)


class TextChunker:
    """Split Markdown documents while preserving heading context."""

    HEADING_PATTERN = re.compile(r"(?m)^#{1,6}\s+.+$")

    def __init__(self, config: ChunkingConfig | None = None) -> None:
        self.config = config or ChunkingConfig()


    def _merge_short_sections(self, sections: list[str]) -> list[str]:
        """Merge short sections with adjacent sections when they fit."""

        merged: list[str] = []
        size = self.config.chunk_size

        for section in sections:
            if not merged:
                merged.append(section)
                continue

            previous = merged[-1]
            combined = f"{previous}\n\n{section}"

            # Merge a heading-only previous section with the next section,
            # or merge adjacent short sections when they fit.
            previous_is_heading_only = (
                previous.startswith("#") and "\n" not in previous
            )

            if len(combined) <= size and (
                previous_is_heading_only
                or len(previous) < size // 2
                or len(section) < size // 2
            ):
                merged[-1] = combined
            else:
                merged.append(section)

        return merged


    def chunk_document(
        self,
        document: KnowledgeDocument,
    ) -> list[KnowledgeDocument]:
        text = document.content.strip()
        if not text:
            return []

        sections = self._merge_short_sections(self._split_sections(text))
        pieces: list[str] = []

        for section in sections:
            pieces.extend(self._split_oversized_section(section))

        total = len(pieces)
        return [
            KnowledgeDocument(
                id=f"{document.id}-chunk-{index}",
                content=piece,
                metadata=DocumentMetadata(
                    source=document.metadata.source,
                    category=document.metadata.category,
                    title=document.metadata.title,
                    chunk_index=index,
                    total_chunks=total,
                ),
            )
            for index, piece in enumerate(pieces)
        ]

    def _split_sections(self, text: str) -> list[str]:
        """Split before Markdown headings, retaining each heading."""
        matches = list(self.HEADING_PATTERN.finditer(text))
        if not matches:
            return [text]

        sections: list[str] = []

        # Preserve any introduction before the first heading.
        if text[:matches[0].start()].strip():
            sections.append(text[:matches[0].start()].strip())

        for index, match in enumerate(matches):
            end = (
                matches[index + 1].start()
                if index + 1 < len(matches)
                else len(text)
            )
            section = text[match.start():end].strip()
            if section:
                sections.append(section)

        return sections

    def _split_oversized_section(self, section: str) -> list[str]:
        """Split long sections, repeating the section heading as context."""
        size = self.config.chunk_size
        overlap = self.config.chunk_overlap

        if len(section) <= size:
            return [section]

        lines = section.splitlines()
        heading = lines[0] if lines and lines[0].startswith("#") else ""
        body = "\n".join(lines[1:]).strip() if heading else section

        if heading and len(heading) < size:
            prefix = heading + "\n"
            body_limit = size - len(prefix)
        else:
            prefix = ""
            body_limit = size

        if body_limit <= 0:
            prefix = ""
            body_limit = size

        chunks: list[str] = []
        start = 0

        while start < len(body):
            end = min(start + body_limit, len(body))

            if end < len(body):
                # Prefer paragraph, then line, then word boundaries.
                candidates = [
                    body.rfind("\n\n", start, end),
                    body.rfind("\n", start, end),
                    body.rfind(" ", start, end),
                ]
                boundary = next(
                    (position for position in candidates if position > start),
                    -1,
                )
                if boundary > start:
                    end = boundary

            if end <= start:
                end = min(start + body_limit, len(body))
                while end < len(body) and not body[end - 1].isspace():
                    end += 1

            content = body[start:end].strip()
            if content:
                chunks.append((prefix + content).strip())

            if end >= len(body):
                break

            next_start = max(start + 1, end - overlap)

            # Align the next chunk with a word boundary.
            while next_start < len(body) and next_start > 0:
                if body[next_start - 1].isspace():
                    break
                next_start += 1

            while next_start < len(body) and body[next_start].isspace():
                next_start += 1

            start = next_start

        return chunks
