
from pathlib import Path


from packages.rag_knowledge_base.models.document import (
    DocumentMetadata,
    KnowledgeDocument,
)


SUPPORTED_EXTENSIONS = {".md", ".markdown"}


class MarkdownLoader:
    """Load Markdown files into validated knowledge documents."""

    def load_file(self, path: Path, knowledge_root: Path) -> KnowledgeDocument:
        path = path.resolve()
        knowledge_root = knowledge_root.resolve()

        # Reject files outside the designated knowledge directory.
        if not path.is_relative_to(knowledge_root):
            raise ValueError("Knowledge files must be inside the knowledge directory")

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {path.suffix}")

        if not path.is_file():
            raise FileNotFoundError(f"Knowledge file not found: {path}")

        content = path.read_text(encoding="utf-8").strip()
        if not content:
            raise ValueError(f"Knowledge file is empty: {path.name}")

        relative_path = path.relative_to(knowledge_root).as_posix()
        category = relative_path.split("/", maxsplit=1)[0]
        if category == relative_path:
            category = path.stem

        return KnowledgeDocument(
            id=relative_path,
            content=content,
            metadata=DocumentMetadata(
                source=relative_path,
                category=category,
                title=path.stem.replace("-", " ").replace("_", " ").title(),
            ),
        )

    def load_directory(self, knowledge_root: Path) -> list[KnowledgeDocument]:
        knowledge_root = knowledge_root.resolve()
        if not knowledge_root.is_dir():
            raise NotADirectoryError(
                f"Knowledge directory not found: {knowledge_root}"
            )

        documents: list[KnowledgeDocument] = []
        for path in sorted(knowledge_root.rglob("*")):
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
                documents.append(self.load_file(path, knowledge_root))

        return documents
