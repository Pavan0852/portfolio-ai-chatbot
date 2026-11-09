
from pathlib import Path

from packages.rag_knowledge_base.chunking.text_chunker import TextChunker
from packages.rag_knowledge_base.ingestion.loaders import MarkdownLoader
from packages.rag_knowledge_base.models.document import KnowledgeDocument


class KnowledgeIngestionPipeline:
    """Load Markdown knowledge and split it into retrieval-ready chunks."""

    def __init__(
        self,
        loader: MarkdownLoader | None = None,
        chunker: TextChunker | None = None,
    ) -> None:
        self.loader = loader or MarkdownLoader()
        self.chunker = chunker or TextChunker()

    def ingest(self, knowledge_root: Path) -> list[KnowledgeDocument]:
        """Load all supported files and return their chunks."""

        documents = self.loader.load_directory(knowledge_root)

        chunks: list[KnowledgeDocument] = []
        for document in documents:
            chunks.extend(self.chunker.chunk_document(document))

        return chunks
